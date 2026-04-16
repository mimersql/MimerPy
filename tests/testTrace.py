# Copyright (c) 2017 Mimer Information Technology

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# See license for more details.

import io
import logging
import os
import tempfile
import unittest

import mimerpy
from mimerpy.cursorPy import _strip_sql_literals
import db_config


class TestStripSqlLiterals(unittest.TestCase):
    """Unit tests for _strip_sql_literals — no database required."""

    def test_string_literal_replaced_with_hashes(self):
        result = _strip_sql_literals("WHERE name = 'Alice'")
        self.assertEqual(result, "WHERE name = '#####'")

    def test_string_literal_length_preserved(self):
        result = _strip_sql_literals("WHERE city = 'New York'")
        self.assertEqual(result, "WHERE city = '########'")

    def test_numeric_literal_replaced(self):
        result = _strip_sql_literals("WHERE age > 30")
        self.assertEqual(result, "WHERE age > #")

    def test_float_literal_replaced(self):
        result = _strip_sql_literals("WHERE price < 3.14")
        self.assertEqual(result, "WHERE price < #")

    def test_multiple_literals(self):
        result = _strip_sql_literals("WHERE name = 'Bob' AND age = 25")
        self.assertEqual(result, "WHERE name = '###' AND age = #")

    def test_question_mark_params_untouched(self):
        result = _strip_sql_literals("INSERT INTO t VALUES (?, ?, ?)")
        self.assertEqual(result, "INSERT INTO t VALUES (?, ?, ?)")

    def test_named_params_untouched(self):
        result = _strip_sql_literals("INSERT INTO t VALUES (:a, :b)")
        self.assertEqual(result, "INSERT INTO t VALUES (:a, :b)")

    def test_escaped_quote_inside_string(self):
        # 'it''s' unescapes to "it's" = 4 chars
        result = _strip_sql_literals("WHERE s = 'it''s'")
        self.assertEqual(result, "WHERE s = '####'")

    def test_empty_string_literal(self):
        result = _strip_sql_literals("WHERE s = ''")
        self.assertEqual(result, "WHERE s = ''")

    def test_no_literals(self):
        sql = "SELECT * FROM mytable"
        self.assertEqual(_strip_sql_literals(sql), sql)


def _capture_logger(name):
    """Return a (logger, list) pair; logged messages are appended to the list."""
    records = []

    class _ListHandler(logging.Handler):
        def emit(self, record):
            records.append(self.format(record))

    handler = _ListHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.Logger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)
    return logger, records


