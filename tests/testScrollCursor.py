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

import unittest
import time
import math
import mimerpy

from mimerpy.mimPyExceptions import *
import db_config

class TestScrollCursorMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.syscon, self.tstcon) = db_config.setup()

    @classmethod
    def tearDownClass(self):
        db_config.teardown(tstcon=self.tstcon, syscon=self.syscon)

    def tearDown(self):
        self.tstcon.rollback()

########################################################################
## Tests below
########################################################################

    def test_createTable(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob(c1 INTEGER, c2 NVARCHAR(10)) in pybank")

    def test_createTable_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobcr1(c1 INTEGER, c2 NVARCHAR(10))")
            c.execute("create table bobcr2(c1 INTEGER, c2 NVARCHAR(10))")
            c.execute("create table bobcr3(c1 INTEGER, c2 NVARCHAR(10))")
            c.execute("create table bobcr4(c1 INTEGER, c2 NVARCHAR(10))")

    def test_createTable_DropTable(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob2(c1 INTEGER, c2 NVARCHAR(10))")
            c.execute("drop table bob2 CASCADE")

    def test_create_invalid_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon (c1 INTEGER, c2 INTEGER) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("banana INTO jon VALUES (3, 14)")

    def test_create_rollback_table(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonnynothere (c1 INTEGER, c2 INTEGER)")
            self.tstcon.rollback()
            c.execute("select * from jonnynothere")

    def test_two_select(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonny (c1 INTEGER, c2 INTEGER) in pybank")
            c.execute("select c1 from jonny where c1 = (?)",(2))
            c.execute("select * from jonny")

    def test_many_select(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob356 (c1 INTEGER) in pybank")
            for val in range(100):
                c.execute("insert into bob356 values (:a)", (val))
            for gal in range(100):
                c.execute("select c1 from bob356 where c1 > (?)",(gal))
                temp = c.fetchall()
                self.assertEqual(len(temp), 99 - gal)

    def test_select_no_commit(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobc (c1 INTEGER, c2 FLOAT) in pybank")
            for val in range(100):
                c.execute("insert into bobc values (:a, :b)", (val, val + 0.5))
            c.execute("select * from bobc where c1 = 99")
            self.assertEqual(c.fetchall(),[(99,99.5)])

    def test_select_description(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table description (columnone INTEGER) in pybank")
            for val in range(10):
                c.execute("insert into description values (?)", val)
            c.execute("select * from description")
            self.assertEqual(c.description,
                             (('columnone', 50, None, None, None, None, None),))

    def test_select_description2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table description2 (c1 INTEGER, c2 FLOAT)")
            for val in range(10):
                c.execute("insert into description2 values (?,?)", (val, val/3))
            c.execute("select * from description2")
            self.assertEqual(c.description,
                             (('c1', 50, None, None, None, None, None),
                              ('c2', 56, None, None, None, None, None)))
            c.execute("select c1 from description2")
            self.assertEqual(c.description,
                             (('c1', 50, None, None, None, None, None),))
            c.execute("select c2 from description2")
            self.assertEqual(c.description,
                             (('c2', 56, None, None, None, None, None),))
            c.execute("select * from description2")
            self.assertEqual(c.description,
                             (('c1', 50, None, None, None, None, None),
                              ('c2', 56, None, None, None, None, None)))

    def test_select_description3(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table description3 (price INTEGER,"
                      "                           currentval FLOAT,"
                      "                           currency NVARCHAR(128),"
                      "                           rate BIGINT,"
                      "                           currentyear INTEGER)")
            for val in range(10):
                c.execute("insert into description3 values (?,?,?,?,?)",
                          (val, val/3, 'SEK', 2**61, val+2000))
            c.execute("select * from description3")
            self.assertEqual(c.description,
                             (('price', 50, None, None, None, None, None),
                              ('currentval', 56, None, None, None, None, None),
                              ('currency', 63, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None),
                              ('currentyear', 50, None, None, None, None, None)))
            c.execute("select price, currentyear, currency, rate"
                      "  from description3")
            self.assertEqual(c.description,
                             (('price', 50, None, None, None, None, None),
                              ('currentyear', 50, None, None, None, None, None),
                              ('currency', 63, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None)))
            c.execute("select rate, rate, rate, rate from description3")
            self.assertEqual(c.description,
                             (('rate', 52, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None)))
            c.execute("select * from description3")
            self.assertEqual(c.description,
                             (('price', 50, None, None, None, None, None),
                              ('currentval', 56, None, None, None, None, None),
                              ('currency', 63, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None),
                              ('currentyear', 50, None, None, None, None, None)))

    def test_select_description4(self):
        with self.tstcon.cursor(scrollable = True) as c:
            name1 = "e"*127+"q"
            name2 = "m"*127+"q"
            query = ("create table description4 (" + name1 + " INTEGER, "
                     + name2 + " BOOLEAN) in pybank")
            c.execute(query)
            for val in range(10):
                c.execute("insert into description4 values (?,?)", (val,val%2))
            c.execute("select * from description4")
            self.assertEqual(c.description,
                             ((name1, 50, None, None, None, None, None),
                              (name2, 42, None, None, None, None, None)))

    def test_select_description5(self):
        with self.tstcon.cursor(scrollable = True) as c:
            name1 = "e"*127+"q"
            name2 = "m"*127+"q"
            query = ("create table description5 (" + name1 + " INTEGER, "
                     + name2 + " BOOLEAN) in pybank")
            c.execute(query)
            for val in range(10):
                c.execute("insert into description5 values (?,?)", (val,val%2))
            c.execute("select * from description5")
            self.assertEqual(c.description,
                             ((name1, 50, None, None, None, None, None),
                              (name2, 42, None, None, None, None, None)))

    def test_invalid_create(self):
        b = self.tstcon.cursor(scrollable = True)
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("creat table jon(i integer)")

    def test_insert_parametermarkers(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob1 (c1 INTEGER,  c2 NVARCHAR(10))")
            c.execute("insert into bob1 values (:a, :b)", (3, 'bob'))

    def test_insert_parametermarkers_long_string(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobstring (c1 INTEGER,  c2 NVARCHAR(256))")
            string = "mimer" * 40
            c.execute("insert into bobstring values (:a, :b)", (3, string))
            self.tstcon.commit()
            c.execute("select c2 from bobstring")
            r = c.fetchall()
            self.assertEqual(r, [(string,)])

    def test_insert_parametermarkers_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob13 (c1 INTEGER, c2 NVARCHAR(10),"
                      "                    c3 FLOAT) in pybank")
            self.tstcon.commit()
            c.executemany("insert into bob13 values (:a, :b, :c)",
                          ((1,'pi',14.345),
                           (2,'pii',14.345),
                           (-3,'piii',14.345),
                           (7,'piii',14.345),
                           (1121231,'piiii',14.345)))
            self.tstcon.commit()
            c.execute("select * from bob13")
            r = c.fetchall()
            self.assertEqual(r, [(1, 'pi', 14.345),
                                 (2, 'pii', 14.345),
                                 (-3, 'piii', 14.345),
                                 (7, 'piii', 14.345),
                                 (1121231, 'piiii', 14.345)])

    def test_insert_parametermarkers_russian(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob14 (c1 INTEGER, c2 NVARCHAR(128),"
                      "                    c3 FLOAT) in pybank")
            self.tstcon.commit()
            c.executemany("insert into bob14 values (:a, :b, :c)",
                          ((1,'продиктованной ангелом',14.345),
                           (2,'安排他們參',14.345)))
            self.tstcon.commit()
            c.execute("select * from bob14")
            self.assertEqual(c.fetchall(),
                             [(1,'продиктованной ангелом',14.345),
                              (2,'安排他們參',14.345)])

    def test_insert_parametermarkers_unicode(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table boby14 (c1 INTEGER, c2 NVARCHAR(128),"
                      "                     c3 FLOAT) in pybank")
            self.tstcon.commit()
            c.executemany("insert into boby14 values (:a, :b, :c)",
                          ((1,'продиктованной ангелом',14.345),
                           (2,'安排他們參‱',14.345)))
            self.tstcon.commit()
            c.execute("select * from boby14")
            self.assertEqual(c.fetchall(),
                             [(1,'продиктованной ангелом',14.345),
                              (2,'安排他們參‱',14.345)])

    def test_insert_parametermarkers_too_long(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob15 (c1 NVARCHAR(10)) in pybank")
            self.tstcon.commit()
            with self.assertRaises(DatabaseError):
                c.execute("insert into bob15 values (:a)",
                          ('This sentence is too long'))
        self.tstcon.commit()

    def test_insert_too_few_parametermarkers(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob3 (c1 INTEGER, c2 NVARCHAR(10))")
            with self.assertRaises(DatabaseError):
                c.execute("insert into bob3 values (:a, :b)", (3))

    # &&&& Wrong exception. Fixme.
    @unittest.skip
    def test_insert_too_many_parametermarkers(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob33 (c1 INTEGER, c2 NVARCHAR(10))")
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob33 values (:a, :b)",
                              ((3,'pi',14), (3,)))

    def test_insert_many_times(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob34(c1 INTEGER, c2 NVARCHAR(10),"
                      "                   c3 FLOAT) in pybank")
            for i in range(0, 101):
                c.execute("insert into bob34 values (5,'ウィキペディ', 4.4543543)")
        self.tstcon.commit()

    def test_executemany_one_value(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob4 (c1 INTEGER) in pybank")
            c.executemany("insert into bob4 values (:a)", [(1,)])
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob4 values (:a)", [(1)])
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob4 values (:a)", (1))
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob4 values (:a)", [1])

    def test_executemany_one_tuple(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob5 (c1 INTEGER, c2 NVARCHAR(10))")
            c.executemany("insert into bob5 values (:a, :b)", ((1,'bob1'),))

    def test_executemany_several_tuples(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobe6 (c1 INTEGER, c2 NVARCHAR(10))")
            c.executemany("insert into bobe6 values (:a, :b)",
                          [(1,'bob1'),
                           (2, 'bob2'),
                           (3,'bob3')])

    def test_commit(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob7 (c1 INTEGER, c2 NVARCHAR(10))")
            c.executemany("insert into bob7 values (:a, :b)",
                          ((1,'bob1'),
                           (2, 'bob2'),
                           (3,'bob3')))
        self.tstcon.commit()

    def test_fetchone(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob8 (c1 INTEGER, c2 NVARCHAR(10))")

        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("insert into bob8 values (:a, :b)", (8, 'bob'))
            self.tstcon.commit()
            c.execute("select * from bob8")
            self.assertEqual(c.fetchone(), (8, 'bob'))

    def test_fetchmany(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob9 (c1 INTEGER, c2 NVARCHAR(10))")

        with self.tstcon.cursor(scrollable = True) as c:
            c.executemany("insert into bob9 values (:a, :b)",
                          ((9, 'bob9'),
                           (10, 'bob10'),
                           (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob9")
            self.assertEqual(c.fetchmany(3),
                             [(9, 'bob9'), (10, 'bob10'), (11, 'bob11')])

    def test_fetchmany_too_many(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob11 (c1 INTEGER, c2 NVARCHAR(10))")
            self.tstcon.commit()
            c.executemany("insert into bob11 values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'), (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob11")
            self.assertEqual(c.fetchmany(5),
                             [(9, 'bob9'), (10, 'bob10'), (11, 'bob11')])

    def test_fetchmany_notall(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob12 (c1 INTEGER, c2 NVARCHAR(10))")
            self.tstcon.commit()
            c.executemany("insert into bob12 values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'), (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob12")
            self.assertEqual(c.fetchmany(2), [(9, 'bob9'), (10, 'bob10')])
            self.assertEqual(c.fetchmany(2), [(11, 'bob11')])

    def test_fetchall(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob10 (c1 INTEGER, c2 NVARCHAR(10))")
            c.executemany("insert into bob10 values (:a, :b)",
                          ((10, 'bob10'), (11, 'bob11'), (12, 'bob12'),))
            self.tstcon.commit()
            c.execute("select * from bob10")
            self.assertEqual(c.fetchall(),
                             [(10, 'bob10'),(11, 'bob11'), (12, 'bob12')])

    def test_fetchall_correct_number_of_rows(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob101(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
            self.tstcon.commit()
            for d in range(1, 101):
                c.execute("insert into bob101 values (5,'ウィキペディ', 4.4543543)")
            self.tstcon.commit()
            c.execute("select * from bob101")
            r = c.fetchall()
            self.assertEqual(len(r), 100)

    def test_fetchall_correct_number_of_rows2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob102(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
            self.tstcon.commit()
            for i in range(1, 101):
                c.execute("insert into bob102 values (5,'ウィキペディ',"
                          " 4.4543543)")
            self.tstcon.rollback()
            c.execute("select * from bob102")
            r = c.fetchall()
            self.assertEqual(len(r), 0)

    @unittest.skip
    def test_fetchall_correct_number_of_rows3(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob109(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
            for i in range(1, 101):
                c.execute("insert into bob109 values (5,'ウィキペディ',"
                          " 4.4543543)")
            self.tstcon.rollback()
            c.execute("select * from bob109")
            r = c.fetchall()
            self.assertEqual(len(r), 0)

    def test_use_next(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobnext(c1 INTEGER) in pybank")
            for i in range(0, 10):
                c.execute("insert into bobnext values (?)", i)
            self.tstcon.commit()
            c.execute("select * from bobnext")
            for i in range(0,10):
                (val,) = c.next()
                self.assertEqual(val, i)

    def test_use_next_StopIteration(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobstop(c1 INTEGER) in pybank")
            for i in range(0, 10):
                c.execute("insert into bobstop values (?)", i)
            self.tstcon.commit()
            c.execute("select * from bobstop")
            for i in range(0,10):
                c.next()
            with self.assertRaises(StopIteration):
                c.next()

    def test_insert_wrong_type_parametermarkers(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob1337 (c1 INTEGER, c2 INTEGER)")
            with self.assertRaises(DataError):
                c.execute("insert into bob1337  values (:a, :b)", (3, 3.14))

    def test_operate_after_closed(self):
        b = self.tstcon.cursor(scrollable = True)
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("select * from jon")

    def test_operate_after_closed_2(self):
        b = self.tstcon.cursor(scrollable = True)
        b.close()
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("Kalle")
        with self.assertRaises(ProgrammingError):
            b.executemany("Kalle", ("Kula"))
        with self.assertRaises(ProgrammingError):
            b.fetchone()
        with self.assertRaises(ProgrammingError):
            b.fetchmany("Kalle")
        with self.assertRaises(ProgrammingError):
            b.fetchall()
        with self.assertRaises(ProgrammingError):
            b.next()

    def test_invalid_select(self):
        with self.tstcon.cursor(scrollable = True) as c:
            with self.assertRaises(ProgrammingError):
                c.execute("select * from jonisnotatablejo where c1 = ?", (5))

    def test_same_table_twice(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob2437(c1 INTEGER) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob2437(c1 INTEGER) in pybank")

    def test_invalid_sequence_select(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob6565(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("select * from bob6565")
            r = c.fetchone()
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob6569(c1 INTEGER) in pybank")
            self.tstcon.rollback()

    #borde bli fel men blir rätt....
    def test_invalid_sequence_select_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob555(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("select * from bob555")
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob556(c1 INTEGER) in pybank")
            self.tstcon.rollback()
            c.execute("create table bob556(c1 INTEGER) in pybank")
            c.execute("insert into bob556 values (3)")
            c.execute("select * from bob556")
            self.assertEqual(c.fetchone(), (3,))

    def test_invalid_sequence_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob6567(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("insert into bob6567 values (3)")
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob6566(c1 INTEGER) in pybank")
            self.tstcon.rollback()

    def test_invalid_sequence_insert_parametermarkers(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob6568(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("insert into bob6568 values (?)", (3))
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob6566(c1 INTEGER) in pybank")
            self.tstcon.rollback()

    def test_executemany_DDL(self):
        with self.assertRaises(ProgrammingError):
            c = self.tstcon.executemany("create table bob6(c1 INTEGER)", (3))
        with self.tstcon.cursor(scrollable = True) as c:
            with self.assertRaises(ProgrammingError):
                c.execute("select * from bob6")

    def test_insert_exceeded(self):
        c = self.tstcon.execute("create table bob16(c1 INTEGER) in pybank")
        big = pow(2,100)
        with self.assertRaises(DataError):
            c.execute("insert into bob16 values (?)", big)

    def test_insert_too_long(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob17(c1 NVARCHAR(10)) in pybank")
            self.tstcon.commit()
            with self.assertRaises(DataError):
                c.execute("insert into bob17 values ('ウィキペデBobWasABoy')")
            self.tstcon.commit()

    def test_valid_int32_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon32 (c1 INTEGER, c2 INTEGER) in pybank")
            nvar = -2**31
            var = 2**31 - 1
            c.execute("insert INTO jon32 VALUES (?, ?)", (nvar, var))

    def test_invalid_int32_insert_too_small(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon31 (c1 INTEGER) in pybank")
            nvar = -2**31 - 1
            with self.assertRaises(DataError):
                c.execute("insert INTO jon31 VALUES (?)", (nvar))

    def test_invalid_int32_insert_too_big(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon33 (c1 INTEGER) in pybank")
            var = 2**31
            with self.assertRaises(DataError):
                c.execute("insert INTO jon33 VALUES (?)", (var))

    def test_valid_int64_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon64 (c1 BIGINT, c2 BIGINT) in pybank")
            nvar = -2**63
            var = 2**63 - 1
            c.execute("insert INTO jon64 VALUES (?,?)", (nvar,var))

    def test_overflow_int64_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table intjon4 (c1 BIGINT, c2 BIGINT) in pybank")
            nvar = -2**633
            var = 2**63 - 1
            with self.assertRaises(DataError):
                c.executemany("insert INTO intjon4 VALUES (?,?)",
                              ((nvar,var),(nvar,var)))

    def test_invalid_int64_insert_too_small(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon63 (c1 BIGINT) in pybank")
            nvar = -2**63 - 1
            with self.assertRaises(DataError):
                c.execute("insert INTO jon63 VALUES (?)", (nvar))

    def test_invalid_int64_insert_too_big(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon65 (c1 BIGINT) in pybank")
            var = 2**63
            with self.assertRaises(DataError):
                c.execute("insert INTO jon65 VALUES (?)", (var))

    def test_valid_int16_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon26 (c1 SMALLINT, c2 SMALLINT)")
            nvar = -2**15
            var = 2**15 - 1
            c.execute("insert INTO jon26 VALUES (?, ?)", (nvar, var))

    def test_invalid_int16_insert_too_small(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon15 (c1 SMALLINT) in pybank")
            nvar = -2**15 - 1
            with self.assertRaises(DataError):
                c.execute("insert INTO jon15 VALUES (?)", (nvar))

    def test_invalid_int16_insert_too_small(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon17 (c1 SMALLINT) in pybank")
            nvar = 2**15
            with self.assertRaises(DataError):
                c.execute("insert INTO jon17 VALUES (?)", (nvar))

    # &&&& Gives a Warning we dont catch atm
    def test_valid_double_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon16 (c1 REAL, c2 DOUBLE PRECISION)")
            var = 2/3
            c.execute("insert INTO jon16 VALUES (?, ?)", (var, var))
            self.tstcon.commit()

    def test_valid_double_insert_none(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon18 (c1 REAL, c2 DOUBLE PRECISION)")
            var = None
            c.execute("insert INTO jon18 VALUES (?, ?)", (var, var))
            self.tstcon.commit()

    def test_valid_double_select_none(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jon19 (c1 REAL, c2 DOUBLE PRECISION)")
            var = None
            c.execute("insert INTO jon19 VALUES (?, ?)", (var, var))
            self.tstcon.commit()
            c.execute("select * from jon19")
            self.assertEqual(c.fetchall(), [(None, None)])

    def test_message_cleared(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonwas17 (c1 SMALLINT) in pybank")
            nvar = 2**15
            with self.assertRaises(DataError):
                c.execute("insert INTO jonwas17 VALUES (?)", (nvar))
            c.execute("insert INTO jonwas17 VALUES (?)", (5))
            self.assertEqual(c.messages, [])

    def test_message_cleared_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonwas173 (c1 SMALLINT) in pybank")
            nvar = 2**15
            with self.assertRaises(DataError):
                c.execute("insert INTO jonwas173 VALUES (?)", (nvar))
            self.assertEqual(c.messages[0][1],
                             (-24010,
                              'Value was too large to fit in destination'))

    def test_None_is_returned(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonNone (c1 INTEGER) in pybank")
            for i in range(1,10):
                c.execute("Insert INTO jonNone VALUES (?)", (i,))
            self.tstcon.commit()
            c.execute("SELECT * from jonNone")
            for i in range(1,10):
                c.fetchone()
            self.assertEqual(c.fetchone(), [])

    def test_empty_sequence_is_returned_many(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonEmpty (c1 INTEGER) in pybank")
            for i in range(1,10):
                c.execute("Insert INTO jonEmpty VALUES (?)", (i))
            self.tstcon.commit()
            c.execute("SELECT * from jonEmpty")
            c.fetchmany(10)
            self.assertEqual(c.fetchmany(10), [])

    def test_empty_sequence_is_returned_all(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonEmpty2 (c1 INTEGER) in pybank")
            for i in range(1,10):
                c.execute("Insert INTO jonEmpty2 VALUES (?)", (i))
            self.tstcon.commit()
            c.execute("SELECT * from jonEmpty2")
            c.fetchall()
            self.assertEqual(c.fetchall(), [])

    def test_empty_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonEmp (c1 NVARCHAR(128)) in pybank")
            c.executemany("Insert INTO jonEmp VALUES (?)",
                          (('',),("",),(" ",)))
            self.tstcon.commit()
            c.execute("select * from jonEmp")
            self.assertEqual(c.fetchall(), [('',), ('',), (' ',)])

    def test_empty_insert2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonEmp2 (c1 NVARCHAR(128)) in pybank")
            c.execute("Insert INTO jonEmp2 VALUES (?)", (''))
            c.execute("Insert INTO jonEmp2 VALUES (?)", (""))
            c.execute("Insert INTO jonEmp2 VALUES (?)", (" "))
            self.tstcon.commit()
            c.execute("select * from jonEmp2")
            self.assertEqual(c.fetchall(), [('',), ('',), (' ',)])

    def test_invalid_databank(self):
        with self.tstcon.cursor(scrollable = True) as c:
            with self.assertRaises(ProgrammingError):
                c.execute("create table bjonEmp2 (c1 NVARCHAR(128)) in potato")

    def test_insert_rowcount_update(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrowcount(c1 INTEGER, c2 NVARCHAR(256))")
            string = "mimer"
            c.execute("insert into bobrowcount values (:a, :b)", (3, string))
            self.assertEqual(c.rowcount, 1)
            c.executemany("insert into bobrowcount values (:a, :b)",
                          ((5,string),(2,string)))
            # self.assertEqual(c.rowcount, 2) # &&&& Should we set rowcount????
            c.execute("select * from bobrowcount")
            r = c.fetchall()
            self.assertEqual(c.rowcount, 3)

    def test_delete(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrowcount2(c1 INTEGER) in pybank")
            for i in range(1,11):
                c.execute("INSERT into bobrowcount2 values (?)", 10)
                c.execute("INSERT into bobrowcount2 values (?)", 20)
            c.execute("INSERT into bobrowcount2 values (?)", 10)
            c.execute("SELECT * from bobrowcount2")
            self.assertEqual(len(c.fetchall()), 21)
            c.execute("DELETE from bobrowcount2 where c1 = 10")
            self.assertEqual(c.rowcount, 11)
            c.execute("SELECT * from bobrowcount2")
            self.assertEqual(len(c.fetchall()), 10)

    def test_update(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobupdate(c1 INTEGER) in pybank")
            for i in range(1,11):
                c.execute("INSERT into bobupdate values (?)", 10)
                c.execute("INSERT into bobupdate values (?)", 20)
            c.execute("INSERT into bobupdate values (?)", 10)
            c.execute("SELECT * from bobupdate")
            self.assertEqual(len(c.fetchall()), 21)
            c.execute("UPDATE bobupdate SET c1 = ? WHERE c1 = 20", 30)
            self.assertEqual(c.rowcount, 10)
            c.execute("SELECT * from bobupdate")
            self.assertEqual(len(c.fetchall()), 21)

    def test_invalid_sequence_fetchone(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonfetchone (c1 INTEGER) in pybank")
            for i in range(1,10):
                c.execute("Insert INTO jonfetchone VALUES (?)", (i))
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.fetchone()

    def test_isolated(self):
        c1 = self.tstcon.cursor()
        c2 = self.tstcon.cursor()
        c1.execute("create table jonisolated (c1 INTEGER) in pybank")
        for i in range(1,6):
            c1.execute("Insert INTO jonisolated VALUES (?)", (i))
        c2.execute("SELECT * FROM jonisolated")
        r2 = c2.fetchall()
        self.assertEqual(len(r2), 5)
        self.assertEqual(r2, [(1,),(2,),(3,),(4,),(5,),])

    def test_invalid_sequence_fetchmany(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonfetchmany (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonfetchmany VALUES (?)", (i))
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.fetchmany(10)

    def test_invalid_sequence_fetchall(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonfetchall (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonfetchall VALUES (?)", (i))
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.fetchall()

    @unittest.skip
    # &&&& need to find a picture to put in the repo
    # Nä, gör en psudorandom-blob
    def test_insert_blob(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonblob (c1 BLOB(18389)) in pybank")
            with open("../minikappa.jpg", 'rb') as input_file:
                ablob = input_file.read()
                c.execute("insert INTO jonblob VALUES (?)", (ablob))
                self.tstcon.commit()
                c.execute("select * from jonblob")
                r = b.fetchall()[0]
                self.assertEqual(r[0], ablob)

    @unittest.skip
    # &&&& need to find a picture to put in the repo
    # Nä, gör en psudorandom-blob
    def test_insert_blob_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonblob2 (c1 BLOB(64111)) in pybank")
            with open("../mimerss.png", 'rb') as input_file:
                ablob = input_file.read()
                c.execute("insert INTO jonblob2 VALUES (?)", (ablob))
                self.tstcon.commit()
                c.execute("select * from jonblob2")
                r = c.fetchall()[0]
                self.assertEqual(r[0], ablob)

    @unittest.skip
    # &&&& need to find a picture to put in the repo
    # Nä, gör en psudorandom-blob
    def test_insert_blob_3(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonblob3 (c1 BLOB(3000000)) in pybank")
            with open("../mimerd.jpg", 'rb') as input_file:
                ablob = input_file.read()
                c.execute("insert INTO jonblob3 VALUES (?)", (ablob))
                self.tstcon.commit()
                c.execute("select * from jonblob3")
                r = c.fetchall()[0][0]
            self.assertEqual(r, ablob)

    @unittest.skip
    # &&&& need to find a picture to put in the repo
    # Nä, gör en psudorandom-blob
    def test_insert_blob_4(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonblob4 (c1 BLOB(3000000)) in pybank")
            with open("../kappa.jpg", 'rb') as input_file:
                ablob = input_file.read()
                c.execute("insert INTO jonblob4 VALUES (?)", (ablob))
                self.tstcon.commit()
                c.execute("select * from jonblob4")
                r = c.fetchall()[0][0]
            self.assertEqual(r, ablob)

    def test_insert_nclob(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonnclob (c1 NCLOB(50000)) in pybank")
            anclob = "mimer" * 1000
            c.execute("insert INTO jonnclob VALUES (?)", (anclob))
            self.tstcon.commit()
            c.execute("select * from jonnclob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], anclob)

    def test_insert_binary(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonbinary (c1 BINARY(3)) in pybank")
            c.execute("insert INTO jonbinary VALUES (x'ABCD01')")
            c.execute("insert INTO jonbinary VALUES (?)", (b'A01'))
            self.tstcon.commit()
            c.execute("select * from jonbinary")
            r = c.fetchall()
            self.assertEqual(r, [(b'\xab\xcd\x01',), (b'A01',)])

    def test_insert_binary_parameter_markers(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonbinary2 (c1 BINARY(2)) in pybank")
            bob = b'\xab\xcd'
            c.execute("insert INTO jonbinary2 VALUES (?)", (bob))
            self.tstcon.commit()
            c.execute("select * from jonbinary2")
            (r,) = c.fetchall()[0]
            self.assertEqual(r, bob)

    @unittest.skip
    def test_insert_nclob_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonnclob2 (c1 Nclob(450000)) in pybank")
            with open("../book2.txt", "r") as input_file:
                anclob = input_file.read()
                c.execute("insert INTO jonnclob2 VALUES (?)", (anclob))
                self.tstcon.commit()
                c.execute("select * from jonnclob2")
                r = c.fetchall()[0]
                self.assertEqual(r[0], anclob)

    def test_insert_clob(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table jonclob (c1 clob(30000)) in pybank")
            anclob = "mimer" * 5
            c.execute("insert INTO jonclob VALUES (?)", (anclob))
            self.tstcon.commit()
            c.execute("select * from jonclob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], anclob)

    def test_insert_bool(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobybool (c1 boolean) in pybank")
            c.execute("insert INTO bobybool VALUES (?)", (False))
            c.execute("insert INTO bobybool VALUES (?)", (True))
            c.execute("insert INTO bobybool VALUES (?)", (None))
            c.execute("insert INTO bobybool VALUES (?)", (45))
            self.tstcon.commit()

    def test_select_bool(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobybool2 (c1 boolean) in pybank")
            c.execute("insert INTO bobybool2 VALUES (?)", (False))
            c.execute("insert INTO bobybool2 VALUES (?)", (True))
            c.execute("insert INTO bobybool2 VALUES (?)", (None))
            c.execute("insert INTO bobybool2 VALUES (?)", (45))
            self.tstcon.commit()
            c.execute("select * from bobybool2")
            r = c.fetchone()
            self.assertEqual(r[0], False)
            r = c.fetchone()
            self.assertEqual(r[0], True)
            r = c.fetchone()
            self.assertEqual(r[0], None)
            r = c.fetchone()
            self.assertEqual(r[0], True)

    def test_get_connection(self):
        b = self.tstcon.cursor(scrollable = True)
        self.assertEqual(b.connection, self.tstcon)
        b.close()

    def test_for(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table fortable (c1 INTEGER) in pybank")
            c.execute("insert INTO fortable VALUES (?)", (45))
            c.execute("select * from fortable")
            for val in c:
                self.assertEqual(val[0], 45)

    def test_result_set_twice(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table kor (c1 INTEGER) in pybank")
            c.execute("insert INTO kor VALUES (?)", (45))
            c.execute("select * from kor")
            for val in c:
                self.assertEqual(val[0], 45)
            c.execute("select * from kor")
            for val in c:
                self.assertEqual(val[0], 45)
            c.execute("select c1 from kor")
            for val in c:
                self.assertEqual(val[0], 45)

    def test_executemany_none(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table manytable (c1 INTEGER) in pybank")
            c.executemany("insert INTO manytable VALUES (?)",
                          [(2,),(34,),(435,),(34,),(63,),(47,),(None,)])
            self.tstcon.commit()

    def test_select_executemany(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobyselect (c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("insert INTO bobyselect VALUES (?)", (1))
            with self.assertRaises(ProgrammingError):
                c.executemany("select * from bobyselect where c1 = (?)",
                              ((5,),(10,)))

    def test_select_twice(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bananaselect (c1 INTEGER) in pybank")
            c.execute("select * from bananaselect where c1 = (?)", (5))
            c.execute("select c1 from bananaselect where c1 = (?)", (7))

    def test_fetchall_no_select(self):
        with self.tstcon.cursor(scrollable = True) as c:
            with self.assertRaises(ProgrammingError):
                c.fetchone()
            with self.assertRaises(ProgrammingError):
                c.fetchmany()
            with self.assertRaises(ProgrammingError):
                c.fetchall()

    def test_bool_insert(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table boolt (c1 BOOLEAN) in pybank")
            c.executemany("insert into boolt values (?)",
                          [(None,), (1,), (0,), (3.1415,),
                           ("potato",), ('code',)])
            c.execute("select * from boolt")

    def test_insert_parametermarkers_different_types(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob176(c1 NVARCHAR(128)) in pybank")
            c.execute("INSERT INTO bob176 VALUES (?)", "bar")    # correct
            c.execute("INSERT INTO bob176 VALUES (?)", ("bar"))  # correct
            c.execute("INSERT INTO bob176 VALUES (?)", ("bar",)) # correct
            c.execute("INSERT INTO bob176 VALUES (?)", ["bar"])  # correct
            self.tstcon.commit()
            c.execute("select * from bob176")
            self.assertEqual(c.fetchall(),
                             [("bar",),("bar",),("bar",),("bar",)])

    def test_insert_bigint(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobbig17(c1 BIGINT) in pybank")
            self.tstcon.commit()
            c.execute("insert into bobbig17 values (234)")
            self.tstcon.commit()

    @unittest.skip
    def test_help(self):
        with self.tstcon.cursor(scrollable = True) as c:
            help(c)

    #ScrollCursor specific tests

    def test_fetchone_2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bob853 (c1 INTEGER, c2 NVARCHAR(10))")
            self.tstcon.commit()
            c.executemany("insert into bob853 values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'), (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob853")
            self.assertEqual(c.fetchone(), (9, 'bob9'))
            self.assertEqual(c.fetchone(), (10, 'bob10'))
            self.assertEqual(c.fetchone(), (11, 'bob11'))
            self.assertEqual(c.fetchone(), [])

    def test_fetchone_rownumber(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow (c1 INTEGER, c2 NVARCHAR(10))")
            c.executemany("insert into bobrow values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'), (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bobrow")
            self.assertEqual(c.rownumber, 0)
            self.assertEqual(c.fetchone(), (9, 'bob9'))
            self.assertEqual(c.rownumber, 1)
            self.assertEqual(c.fetchone(), (10, 'bob10'))
            self.assertEqual(c.rownumber, 2)
            self.assertEqual(c.fetchone(), (11, 'bob11'))
            self.assertEqual(c.rownumber, 3)
            self.assertEqual(c.fetchone(), [])
            self.assertEqual(c.rownumber, 3)

    def test_fetchmany_rownumber(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow2(c1 INTEGER, c2 NVARCHAR(100))")
            for i in range(1, 11):
                c.execute("insert into bobrow2 values (:a, :b)",
                          (i, 'bob' + str(i) ))
            self.tstcon.commit()
            c.execute("select * from bobrow2")
            self.assertEqual(c.rownumber, 0)
            self.assertEqual(c.fetchmany(3),
                             [(1, 'bob1'),(2, 'bob2'),(3, 'bob3')])
            self.assertEqual(c.rownumber, 3)
            self.assertEqual(c.fetchmany(3),
                             [(4, 'bob4'),(5, 'bob5'),(6, 'bob6')])
            self.assertEqual(c.rownumber, 6)
            self.assertEqual(c.fetchmany(10),
                             [(7, 'bob7'),(8, 'bob8'),(9, 'bob9'),(10, 'bob10')])
            self.assertEqual(c.rownumber, 10)
            self.assertEqual(c.fetchmany(2), [])

    def test_fetchall_rownumber(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow3(c1 INTEGER, c2 NVARCHAR(100))")
            for i in range(1, 6):
                c.execute("insert into bobrow3 values (:a, :b)",
                          (i, 'bob' + str(i) ))
            self.tstcon.commit()
            c.execute("select * from bobrow3")
            self.assertEqual(c.rownumber, 0)
            self.assertEqual(c.fetchall(),
                             [(1, 'bob1'),(2, 'bob2'),(3, 'bob3'),
                              (4, 'bob4'),(5, 'bob5')])
            self.assertEqual(c.rownumber, 5)
            self.assertEqual(c.fetchall(), [])

    def test_mixfetch_rownumber(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow4(c1 INTEGER, c2 NVARCHAR(100))")
            for i in range(1, 11):
                c.execute("insert into bobrow4 values (:a, :b)",
                          (i, 'bob' + str(i) ))
            self.tstcon.commit()
            c.execute("select * from bobrow4")
            self.assertEqual(c.rownumber, 0)
            self.assertEqual(c.fetchone(), (1, 'bob1'))
            self.assertEqual(c.rownumber, 1)
            self.assertEqual(c.fetchmany(3),
                             [(2, 'bob2'),(3, 'bob3'), (4, 'bob4')])
            self.assertEqual(c.rownumber, 4)
            self.assertEqual(c.fetchone(), (5, 'bob5'))
            self.assertEqual(c.rownumber, 5)
            self.assertEqual(c.fetchall(),
                             [(6, 'bob6'),(7, 'bob7'),(8, 'bob8'),
                              (9, 'bob9'),(10, 'bob10')])
            self.assertEqual(c.rownumber, 10)
            self.assertEqual(c.fetchone(), [])
            self.assertEqual(c.fetchmany(21), [])
            self.assertEqual(c.fetchall(), [])

    def test_mixfetch_rowcount(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow5(c1 INTEGER) in pybank")
            for i in range(1, 101):
                c.execute("insert into bobrow5 values (?)", (i))
            self.tstcon.commit()
            c.execute("select * from bobrow5")
            self.assertEqual(c.rowcount, 100)
            c.execute("select c1 from bobrow5 where c1 >= ?", (50))
            self.assertEqual(c.rowcount, 51)
            c.execute("select c1 from bobrow5 where c1 < ?", (10))
            self.assertEqual(c.rowcount, 9)

    def test_scroll(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow6(c1 INTEGER) in pybank")
            for i in range(1, 101):
                c.execute("insert into bobrow6 values (?)", (i))
            self.tstcon.commit()
            c.execute("select * from bobrow6")
            c.scroll(2,mode='relative')
            self.assertEqual(c.rownumber, 2)
            self.assertEqual(c.fetchone(), (3,))
            c.scroll(3,mode='relative')
            self.assertEqual(c.rownumber, 6)
            self.assertEqual(c.fetchone(), (7,))
            c.scroll(3,mode='absolute')
            self.assertEqual(c.rownumber, 3)
            c.scroll(5,mode='relative')
            self.assertEqual(c.rownumber, 8)

    def test_scroll_error(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow7(c1 INTEGER) in pybank")
            for i in range(1, 101):
                c.execute("insert into bobrow7 values (?)", (i))
            self.tstcon.commit()
            c.execute("select * from bobrow7")
            with self.assertRaises(ProgrammingError):
                c.scroll(5,mode='nonexistingmode')
            with self.assertRaises(IndexError):
                c.scroll(101,mode='absolute')

    def test_next(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow8(c1 INTEGER, c2 NVARCHAR(100))")
            for i in range(1, 11):
                c.execute("insert into bobrow8 values (:a, :b)",
                          (i, 'bob' + str(i) ))
            self.tstcon.commit()
            c.execute("select * from bobrow8")
            self.assertEqual(c.next(), (1, 'bob1'),)
            c.scroll(5,mode='relative')
            self.assertEqual(c.next(), (7, 'bob7'),)
            c.scroll(9, mode='absolute')

    def test_next_fetch(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow10(c1 INTEGER, c2 NVARCHAR(100))")
            for i in range(1, 11):
                c.execute("insert into bobrow10 values (:a, :b)",
                          (i, 'bob' + str(i) ))
            self.tstcon.commit()
            c.execute("select * from bobrow10")
            self.assertEqual(c.fetchone(), (1, 'bob1'),)
            self.assertEqual(c.next(), (2, 'bob2'),)
            self.assertEqual(c.fetchmany(2), [(3, 'bob3'), (4, 'bob4')])
            self.assertEqual(c.next(), (5, 'bob5'),)
            c.scroll(1, mode='relative')
            self.assertEqual(c.fetchall(),
                             [(7, 'bob7'), (8, 'bob8'),
                              (9, 'bob9'), (10, 'bob10')])

    def test_next_error(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobrow9(c1 INTEGER, c2 NVARCHAR(100))")
            for i in range(1, 11):
                c.execute("insert into bobrow9 values (:a, :b)",
                          (i, 'bob' + str(i) ))
            self.tstcon.commit()
            c.execute("select * from bobrow9")
            c.scroll(9, mode='absolute')
            with self.assertRaises(StopIteration):
                c.next()
                c.next()

    def test_fetchall_IndexError(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table indexerror (c1 INTEGER) in pybank")
            for val in range(0,10):
                c.execute("insert INTO indexerror VALUES (?)", (val))
            c.execute("select * from indexerror")
            r = c.fetchmany(9)
            r = c.fetchall()

    def test_fetchall_Scroll_outside(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table scrolloutside (c1 INTEGER) in pybank")
            for val in range(0,10):
                c.execute("insert INTO scrolloutside VALUES (?)", (val))
            c.execute("select * from scrolloutside")
            with self.assertRaises(IndexError):
                r = c.scroll(100)

    def test_no_select(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobnoselect(c1 INTEGER) in pybank")
            self.tstcon.commit()
            for i in range(1, 11):
                c.execute("insert into bobnoselect values (5)")
            self.tstcon.rollback()
            c.execute("select * from bobnoselect")
            r = c.fetchone()
            self.assertEqual(len(r), 0)

    def test_no_select2(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobnoselect2(c1 INTEGER) in pybank")
            self.tstcon.commit()
            for i in range(1, 11):
                c.execute("insert into bobnoselect2 values (5)")
            self.tstcon.rollback()
            c.execute("select * from bobnoselect2")
            r = c.fetchmany(5)
            self.assertEqual(len(r), 0)

    def test_no_select3(self):
        with self.tstcon.cursor(scrollable = True) as c:
            c.execute("create table bobnoselect3(c1 INTEGER) in pybank")
            self.tstcon.commit()
            for i in range(1, 11):
                c.execute("insert into bobnoselect3 values (5)")
            self.tstcon.rollback()
            c.execute("select * from bobnoselect3")
            r = c.next()
            self.assertEqual(len(r), 0)

    def test_next_noselect(self):
        with self.tstcon.cursor(scrollable = True) as c:
            with self.assertRaises(ProgrammingError):
                c.next()

if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