class TestTraceLogging(unittest.TestCase):
    """Integration tests: verify that SQL operations produce correct log entries."""

    @classmethod
    def setUpClass(cls):
        (cls.syscon, cls.tstcon) = db_config.setup()
        with cls.tstcon.cursor() as c:
            c.execute("CREATE TABLE trace_t (c1 INTEGER, c2 NVARCHAR(64)) IN pybank")
        cls.tstcon.commit()

    @classmethod
    def tearDownClass(cls):
        with cls.tstcon.cursor() as c:
            c.execute("DROP TABLE trace_t")
        cls.tstcon.commit()
        db_config.teardown(tstcon=cls.tstcon, syscon=cls.syscon)

    def _con_with_logger(self, unsafe=False):
        """Return a connection whose _logger is wired to an in-memory list."""
        con = mimerpy.connect(**db_config.TSTUSR)
        logger, records = _capture_logger(f'test_trace_{id(self)}')
        con._logger = logger
        con._log_unsafe = unsafe
        return con, records

    # ------------------------------------------------------------------
    # Safe mode (default)
    # ------------------------------------------------------------------

    def test_execute_logged(self):
        con, log = self._con_with_logger()
        con.execute("SELECT * FROM trace_t")
        con.close()
        self.assertTrue(any("execute:" in m for m in log))

    def test_execute_literals_stripped(self):
        con, log = self._con_with_logger()
        con.execute("SELECT * FROM trace_t WHERE c2 = 'secret'")
        con.close()
        entry = next(m for m in log if "execute:" in m)
        self.assertNotIn("secret", entry)
        self.assertIn("'######'", entry)

    def test_execute_numeric_literal_stripped(self):
        con, log = self._con_with_logger()
        con.execute("SELECT * FROM trace_t WHERE c1 = 42")
        con.close()
        entry = next(m for m in log if "execute:" in m)
        self.assertNotIn("42", entry)
        self.assertIn("#", entry)

    def test_execute_params_not_logged_in_safe_mode(self):
        con, log = self._con_with_logger()
        with con.cursor() as cur:
            cur.execute("INSERT INTO trace_t VALUES (?, ?)", (99, 'hidden'))
        con.rollback()
        con.close()
        entry = next(m for m in log if "execute:" in m)
        self.assertNotIn("hidden", entry)
        self.assertNotIn("99", entry)

    def test_executemany_logged(self):
        con, log = self._con_with_logger()
        with con.cursor() as cur:
            cur.executemany("INSERT INTO trace_t VALUES (?, ?)",
                            [(1, 'a'), (2, 'b'), (3, 'c')])
        con.rollback()
        con.close()
        entry = next(m for m in log if "executemany:" in m)
        self.assertIn("3 rows", entry)

    def test_commit_logged(self):
        con, log = self._con_with_logger()
        con.execute("SELECT * FROM trace_t")
        con.commit()
        con.close()
        self.assertTrue(any(m.endswith("commit") for m in log))

    def test_rollback_logged(self):
        con, log = self._con_with_logger()
        con.execute("SELECT * FROM trace_t")
        con.rollback()
        con.close()
        self.assertTrue(any(m.endswith("rollback") for m in log))

    # ------------------------------------------------------------------
    # Unsafe mode
    # ------------------------------------------------------------------

    def test_unsafe_literals_not_stripped(self):
        con, log = self._con_with_logger(unsafe=True)
        con.execute("SELECT * FROM trace_t WHERE c2 = 'secret'")
        con.close()
        entry = next(m for m in log if "execute:" in m)
        self.assertIn("secret", entry)

    def test_unsafe_params_logged(self):
        con, log = self._con_with_logger(unsafe=True)
        with con.cursor() as cur:
            cur.execute("INSERT INTO trace_t VALUES (?, ?)", (99, 'visible'))
        con.rollback()
        con.close()
        entry = next(m for m in log if "execute:" in m)
        self.assertIn("visible", entry)

    # ------------------------------------------------------------------
    # File trace
    # ------------------------------------------------------------------

    def test_trace_to_file(self):
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            logfile = f.name
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=logfile)
            con.execute("SELECT * FROM trace_t")
            con.commit()
            con.close()
            with open(logfile, encoding='utf-8') as f:
                content = f.read()
            self.assertIn("execute:", content)
            self.assertIn("commit", content)
        finally:
            os.unlink(logfile)

    def test_trace_file_appended(self):
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False,
                                         mode='w', encoding='utf-8') as f:
            f.write("existing line\n")
            logfile = f.name
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=logfile)
            con.execute("SELECT * FROM trace_t")
            con.close()
            with open(logfile, encoding='utf-8') as f:
                content = f.read()
            self.assertTrue(content.startswith("existing line\n"))
            self.assertIn("execute:", content)
        finally:
            os.unlink(logfile)

    def test_no_trace_by_default(self):
        saved = os.environ.pop('MIMERPY_TRACE', None)
        try:
            con = mimerpy.connect(**db_config.TSTUSR)
            self.assertIsNone(con._logger)
            con.close()
        finally:
            if saved is not None:
                os.environ['MIMERPY_TRACE'] = saved

    def test_trace_false_overrides_env(self):
        os.environ['MIMERPY_TRACE'] = '1'
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=False)
            self.assertIsNone(con._logger)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE']

    def test_trace_none_picks_up_env(self):
        os.environ['MIMERPY_TRACE'] = '1'
        try:
            con = mimerpy.connect(**db_config.TSTUSR)
            self.assertIsNotNone(con._logger)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE']

    def test_trace_unsafe_false_overrides_env(self):
        os.environ['MIMERPY_TRACE_UNSAFE'] = '1'
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=True, trace_unsafe=False)
            self.assertFalse(con._log_unsafe)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE_UNSAFE']

    def test_trace_unsafe_none_picks_up_env(self):
        os.environ['MIMERPY_TRACE_UNSAFE'] = '1'
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=True)
            self.assertTrue(con._log_unsafe)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE_UNSAFE']

    # -- explicit False always wins, regardless of env var value ----------

    def test_trace_false_overrides_env_filename(self):
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            logfile = f.name
        os.environ['MIMERPY_TRACE'] = logfile
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=False)
            self.assertIsNone(con._logger)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE']
            os.unlink(logfile)

    def test_trace_false_overrides_env_true(self):
        for val in ('true', 'yes'):
            os.environ['MIMERPY_TRACE'] = val
            try:
                con = mimerpy.connect(**db_config.TSTUSR, trace=False)
                self.assertIsNone(con._logger, f"trace=False should block MIMERPY_TRACE={val}")
                con.close()
            finally:
                del os.environ['MIMERPY_TRACE']

    def test_trace_unsafe_false_overrides_env_true(self):
        for val in ('true', 'yes'):
            os.environ['MIMERPY_TRACE_UNSAFE'] = val
            try:
                con = mimerpy.connect(**db_config.TSTUSR, trace=True, trace_unsafe=False)
                self.assertFalse(con._log_unsafe,
                                 f"trace_unsafe=False should block MIMERPY_TRACE_UNSAFE={val}")
                con.close()
            finally:
                del os.environ['MIMERPY_TRACE_UNSAFE']

    # -- explicit True works without env var ------------------------------

    def test_trace_true_without_env(self):
        os.environ.pop('MIMERPY_TRACE', None)
        con = mimerpy.connect(**db_config.TSTUSR, trace=True)
        self.assertIsNotNone(con._logger)
        con.close()

    def test_trace_unsafe_true_without_env(self):
        os.environ.pop('MIMERPY_TRACE_UNSAFE', None)
        con = mimerpy.connect(**db_config.TSTUSR, trace=True, trace_unsafe=True)
        self.assertTrue(con._log_unsafe)
        con.close()

    # -- env var picked up for all accepted truthy values -----------------

    def test_trace_env_yes(self):
        os.environ['MIMERPY_TRACE'] = 'yes'
        try:
            con = mimerpy.connect(**db_config.TSTUSR)
            self.assertIsNotNone(con._logger)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE']

    def test_trace_unsafe_env_yes(self):
        os.environ['MIMERPY_TRACE_UNSAFE'] = 'yes'
        try:
            con = mimerpy.connect(**db_config.TSTUSR, trace=True)
            self.assertTrue(con._log_unsafe)
            con.close()
        finally:
            del os.environ['MIMERPY_TRACE_UNSAFE']


if __name__ == '__main__':
    unittest.main()
