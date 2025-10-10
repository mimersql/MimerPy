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

import unittest, time, math, random, uuid, decimal
import mimerpy
from mimerpy import mimerapi
from mimerpy.mimPyExceptions import *
import db_config


# noinspection SqlDialectInspection
class TestCursorMethods(unittest.TestCase):

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

    def test_fetchall_ts(self):
        with self.tstcon.cursor() as c:
            c.execute("select 'a', cast('2020-09-17 11:21:51' as timestamp(2)) from system.onerow")
            self.assertEqual(c.fetchall(), [('a', '2020-09-17 11:21:51.00')])

    def test_fetchall_timestamp_one(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_timestamp(c1 TIMESTAMP(2)) in pybank")
            c.execute("insert into bob_timestamp values (:a)", ('2020-09-17 11:21:51'))
            self.tstcon.commit()
            c.execute("select * from bob_timestamp")
            r = c.fetchone()
            self.assertEqual(r, ('2020-09-17 11:21:51.00',))

    def test_fetchall_timestamp_two(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_timestamp2(c1 TIMESTAMP(9)) in pybank")
            c.execute("insert into bob_timestamp2 values (:a)", ('2020-09-17 11:21:51.123456789'))
            self.tstcon.commit()
            c.execute("select * from bob_timestamp2")
            r = c.fetchone()
            self.assertEqual(r, ('2020-09-17 11:21:51.123456789',))

    def test_privilege(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(DatabaseError):
                c.execute("drop ident sysadm cascade")

    def test_createTable(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob(c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")

    def test_createTable_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobcr1(c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("create table bobcr2(c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("create table bobcr3(c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("create table bobcr4(c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
        self.tstcon.commit()

    def test_createTable_DropTable(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob2(c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("drop table bob2 CASCADE")
        self.tstcon.commit()

    def test_create_invalid_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon (c1 INTEGER, c2 INTEGER) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("banana INTO jon VALUES (3, 14)")

# &&&& This test should fail when we can rollback DDL
    def test_create_rollback_table(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonnynothere (c1 INTEGER, c2 INTEGER)"
                      " in pybank")
            self.tstcon.rollback()
            c.execute("select * from jonnynothere")

    def test_two_select(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonny (c1 INTEGER, c2 INTEGER) in pybank")
            c.execute("select c1 from jonny where c1 = (?)", (2))
            c.execute("select * from jonny")

    def test_many_select(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob356 (c1 INTEGER) in pybank")
            for val in range(100):
                c.execute("insert into bob356 values (:a)", (val))
            for gal in range(100):
                c.execute("select c1 from bob356 where c1 > (?)", (gal))
                r = c.fetchall()
                # &&&& Check resultset

    def test_select_no_commit(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobc (c1 INTEGER, c2 FLOAT) in pybank")
            for val in range(100):
                c.execute("insert into bobc values (:a, :b)", (val, val + 0.5))
            c.execute("select * from bobc where c1 = 99")
            self.assertEqual(c.fetchall(), [(99, 99.5)])

    def test_select_description(self):
        with self.tstcon.cursor() as c:
            c.execute("create table description (columnone INTEGER) in pybank")
            for val in range(10):
                c.execute("insert into description values (?)", val)
            c.execute("select * from description")
            self.assertEqual(c.description,
                             (('columnone', 50, None, None, None, None, None),))

    def test_select_description2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table description2 (c1 INTEGER, c2 FLOAT)"
                      " in pybank")
            for val in range(10):
                c.execute("insert into description2 values (?,?)",
                          (val, val / 3))
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
        with self.tstcon.cursor() as c:
            c.execute("""create table description3(price INTEGER,
                                      currentvalue FLOAT,
                                      currency NVARCHAR(128),
                                      rate BIGINT,
                                      currentyear INTEGER) in pybank""")
            for val in range(10):
                c.execute("insert into description3 values (?,?,?,?,?)",
                          (val, val / 3, 'SEK', 2 ** 61, val + 2000))
            c.execute("select * from description3")
            self.assertEqual(c.description,
                             (('price', 50, None, None, None, None, None),
                              ('currentvalue', 56, None, None, None, None, None),
                              ('currency', 63, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None),
                              ('currentyear', 50, None, None, None, None, None)))
            c.execute("select price, currentyear, currency, rate from description3")
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
                              ('currentvalue', 56, None, None, None, None, None),
                              ('currency', 63, None, None, None, None, None),
                              ('rate', 52, None, None, None, None, None),
                              ('currentyear', 50, None, None, None, None, None)))

    def test_select_description4(self):
        with self.tstcon.cursor() as c:
            name1 = "e" * 127 + "q"
            name2 = "m" * 127 + "q"
            query = ("create table description4 (" + name1 + " INTEGER, "
                     + name2 + " BOOLEAN) in pybank")
            c.execute(query)
            for val in range(10):
                c.execute("insert into description4 values (?,?)",
                          (val, val % 2))
            c.execute("select * from description4")
            self.assertEqual(c.description,
                             ((name1, 50, None, None, None, None, None),
                              (name2, 42, None, None, None, None, None)))

    def test_select_description5(self):
        with self.tstcon.cursor() as c:
            name1 = "e" * 127 + "q"
            name2 = "m" * 127 + "q"
            query = ("create table description5 (" + name1 + " INTEGER, " +
                     name2 + " BOOLEAN) in pybank")
            c.execute(query)
            for val in range(10):
                c.execute("insert into description5 values (?,?)",
                          (val, val % 2))
            c.execute("select * from description5")
            self.assertEqual(c.description,
                             ((name1, 50, None, None, None, None, None),
                              (name2, 42, None, None, None, None, None)))

    def test_invalid_create(self):
        b = self.tstcon.cursor()
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("create table jon(i int) in pybank")

    def test_insert_parametermarkers(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob1 (c1 INTEGER,  c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("insert into bob1 values (:a, :b)", (3, 'bob'))

    def test_insert_parametermarkers_long_string(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobstring (c1 INTEGER,  c2 NVARCHAR(256))"
                      " in pybank")
            string = "mimer" * 40
            c.execute("insert into bobstring values (:a, :b)", (3, string))
            self.tstcon.commit()
            c.execute("select c2 from bobstring")
            self.assertEqual(c.fetchall(), [(string,)])

    def test_insert_parametermarkers_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob13 (c1 INTEGER, c2 NVARCHAR(10),"
                      "                    c3 FLOAT) in pybank")
            self.tstcon.commit()
            pmarkers = [(1, 'pi', 14.345),
                           (2, 'pii', 14.345),
                           (-3, 'piii', 14.345),
                           (7, 'piii', 14.345),
                           (1121231, 'piiii', 14.345)]
            c.executemany("insert into bob13 values (:a, :b, :c)",
                         pmarkers)
            self.tstcon.commit()
            c.execute("select * from bob13")
            self.assertEqual(c.fetchall(),
                            pmarkers)

    def test_insert_parametermarkers_russian(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob14 (c1 INTEGER, c2 NVARCHAR(128),"
                      "                    c3 FLOAT) in pybank")
            self.tstcon.commit()
            c.executemany("insert into bob14 values (:a, :b, :c)",
                          ((1, 'продиктованной ангелом', 14.345),
                           (2, '安排他們參', 14.345)))
            self.tstcon.commit()
            c.execute("select * from bob14")
            self.assertEqual(c.fetchall(),
                             [(1, 'продиктованной ангелом', 14.345),
                              (2, '安排他們參', 14.345)])

    def test_insert_parametermarkers_unicode(self):
        with self.tstcon.cursor() as c:
            c.execute("create table boby14 (c1 INTEGER, c2 NVARCHAR(128),"
                      "                     c3 FLOAT) in pybank")
            self.tstcon.commit()
            c.executemany("insert into boby14 values (:a, :b, :c)",
                          ((1, 'продиктованной ангелом', 14.345),
                           (2, '安排他們參‱', 14.345)))
            self.tstcon.commit()
            c.execute("select * from boby14")
            self.assertEqual(c.fetchall(),
                             [(1, 'продиктованной ангелом', 14.345),
                              (2, '安排他們參‱', 14.345)])

    def test_insert_parametermarkers_goodchar(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobg14(c1 char(10)) in pybank")
            self.tstcon.commit()
            c.execute("insert into bobg14 values (?)", 'åååååååååå')
            self.tstcon.commit()
            c.execute("select * from bobg14")
            self.assertEqual(c.fetchall(),
                             [('åååååååååå',)])

    def test_insert_parametermarkers_illchar(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobz14(c1 char(10)) in pybank")
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.execute("insert into bobz14 values (?)", '安排')
            with self.assertRaises(ProgrammingError):
                c.execute("insert into bobz14 values (?)", '€')

    def test_insert_parametermarkers_too_long(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob15 (c1 NVARCHAR(10)) in pybank")
            self.tstcon.commit()
            with self.assertRaises(DatabaseError):
                c.execute("insert into bob15 values (:a)",
                          ('This sentence is too long'))
        self.tstcon.commit()

    def test_insert_too_few_parametermarkers(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob3 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            with self.assertRaises(DatabaseError):
                c.execute("insert into bob3 values (:a, :b)", (3))

    def test_insert_too_many_parametermarkers(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob33 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob33 values (:a, :b)",
                              ((3, 'pi', 14), (3)))

    def test_insert_parametermarkers_dict(self):
        with self.tstcon.cursor() as c:
            c.execute("create table poff_dict1 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("insert into poff_dict1 values (:a, :b)",
                              {'a':3, 'b':'pi'})
        self.tstcon.commit()

    def test_to_many_parametermarkers_dict(self):
        with self.tstcon.cursor() as c:
            c.execute("create table poff_dict2 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.execute("insert into poff_dict2 values (:a, :b)",
                              {'g':55, 'a':3, 'b':'pi', 'y':'Boo'})
            c.execute("select * from poff_dict2")
            r = c.fetchall()[0]
            self.assertEqual(r, (3, 'pi'))
        self.tstcon.commit()

    def test_insert_many_times(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob34(c1 INTEGER, c2 NVARCHAR(10),"
                      "                   c3 FLOAT) in pybank")
            for i in range(0, 101):
                c.execute("insert into bob34 values (5,'ウィキペディ', 4.4543543)")
        self.tstcon.commit()

    def test_executemany_one_value(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob4 (c1 INTEGER) in pybank")
            c.executemany("insert into bob4 values (:a)", [(1,)])
            #with self.assertRaises(ProgrammingError):
            c.execute("insert into bob4 values (:a)", [(1)])
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob4 values (:a)", (1))
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob4 values (:a)", [1])

    def test_executemany_one_tuple(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob5 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.executemany("insert into bob5 values (:a, :b)", ((1, 'bob1'),))

    def test_executemany_several_tuples(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobe6 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.executemany("insert into bobe6 values (:a, :b)",
                          [(1, 'bob1'), (2, 'bob2'),
                           (3, 'bob3')])

    def test_commit(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob7d (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.executemany("insert into bob7d values (:a, :b)",
                          ((1, 'bob1'), (2, 'bob2'),
                           (3, 'bob3')))
            self.tstcon.commit()

    ### &&&& Should fail since DDL has no commit
    def test_fetchone(self):
        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.cursor()
        b.execute("create table bob8 (c1 INTEGER, c2 NVARCHAR(10)) in pybank")
        a.close()

        with self.tstcon.cursor() as c:
            c.execute("insert into bob8 values (:a, :b)", (8, 'bob'))
            self.tstcon.commit()
            c.execute("select * from bob8")
            self.assertEqual(c.fetchone(), (8, 'bob'))

    def test_fetchmany(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob9 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            self.tstcon.commit()

            c.executemany("insert into bob9 values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'),
                           (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob9")
            self.assertEqual(c.fetchmany(3),
                             [(9, 'bob9'), (10, 'bob10'), (11, 'bob11')])

    def test_fetchmany_too_many(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob11 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            self.tstcon.commit()
            c.executemany("insert into bob11 values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'),
                           (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob11")
            self.assertEqual(c.fetchmany(5),
                             [(9, 'bob9'), (10, 'bob10'), (11, 'bob11')])

    def test_fetchmany_notall(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob12 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            self.tstcon.commit()
            c.executemany("insert into bob12 values (:a, :b)",
                          ((9, 'bob9'), (10, 'bob10'),
                           (11, 'bob11')))
            self.tstcon.commit()
            c.execute("select * from bob12")
            self.assertEqual(c.fetchmany(2),
                             [(9, 'bob9'), (10, 'bob10')])
            self.assertEqual(c.fetchmany(2), [(11, 'bob11')])

    def test_fetchmany_generator_smol(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_generator (c1 INTEGER, c2 INTEGER)"
                      " in pybank")
            generator = ((i,-i) for i in range(10))
            c.executemany("insert into bob_generator values (:a, :b)", generator)
            self.tstcon.commit()

    def test_fetchmany_generator_large(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_generator2 (c1 INTEGER, c2 INTEGER)"
                      " in pybank")
        with self.tstcon.cursor() as c:
            size = 100000
            generator = ((i,-i) for i in range(size))
            c.executemany("insert into bob_generator2 values (:a, :b)", generator)
            self.tstcon.commit()
            c.execute("SELECT MAX(c1), MIN(c2) AS maxv FROM bob_generator2")
            self.assertEqual(c.fetchone(),(size - 1, -size + 1))

    @unittest.skip
    def test_fetchmany_generator_too_large(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_generator3 (c1 INTEGER, c2 INTEGER)"
                    " in pybank")
        with self.tstcon.cursor() as c:
            size = 1000000
            generator = ((i,-i) for i in range(size))
            c.executemany("insert into bob_generator3 values (:a, :b)", generator)
            self.tstcon.commit()
            c.execute("SELECT MAX(c1), MIN(c2) AS maxv FROM bob_generator")
            self.assertEqual(c.fetchone(),(size - 1, -size + 1))

    def test_fetchall(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob10 (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            self.tstcon.commit()
            c.executemany("insert into bob10 values (:a, :b)",
                          ((10, 'bob10'), (11, 'bob11'), (12, 'bob12'),))
            self.tstcon.commit()
            c.execute("select * from bob10")
            self.assertEqual(c.fetchall(),
                             [(10, 'bob10'), (11, 'bob11'), (12, 'bob12')])

    def test_fetchall_correct_number_of_rows(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob101(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
            for i in range(1, 101):
                c.execute("insert into bob101 values (5,'ウィキペディ', 4.4543543)")
            self.tstcon.commit()
            c.execute("select * from bob101")
            r = c.fetchall()
            self.assertEqual(len(r), 100)

    def test_fetchall_correct_number_of_rows2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob102(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
        with self.tstcon.cursor() as c:
            for i in range(1, 101):
                c.execute("insert into bob102 values (5,'ウィキペディ', 4.4543543)")
            self.tstcon.rollback()
            c.execute("select * from bob102")
            r = c.fetchall()
            self.assertEqual(len(r), 0)

    def test_fetchall_correct_number_of_rows3(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob103(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
        with self.tstcon.cursor() as c:  
            for i in range(1, 101):
                c.execute("insert into bob103 values (5,'ウィキペディ', 4.4543543)")
                self.tstcon.rollback()
                c.execute("select * from bob103")
                r = c.fetchall()
                self.assertEqual(len(r), 0)

    def test_use_next(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobnext(c1 INTEGER) in pybank")
            for i in range(0, 10):
                c.execute("insert into bobnext values (?)", i)
                self.tstcon.commit()
                c.execute("select * from bobnext")
            for i in range(0, 10):
                val = c.next()
                self.assertEqual(val, (i,))

    def test_use_next_StopIteration(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobstop(c1 INTEGER) in pybank")
            for i in range(0, 10):
                c.execute("insert into bobstop values (?)", i)
                self.tstcon.commit()
                c.execute("select * from bobstop")
            for i in range(0, 10):
                c.next()
            with self.assertRaises(StopIteration):
                c.next()

    def test_insert_wrong_type_parametermarkers(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob1337 (c1 INTEGER, c2 INTEGER) in pybank")
            with self.assertRaises(DataError):
                c.execute("insert into bob1337  values (:a, :b)", (3, 3.14))

    def test_operate_after_closed(self):
        c = self.tstcon.cursor()
        c.close()
        with self.assertRaises(ProgrammingError):
            c.execute("select * from system.onerow")

    def test_operate_after_closed_2(self):
        c = self.tstcon.cursor()
        c.close()
        c.close()
        with self.assertRaises(ProgrammingError):
            c.execute("Kalle")
        with self.assertRaises(ProgrammingError):
            c.executemany("Kalle", ("Kula"))
        with self.assertRaises(ProgrammingError):
            c.fetchone()
        with self.assertRaises(ProgrammingError):
            c.fetchmany("Kalle")
        with self.assertRaises(ProgrammingError):
            c.fetchall()
        with self.assertRaises(ProgrammingError):
            c.next()

    def test_invalid_select(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(ProgrammingError):
                c.execute("select * from jonisnotatablejo where c1 = ?", (5))

    def test_same_table_twice(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob2437(c1 INTEGER) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob2437(c1 INTEGER) in pybank")

    def test_invalid_sequence_select(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob6565(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("select * from bob6565")
            r = c.fetchone()
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob6569(c1 INTEGER) in pybank")

    # &&&& borde bli fel men blir rätt....
    # Blir inte rätt för att man blandar DDL och DML i samma transaktion
    @unittest.skip
    def test_invalid_sequence_select_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob555(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("select * from bob555")
            c.execute("create table bob556(c1 INTEGER) in pybank")
            c.execute("insert into bob556 values (3)")
            self.tstcon.rollback()
            c.execute("select * from bob556")
            self.assertEqual(c.fetchone(), [])

    def test_invalid_sequence_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob6567(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("insert into bob6567 values (3)")
            ## &&&& Should not fail
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob65ss(c1 INTEGER) in pybank")
                self.tstcon.rollback()

    def test_invalid_sequence_insert_parametermarkers(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob6568(c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("insert into bob6568 values (?)", (3))
            ## &&&& Should not fail
            with self.assertRaises(ProgrammingError):
                c.execute("create table bob6566(c1 INTEGER) in pybank")
                self.tstcon.rollback()

    def test_executemany_DDL(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(ProgrammingError):
                b = c.executemany("create table bob6(c1 INTEGER) in pybank",
                                  (3))

    def test_insert_exceeded(self):
        with self.tstcon.cursor() as c:
            b = c.execute("create table bob16(c1 BIGINT) in pybank")
            big = pow(2, 100)
            with self.assertRaises(DataError):
                c.execute("insert into bob16 values (?)", big)

    def test_insert_too_long(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob17(c1 NVARCHAR(10)) in pybank")
            self.tstcon.commit()
            with self.assertRaises(DataError):
                c.execute("insert into bob17 values ('ウィキペデBobWasAYoungBoy')")
                self.tstcon.commit()

    def test_valid_int32_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon32 (c1 INTEGER, c2 INTEGER) in pybank")
            nvar = -2 ** 31
            var = 2 ** 31 - 1
            c.execute("insert INTO jon32 VALUES (?, ?)", (nvar, var))
            self.tstcon.commit()

    def test_invalid_int32_insert_too_small(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon31 (c1 INTEGER) in pybank")
            nvar = -2 ** 31 - 1
            with self.assertRaises(DataError):
                c.execute("insert INTO jon31 VALUES (?)", (nvar))

    def test_invalid_int32_insert_too_big(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon33 (c1 INTEGER) in pybank")
            var = 2 ** 31
            with self.assertRaises(DataError):
                c.execute("insert INTO jon33 VALUES (?)", (var))

    def test_valid_int64_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon64 (c1 BIGINT, c2 BIGINT) in pybank")
            nvar = -2 ** 63
            var = 2 ** 63 - 1
            c.execute("insert INTO jon64 VALUES (?,?)", (nvar, var))
            self.tstcon.commit()
            c.execute("Select * from jon64")
            self.assertEqual(c.fetchall(), [(nvar, var)])

    def test_overflow_int64_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table intjon4 (c1 BIGINT, c2 BIGINT) in pybank")
            nvar = -2 ** 633
            var = 2 ** 63 - 1
            with self.assertRaises(DataError):
                c.executemany("insert INTO intjon4 VALUES (?,?)",
                              ((nvar, var), (nvar, var)))

    def test_invalid_int64_insert_too_small(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon63 (c1 BIGINT) in pybank")
            nvar = -2 ** 63 - 1
            with self.assertRaises(DataError):
                c.execute("insert INTO jon63 VALUES (?)", (nvar))

    def test_invalid_int64_insert_too_big(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon65 (c1 BIGINT) in pybank")
            var = 2 ** 63
            with self.assertRaises(DataError):
                c.execute("insert INTO jon65 VALUES (?)", (var))

    def test_valid_int16_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon26 (c1 SMALLINT, c2 SMALLINT) in pybank")
            nvar = -2 ** 15
            var = 2 ** 15 - 1
            c.execute("insert INTO jon26 VALUES (?, ?)", (nvar, var))
            self.tstcon.commit()
            c.execute("SELECT * from jon26")
            self.assertEqual(c.fetchall(), [(nvar,var)])

    def test_invalid_int16_insert_too_small(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon15 (c1 SMALLINT) in pybank")
            nvar = -2 ** 15 - 1
            with self.assertRaises(DataError):
                c.execute("insert INTO jon15 VALUES (?)", (nvar))

    def test_invalid_int16_insert_too_big(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon17 (c1 SMALLINT) in pybank")
            nvar = 2 ** 15
            with self.assertRaises(DataError):
                c.execute("insert INTO jon17 VALUES (?)", (nvar))

    # &&&& Gives a Warning we dont catch atm
    def test_valid_double_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon16 (c1 REAL, c2 DOUBLE PRECISION)"
                      " in pybank")
            var = 2 / 3
            c.execute("insert INTO jon16 VALUES (?, ?)", (var, var))
            self.tstcon.commit()
            c.execute("select * from jon16")
            self.assertEqual(c.fetchall(), [(0.6666666865348816, var)])

    def test_invalid_double_insert(self):
        b = self.tstcon.cursor()
        c = self.tstcon.cursor()
        d = self.tstcon.cursor()
        e = self.tstcon.cursor()
        f = self.tstcon.cursor()
        b.execute("create table jondd (c1 FLOAT) in pybank")
        var = 10 ** 309
        with self.assertRaises(DataError):
            b.execute("insert INTO jondd VALUES (?)", (var))
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jondd VALUES (?, ?)", (-var, -var))
        b.close()
        c.close()
        d.close()
        e.close()
        f.close()

    def test_valid_double_insert_none(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon18 (c1 REAL, c2 DOUBLE PRECISION)"
                      " in pybank")
            var = None
            c.execute("insert INTO jon18 VALUES (?, ?)", (var, var))
            self.tstcon.commit()
            c.execute("select * from jon18")
            self.assertEqual(c.fetchall(), [(None, None)])

    def test_valid_double_select_none(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon19 (c1 REAL, c2 DOUBLE PRECISION)"
                      " in pybank")
            var = None
            c.execute("insert INTO jon19 VALUES (?, ?)", (var, var))
            self.tstcon.commit()
            c.execute("select * from jon19")
            self.assertEqual(c.fetchall(), [(None, None)])

    def test_message_cleared(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonwas17 (c1 SMALLINT) in pybank")
            nvar = 2 ** 15
            with self.assertRaises(DataError):
                c.execute("insert INTO jonwas17 VALUES (?)", (nvar))
            c.execute("insert INTO jonwas17 VALUES (?)", (5))
            self.assertEqual(c.messages, [])

    def test_message_cleared_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonwas173 (c1 SMALLINT) in pybank")
            nvar = 2 ** 15
            with self.assertRaises(DataError):
                c.execute("insert INTO jonwas173 VALUES (?)", (nvar))
            self.assertEqual(c.messages[0][1],
                             (-24010,
                              'Value was too large to fit in destination'))

    def test_None_is_returned(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonNone (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonNone VALUES (?)", (i))
            self.tstcon.commit()
            c.execute("SELECT * from jonNone")
            for i in range(1, 10):
                c.fetchone()
            self.assertEqual(c.fetchone(), [])

    def test_empty_sequence_is_returned_many(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonEmpty (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonEmpty VALUES (?)", (i))
            self.tstcon.commit()
            c.execute("SELECT * from jonEmpty")
            c.fetchmany(10)
            self.assertEqual(c.fetchmany(10), [])

    def test_empty_sequence_is_returned_all(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonEmpty2 (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonEmpty2 VALUES (?)", (i))
            self.tstcon.commit()
            c.execute("SELECT * from jonEmpty2")
            c.fetchall()
            self.assertEqual(c.fetchall(), [])

    def test_empty_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonEmp (c1 NVARCHAR(128)) in pybank")
            c.executemany("Insert INTO jonEmp VALUES (?)",
                          (('',), ("",), (" ",)))
            self.tstcon.commit()
            c.execute("select * from jonEmp")
            self.assertEqual(c.fetchall(), [('',), ('',), (' ',)])

    def test_empty_insert2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonEmp2 (c1 NVARCHAR(128)) in pybank")
            c.execute("Insert INTO jonEmp2 VALUES (?)", (''))
            c.execute("Insert INTO jonEmp2 VALUES (?)", (""))
            c.execute("Insert INTO jonEmp2 VALUES (?)", (" "))
            self.tstcon.commit()
            c.execute("select * from jonEmp2")
            self.assertEqual(c.fetchall(), [('',), ('',), (' ',)])

    def test_invalid_databank(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(ProgrammingError):
                c.execute("create table bjonEmp2 (c1 NVARCHAR(128)) in potato")

    def test_insert_rowcount_update(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobrowcount (c1 INTEGER, c2 NVARCHAR(256))"
                      " in pybank")
            string = "mimer"
            c.execute("insert into bobrowcount values (:a, :b)", (3, string))
            self.assertEqual(c.rowcount, 1)
            c.executemany("insert into bobrowcount values (:a, :b)",
                          ((5, string), (2, string)))
            c.execute("select * from bobrowcount")
            r = c.fetchall()
            self.assertEqual(c.rowcount, 2)

    def test_delete(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobrowcount2(c1 INTEGER) in pybank")
            for i in range(1, 11):
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
        with self.tstcon.cursor() as c:
            c.execute("create table bobupdate(c1 INTEGER) in pybank")
            for i in range(1, 11):
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
        with self.tstcon.cursor() as c:
            c.execute("create table jonfetchone (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonfetchone VALUES (?)", (i))
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.fetchone()

    def test_isolated(self):
        b1 = self.tstcon.cursor()
        b2 = self.tstcon.cursor()
        b1.execute("create table jonisolated (c1 INTEGER) in pybank")
        for c in range(1, 6):
            b1.execute("Insert INTO jonisolated VALUES (?)", (c))
        b2.execute("SELECT * FROM jonisolated")
        c2 = b2.fetchall()
        self.assertEqual(len(c2), 5)
        self.assertEqual(c2, [(1,), (2,), (3,), (4,), (5,), ])

    def test_isolated2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonisolated2 (c1 INTEGER) in pybank")
            self.tstcon.commit()

        cred = db_config.TSTUSR.copy()
        cred['autocommit'] = True
        a1 = mimerpy.connect(**cred)
        a2 = mimerpy.connect(**cred)
        b1 = a1.cursor()
        b2 = a2.cursor()
        for c in range(1, 6):
            b1.execute("Insert INTO jonisolated2 VALUES (?)", (c))
        b2.execute("SELECT * FROM jonisolated2 WHERE c1 < ?", 3)
        c2 = b2.fetchall()
        self.assertEqual(len(c2), 2)
        self.assertEqual(c2, [(1,), (2,)])
        b2.execute("SELECT * FROM jonisolated2")
        c3 = b2.fetchall()
        self.assertEqual(len(c3), 5)
        self.assertEqual(c3, [(1,), (2,), (3,), (4,), (5,), ])
        a1.close()
        a2.close()

    # fråga per
    def test_isolated3(self):
        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.cursor()
        b.execute("create table jonisolated3 (c1 INTEGER) in pybank")
        a.commit()
        a.close()
        with self.tstcon.cursor() as c:
            for i in range(1, 6):
                c.execute("Insert INTO jonisolated3 VALUES (?)", (i))
            c.execute("SELECT * FROM jonisolated3")
            c1 = c.fetchall()
            self.assertEqual(c1, [(1,), (2,), (3,), (4,), (5,), ])
            c.execute("SELECT * FROM jonisolated3")
            c2 = c.fetchall()
            self.assertEqual(c2, [(1,), (2,), (3,), (4,), (5,), ])

    def test_invalid_sequence_fetchmany(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonfetchmany (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonfetchmany VALUES (?)", (i))
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.fetchmany(10)

    def test_invalid_sequence_fetchall(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonfetchall (c1 INTEGER) in pybank")
            for i in range(1, 10):
                c.execute("Insert INTO jonfetchall VALUES (?)", (i))
            self.tstcon.commit()
            with self.assertRaises(ProgrammingError):
                c.fetchall()

    @unittest.skip
    def test_UUID_one(self):
        with self.tstcon.cursor() as c:
            c.execute("create table uuidtable( id BUILTIN.UUID) in pybank")
            vuuid = uuid.uuid4().bytes
            c.execute("insert into uuidtable values(?)", (vuuid))
            self.tstcon.commit()
            c.execute("select id.as_text() from uuidtable")
            r = c.fetchall()[0][0]
            self.assertEqual(r, vuuid)

    
    def test_UUID_two(self):
        with self.tstcon.cursor() as c:
            c.execute("create table uuidtable2( id BUILTIN.UUID) in pybank")
            vuuid = str(uuid.uuid1())
            c.execute("insert into uuidtable2 values(builtin.uuid_from_text(cast(? as varchar(50))))", (vuuid))
            self.tstcon.commit()
            c.execute("select id.as_text() from uuidtable2")
            r = c.fetchall()[0][0]
            self.assertEqual(r, vuuid)

    @unittest.skip
    def test_datatype_GIS_one(self):
        with self.tstcon.cursor() as c:
            vuuid = '40.75,-74.0'
            c.execute("create table gistable2( id BUILTIN.GIS_LATITUDE) in pybank")
            c.execute("insert into gistable2 values(BUILTIN.GIS_LOCATION(40.75,-74.0))")
            self.tstcon.commit()
            c.execute("select id.as_text() from uuidtable2")
            r = c.fetchall()[0][0]
            self.assertEqual(r, vuuid)

    @unittest.skip
    def test_datatype_GIS(self):
        with self.tstcon.cursor() as c:
            c.execute("create table gistable2( id BUILTIN.GIS_LATITUDE) in pybank")
            x,y = 40.75,-74.0
            c.execute("insert into gistable2 values(BUILTIN.GIS_LOCATION(?,?))", (x,y))
            self.tstcon.commit()
            #c.execute("select id.as_text() from uuidtable2")
            #r = c.fetchall()[0][0]
            #self.assertEqual(r, vuuid)

    def test_insert_blob(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonblob (c1 BLOB(18389)) in pybank")
            ablob = bytes(bytearray("Hello there", encoding ='utf-8'))
            c.execute("insert INTO jonblob VALUES (?)", (ablob))
            self.tstcon.commit()
            c.execute("select * from jonblob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ablob)

    def test_insert_blob_21(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonblob2 (c1 BLOB(64111)) in pybank")
            with open("testCursor.py", 'rb') as input_file:
                ablob = input_file.read(200)
                c.execute("insert INTO jonblob2 VALUES (?)", (ablob))
                self.tstcon.commit()
                c.execute("select * from jonblob2")
                r = c.fetchall()[0]
                self.assertEqual(r[0], ablob)

    def test_insert_blob_multi_column(self):
        with self.tstcon.cursor() as c:
            ablob = ('åäö' * 1024 * 2000).encode('utf-8') 
            c.execute("create table jonblobmulti (c1 BLOB(20m), c2 BLOB(20m)) in pybank")
            c.execute("insert INTO jonblobmulti VALUES (?,?)", (ablob,ablob))
            self.tstcon.commit()
            c.execute("select * from jonblobmulti")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ablob)
    
    def test_insert_blob_multi_column2(self):
        with self.tstcon.cursor() as c:
            ablob = (256).to_bytes(1024 * 10000,byteorder='big')
            ablob2 = ('åäö' * 1024 * 3000).encode('utf-8')
            c.execute("create table jonblobmulti2 (c1 BLOB(30m), c2 BLOB(30m), c3 BLOB(30m)) in pybank")
            c.execute("insert INTO jonblobmulti2 VALUES (?,?,?)", (ablob,ablob,ablob2))
            self.tstcon.commit()
            c.execute("select * from jonblobmulti2")
            r = c.fetchall()[0]
            self.assertEqual(r[2], ablob2)

    def test_insert_blob_10mb(self):
        with self.tstcon.cursor() as c:
            ablob = (256).to_bytes(1024 * 10000,byteorder='big') 
            c.execute("create table jonblob10 (c1 BLOB(100m)) in pybank")
            c.execute("insert INTO jonblob10 VALUES (?)", (ablob))
            self.tstcon.commit()
            c.execute("select * from jonblob10")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ablob)
    
    #@unittest.skip
    def test_insert_blob_50mb(self):
        with self.tstcon.cursor() as c:
            ablob = (512).to_bytes(1024 * 50000,byteorder='big') 
            c.execute("create table jonblob50 (c1 BLOB(100m)) in pybank")
            c.execute("insert INTO jonblob50 VALUES (?)", (ablob))
            self.tstcon.commit()
            c.execute("select * from jonblob50")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ablob)
    
    #@unittest.skip
    def test_insert_blob_100mb(self):
        with self.tstcon.cursor() as c:
            ablob = (1024).to_bytes(1024 * 100000,byteorder='big') 
            c.execute("create table jonblob100 (c1 BLOB(100m)) in pybank")
            c.execute("insert INTO jonblob100 VALUES (?)", (ablob))
            self.tstcon.commit()
            c.execute("select * from jonblob100")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ablob)

    # Might have to up your bufferpool memory to run this
    @unittest.skip
    def test_insert_blob_1gb(self):
        with self.tstcon.cursor() as c:
            ablob = (1024).to_bytes(1024 * 1000000,byteorder='big') 
            c.execute("create table jonblobgb (c1 BLOB(1000m)) in pybank")
            c.execute("insert INTO jonblobgb VALUES (?)", (ablob))
            self.tstcon.commit()
            c.execute("select * from jonblobgb")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ablob)

    def test_insert_nclob(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonnclob (c1 NCLOB(50000)) in pybank")
            anclob = "mimer" * 1000
            c.execute("insert INTO jonnclob VALUES (?)", (anclob))
            self.tstcon.commit()
            c.execute("select * from jonnclob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], anclob)

    def test_insert_nclob_unicode(self):
        with self.tstcon.cursor() as c:
            c.execute("create table unijonnclob (c1 NCLOB(50000)) in pybank")
            uniclob = "安排他們參"
            self.tstcon.commit()
            c.execute("insert into unijonnclob values (:a)",(uniclob,))
            self.tstcon.commit()
            c.execute("select * from unijonnclob")
            self.assertEqual(c.fetchall(),
                             [(uniclob,)])

    def test_insert_binary(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonbinary (c1 BINARY(3)) in pybank")
            c.execute("insert INTO jonbinary VALUES (x'ABCD01')")
            c.execute("insert INTO jonbinary VALUES (?)", (b'A01'))
            self.tstcon.commit()
            c.execute("select * from jonbinary")
            r = c.fetchall()
            self.assertEqual(r, [(b'\xab\xcd\x01',), (b'A01',)])

    def test_insert_binary_parameter_markers(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonbinary2 (c1 BINARY(4)) in pybank")
            bob = b"0x53"
            c.execute("insert INTO jonbinary2 VALUES (?)", (bob))
            self.tstcon.commit()
            c.execute("select * from jonbinary2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], b'0x53')

    def test_insert_nclob_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonnclob2 (c1 Nclob(450000)) in pybank")
            res = ''.join(format(i, 'b') for i in bytearray("Hello there", encoding ='utf-8')) 
            c.execute("insert INTO jonnclob2 VALUES (?)", (res))
            self.tstcon.commit()
            c.execute("select * from jonnclob2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], res)

    def test_insert_clob(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonclob (c1 clob(30000)) in pybank")
            aclob = "mimer" * 5
            c.execute("insert INTO jonclob VALUES (?)", (aclob))
            self.tstcon.commit()
            c.execute("select * from jonclob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], aclob)

    def test_datatype_clob(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonclob2 (c1 clob) in pybank")
            aclob = "mimer" * 5
            c.execute("insert INTO jonclob2 VALUES (?)", (aclob))
            self.tstcon.commit()
            c.execute("select * from jonclob2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], aclob)

    def test_insert_date(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jondata (c1 DATE) in pybank")
            data = "2020-09-24"
            c.execute("insert INTO jondata VALUES (?)", (data))
            self.tstcon.commit()
            c.execute("select * from jondata")
            r = c.fetchall()[0]
            self.assertEqual(r[0], data)

    def test_insert_time_one(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jontime (c1 TIME(0)) in pybank")
            time = "16:04:55"
            c.execute("insert INTO jontime VALUES (?)", (time))
            self.tstcon.commit()
            c.execute("select * from jontime")
            r = c.fetchall()[0]
            self.assertEqual(r[0], time)

    def test_insert_time_two(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jontime2 (c1 TIME(4)) in pybank")
            time = "16:04:55.1234"
            c.execute("insert INTO jontime2 VALUES (?)", (time))
            self.tstcon.commit()
            c.execute("select * from jontime2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], time)
    
    def test_insert_decimal_str(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jondecimal (c1 DECIMAL(7,2)) in pybank")
            floatnum = '32423.23'
            c.execute("insert INTO jondecimal VALUES (?)", (floatnum))
            self.tstcon.commit()
            c.execute("select * from jondecimal")
            r = c.fetchall()[0]
            self.assertEqual(r[0], decimal.Decimal(floatnum))

    def test_insert_decimal_decimal(self):
        with self.tstcon.cursor() as c:
            decimal.getcontext().prec = 45
            des = decimal.Decimal("1.14")
            c.execute("create table jondecimal2 (c1 DECIMAL(3,2)) in pybank")
            c.execute("insert INTO jondecimal2 VALUES (?)", (des))
            self.tstcon.commit()
            c.execute("select * from jondecimal2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], des)

    # Bör runda av, men ger för tillfället en exception
    @unittest.skip
    def test_insert_decimal_decimal2(self):
        with self.tstcon.cursor() as c:
            decimal.getcontext().prec = 45
            des = decimal.Decimal("1.141")
            c.execute("create table jondecimal2 (c1 DECIMAL(3,2)) in pybank")
            c.execute("insert INTO jondecimal2 VALUES (?)", (des))
            self.tstcon.commit()
            c.execute("select * from jondecimal2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], des)

    def test_insert_decimal_decimal3(self):
        with self.tstcon.cursor() as c:
            decimal.getcontext().prec = 45
            des = decimal.Decimal("1.14")
            c.execute("create table jondecimal22 (c1 DECIMAL(3,2)) in pybank")
            c.execute("insert INTO jondecimal22 VALUES (cast(cast('1.141' as varchar(20)) as DECIMAL(3,2)))")
            self.tstcon.commit()
            c.execute("select * from jondecimal22")
            r = c.fetchall()[0]
            self.assertEqual(r[0], des)

    def test_insert_decimal_none(self):
        with self.tstcon.cursor() as c:
            decimal.getcontext().prec = 45
            c.execute("create table jondecimalnone (c1 DECIMAL(3,2)) in pybank")
            c.execute("insert INTO jondecimalnone VALUES (?)", (None))
            self.tstcon.commit()
            c.execute("select * from jondecimalnone")
            r = c.fetchall()[0]
            self.assertEqual(r[0], None)

    def test_datatype_interval_DAY(self):
        with self.tstcon.cursor() as c:
            day = "20005"
            c.execute("create table jonday (c1 INTERVAL DAY(5)) in pybank")
            c.execute("insert INTO jonday VALUES (?)", (day))
            self.tstcon.commit()
            c.execute("select * from jonday")
            r = c.fetchall()[0]
            self.assertEqual(r[0], day)

    def test_datatype_interval_HOUR(self):
        with self.tstcon.cursor() as c:
            hour = "20005"
            c.execute("create table jonhour (c1 INTERVAL HOUR(5)) in pybank")
            c.execute("insert INTO jonhour VALUES (?)", (hour))
            self.tstcon.commit()
            c.execute("select * from jonhour")
            r = c.fetchall()[0]
            self.assertEqual(r[0], hour)

    def test_datatype_interval_MINUTE(self):
        with self.tstcon.cursor() as c:
            minute = "1234567890"
            c.execute("create table jonminute (c1 INTERVAL MINUTE(10)) in pybank")
            c.execute("insert INTO jonminute VALUES (?)", (minute))
            self.tstcon.commit()
            c.execute("select * from jonminute")
            r = c.fetchall()[0]
            self.assertEqual(r[0], minute)

    def test_datatype_interval_year(self):
        with self.tstcon.cursor() as c:
            year = "20005"
            c.execute("create table jonyear (c1 INTERVAL year(5)) in pybank")
            c.execute("insert INTO jonyear VALUES (?)", (year))
            self.tstcon.commit()
            c.execute("select * from jonyear")
            r = c.fetchall()[0]
            self.assertEqual(r[0], year)

    def test_datatype_interval_SECOND(self):
        with self.tstcon.cursor() as c:
            second = "20005.000000"
            c.execute("create table jonsecond (c1 INTERVAL SECOND(5)) in pybank")
            c.execute("insert INTO jonsecond VALUES (?)", (second))
            self.tstcon.commit()
            c.execute("select * from jonsecond")
            r = c.fetchall()[0]
            self.assertEqual(r[0], second)

    def test_datatype_interval_SECOND_P(self):
        with self.tstcon.cursor() as c:
            second = "12345.67"
            c.execute("create table jonsecondp (c1 INTERVAL SECOND(5,2)) in pybank")
            c.execute("insert INTO jonsecondp VALUES (?)", (second))
            self.tstcon.commit()
            c.execute("select * from jonsecondp")
            r = c.fetchall()[0]
            self.assertEqual(r[0], second)

    def test_datatype_interval_YEAR_TO_MONTH(self):
        with self.tstcon.cursor() as c:
            ym = "5-10"
            c.execute("create table jonytm (c1 INTERVAL YEAR(5) TO MONTH) in pybank")
            c.execute("insert INTO jonytm VALUES (?)", (ym))
            self.tstcon.commit()
            c.execute("select * from jonytm")
            r = c.fetchall()[0]
            self.assertEqual(r[0], ym)

    def test_datatype_interval_DAY_TO_HOUR(self):
        with self.tstcon.cursor() as c:
            dhms = "5 23"
            c.execute("create table jondth (c1 INTERVAL DAY(5) TO HOUR) in pybank")
            c.execute("insert INTO jondth VALUES (?)", (dhms))
            self.tstcon.commit()
            c.execute("select * from jondth")
            r = c.fetchall()[0]
            self.assertEqual(r[0], dhms)

    def test_datatype_interval_DAY_TO_MINUTE(self):
        with self.tstcon.cursor() as c:
            dhm = "5 23:55"
            c.execute("create table jondtm (c1 INTERVAL DAY(5) TO MINUTE) in pybank")
            c.execute("insert INTO jondtm VALUES (?)", (dhm))
            self.tstcon.commit()
            c.execute("select * from jondtm")
            r = c.fetchall()[0]
            self.assertEqual(r[0], dhm)

    def test_datatype_interval_DAY_TO_SECOND(self):
        with self.tstcon.cursor() as c:
            dhms = "5 23:05:01.123"
            c.execute("create table jondts (c1 INTERVAL DAY(5) TO SECOND(3)) in pybank")
            c.execute("insert INTO jondts VALUES (?)", (dhms))
            self.tstcon.commit()
            c.execute("select * from jondts")
            r = c.fetchall()[0]
            self.assertEqual(r[0], dhms)

    def test_datatype_interval_HOUR_TO_MINUTE(self):
        with self.tstcon.cursor() as c:
            hts = "55555:01"
            c.execute("create table jonhtm (c1 INTERVAL HOUR(5) TO MINUTE) in pybank")
            c.execute("insert INTO jonhtm VALUES (?)", (hts))
            self.tstcon.commit()
            c.execute("select * from jonhtm")
            r = c.fetchall()[0]
            self.assertEqual(r[0], hts)

    def test_datatype_interval_HOUR_TO_SECOND(self):
        with self.tstcon.cursor() as c:
            hts = "55555:23:02.12345"
            c.execute("create table jonhts (c1 INTERVAL HOUR(5) TO SECOND(5)) in pybank")
            c.execute("insert into jonhts values(cast(? as interval HOUR(5) to second(5)))", (hts))
            #c.execute("insert INTO jonhts VALUES (?)", (hts))
            self.tstcon.commit()
            c.execute("select * from jonhts")
            r = c.fetchall()[0]
            self.assertEqual(r[0], hts)

    def test_datatype_interval_MINUTE_TO_SECOND(self):
        with self.tstcon.cursor() as c:
            minute = '12345:12.12345679'
            c.execute("create table jonmts (c1 INTERVAL MINUTE(5) TO SECOND(8)) in pybank")
            c.execute("insert into jonmts values (?)", minute)
            self.tstcon.commit()
            c.execute("select * from jonmts")
            r = c.fetchall()
            self.assertEqual(r[0][0], minute)
            
    def test_insert_bool(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobybool (c1 boolean) in pybank")
            c.execute("insert INTO bobybool VALUES (?)", (False))
            c.execute("insert INTO bobybool VALUES (?)", (45))
            self.tstcon.commit()

    def test_select_bool(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobybool2 (c1 boolean) in pybank")
            c.execute("insert INTO bobybool2 VALUES (?)", (False))
            c.execute("insert INTO bobybool2 VALUES (?)", (45))
            self.tstcon.commit()
            c.execute("select * from bobybool2")
            r = c.fetchone()
            self.assertEqual(r[0], False)
            r = c.fetchone()
            self.assertEqual(r[0], True)

    def test_get_connection(self):
        c = self.tstcon.cursor()
        self.assertEqual(c.connection, self.tstcon)
        c.close()

    def test_for(self):
        with self.tstcon.cursor() as c:
            c.execute("create table fortable (c1 INTEGER, c2 INTEGER)"
                      " in pybank")
            c.execute("insert INTO fortable VALUES (?,?)", (1,99))
            c.execute("insert INTO fortable VALUES (?,?)", (3,97))
            c.execute("insert INTO fortable VALUES (?,?)", (10,90))
            c.execute("select * from fortable")
            count = 0
            for val in c:
                self.assertEqual(val[0]+val[1], 100)
                count = count + 1
            self.assertEqual(count, 3)

    def test_result_set_twice(self):
        with self.tstcon.cursor() as c:
            c.execute("create table kor (c1 INTEGER) in pybank")
            c.execute("insert INTO kor VALUES (?)", (45))
            c.execute("select * from kor")
            for val in c:
                self.assertEqual(val[0], 45)
            c.execute("select * from kor")
            c.execute("select c1 from kor")

    def test_executemany_none(self):
        with self.tstcon.cursor() as c:
            c.execute("create table manytable (c1 INTEGER) in pybank")
            c.executemany("insert INTO manytable VALUES (?)",
                          [(2,), (34,), (435,), (34,), (63,), (47,), (None,)])
            self.tstcon.commit()

    def test_select_executemany(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobyselect (c1 INTEGER) in pybank")
            self.tstcon.commit()
            c.execute("insert INTO bobyselect VALUES (?)", (1))
            with self.assertRaises(ProgrammingError):
                c.executemany("select * from bobyselect where c1 = (?)",
                              ((5,), (10,)))

    def test_select_twice(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bananaselect (c1 INTEGER) in pybank")
            c.execute("select * from bananaselect where c1 = (?)", (5))
            c.execute("select c1 from bananaselect where c1 = (?)", (7))

    def test_fetchall_no_select(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(ProgrammingError):
                c.fetchall()

    def test_bool_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table boolt (c1 BOOLEAN) in pybank")
            c.executemany("insert into boolt values (?)",
                          [(None,), (1,), (0,), (3.1415,),
                           ("potato",), ('code',)])
            c.execute("select * from boolt")
            r = c.fetchall()
            self.assertEqual(r, [(None,), (True,), (False,),
                                 (True,), (True,), (True,)])

    def test_insert_parametermarkers_different_types(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob176(c1 NVARCHAR(128)) in pybank")
            c.execute("INSERT INTO bob176 VALUES (?)", "bar")  # correct
            c.execute("INSERT INTO bob176 VALUES (?)", ("bar"))  # correct
            c.execute("INSERT INTO bob176 VALUES (?)", ("bar",))  # correct
            c.execute("INSERT INTO bob176 VALUES (?)", ["bar"])  # correct
            self.tstcon.commit()
            c.execute("select * from bob176")
            self.assertEqual(c.fetchall(), [("bar",), ("bar",),
                                            ("bar",), ("bar",)])

    def test_insert_parametermarkers_different_types2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bobd(c1 NVARCHAR(128), c2 INTEGER,"
                      "                  c3 FLOAT) in pybank")
            c.execute("INSERT INTO bobd VALUES (?,?,?)",
                      ("bar", 314, 41.23))
            c.execute("INSERT INTO bobd VALUES (?,?,?)",
                      ("bar", 315, 41.23,))
            with self.assertRaises(ProgrammingError):
                c.execute("INSERT INTO bobd VALUES (?,?,?)",
                          "bar", (316), (41.23))
            c.execute("INSERT INTO bobd VALUES (?,?,?)",
                      ["bar", 317, 41.23])
            self.tstcon.commit()
            c.execute("select * from bobd")
            self.assertEqual(c.fetchall(),
                             [('bar', 314, 41.23),
                              ('bar', 315, 41.23),
                              ('bar', 317, 41.23)])

    def test_char_table(self):
        with self.tstcon.cursor() as c:
            c.execute("create table charbob(c1 CHAR(10)) in pybank")
            c.execute("INSERT INTO charbob VALUES ('Kalle Kula')")
            self.tstcon.commit()
            c.execute("select * from charbob")
            self.assertEqual(c.fetchall(), [("Kalle Kula",)])

    def test_invalid_char(self):
        with self.tstcon.cursor() as c:
            c.execute("create table invalidbob(c1 CHAR(10)) in pybank")
            # kastar inget fel för tillfället, vilket är micro api's fel,
            # men inget vi ska lösa just nu
            # &&&& Fixme!
            c.execute("INSERT INTO invalidbob VALUES ('?')", ("ィキペデ"))
            with self.assertRaises(DataError):
                c.execute("INSERT INTO invalidbob VALUES ('ィキペデ')")
            self.tstcon.commit()
            c.execute("select * from invalidbob")
            r = c.fetchall()


    def test_varchar_table(self):
        with self.tstcon.cursor() as c:
            c.execute("create table varcharbob(c1 VARCHAR(128)) in pybank")
            c.execute("INSERT INTO varcharbob VALUES ('Kalle Kula')")
            self.tstcon.commit()
            c.execute("select * from varcharbob")
            self.assertEqual(c.fetchall(), [("Kalle Kula",)])

    def test_nchar_table(self):
        with self.tstcon.cursor() as c:
            c.execute("create table ncharbob(c1 VARCHAR(128)) in pybank")
            c.execute("INSERT INTO ncharbob VALUES ('Kalle Kula')")
            self.tstcon.commit()
            c.execute("select * from ncharbob")
            self.assertEqual(c.fetchall(), [("Kalle Kula",)])

    def test_callproc_nextset(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(NotSupportedError):
                c.nextset()
            with self.assertRaises(NotSupportedError):
                c.callproc()

    def test_insert_blob_2(self):
        with self.tstcon.cursor() as c:
            c.execute("CREATE TABLE blob_table (blobcolumn BLOB)")
            blob = bytes(bytearray("Hello there again", encoding ='utf-8'))
            c.execute("INSERT INTO blob_table VALUES (?)", (blob))
            self.tstcon.commit()
            c.execute("SELECT * FROM blob_table")
            r = c.fetchall()[0][0]
            self.assertEqual(r, blob)

    def test_conflict_drop(self):
        with self.tstcon.cursor() as c:
            mytuplelist = list(zip(list(range(100)), list(range(100))))
            c.execute("CREATE TABLE conflict_test2 (int1 INTEGER, int2 INTEGER)")
            c.executemany("INSERT INTO conflict_test2 VALUES (?,?)", (mytuplelist))
            self.tstcon.commit()

        conn1 = mimerpy.connect(**db_config.TSTUSR)
        conn2 = mimerpy.connect(**db_config.TSTUSR)
        conn1.execute("INSERT INTO conflict_test2 VALUES (?,?)", (200,200))
        with self.assertRaises(OperationalError) as e:
            conn2.execute("DROP TABLE conflict_test2 CASCADE")
        self.assertEqual(-16001, e.exception.errno)
        self.assertEqual("Table MIMERPY.conflict_test2 locked by another user", e.exception.message)
        conn1.close()
        conn2.close()
    
    def test_conflict_insert(self):
        with self.tstcon.cursor() as c:
            mytuplelist = list(zip(list(range(100)), list(range(100))))
            c.execute("CREATE TABLE conflict_test3 (int1 INTEGER, int2 INTEGER, PRIMARY KEY (int1))")
            c.executemany("INSERT INTO conflict_test3 VALUES (?,?)", (mytuplelist))
            self.tstcon.commit()

        conn1 = mimerpy.connect(**db_config.TSTUSR)
        conn2 = mimerpy.connect(**db_config.TSTUSR)
        mytuplelist = list(zip(list(range(200,300)), list(range(200, 300))))
        conn1.executemany("INSERT INTO conflict_test3 VALUES (?,?)", (mytuplelist))
        conn2.executemany("INSERT INTO conflict_test3 VALUES (?,?)", (mytuplelist))
        conn1.commit()
        with self.assertRaises(TransactionAbortError) as e:
            conn2.commit()
        self.assertEqual(-10001, e.exception.errno)
        self.assertEqual("Transaction aborted due to conflict with other transaction", e.exception.message)
        conn1.close()
        conn2.close()

    def test_conflict_update(self):
        with self.tstcon.cursor() as c:
            mytuplelist = list(zip(list(range(100)), list(range(100))))
            c.execute("CREATE TABLE conflict_test4 (int1 INTEGER, int2 INTEGER)")
            c.executemany("INSERT INTO conflict_test4 VALUES (?,?)", (mytuplelist))
            self.tstcon.commit()

        conn1 = mimerpy.connect(**db_config.TSTUSR)
        conn2 = mimerpy.connect(**db_config.TSTUSR)
        conn1.execute("UPDATE conflict_test4 SET int1 = 500 where int1 = 50")
        conn2.execute("UPDATE conflict_test4 SET int1 = 555 where int1 = 50")
        conn1.commit()
        with self.assertRaises(OperationalError) as e:
            conn2.commit()
        self.assertEqual(-10001, e.exception.errno)
        self.assertEqual("Transaction aborted due to conflict with other transaction", e.exception.message)
        conn1.close()
        conn2.close()

    # these are the test examples for the documentaion
    def test_for_doc_1(self):
        with self.tstcon.cursor() as c:
            c.execute("CREATE TABLE with_table_cursor1(c1 INTEGER,"
                      "                            c2 VARCHAR(32)) in pybank")
            c.execute("INSERT INTO with_table_cursor1 VALUES (?,?)",
                      (1, "This is an example"))
            c.execute("INSERT INTO with_table_cursor1 VALUES (?,?)",
                      (2, "on how to use"))
            c.execute("INSERT INTO with_table_cursor1 VALUES (?,?)",
                      (3, "the with functionality."))
        with self.tstcon.cursor() as c:
            c.execute("SELECT * from with_table_cursor1")

    # these are the test examples for the documentaion
    @unittest.skip
    def test_for_doc_2(self):
        with self.tstcon.cursor() as c:
            c.execute("CREATE TABLE with_table_connection1(c1 INTEGER,"
                             " c2 VARCHAR(32)) in pybank")
        self.tstcon.commit()

        with mimerpy.connect(**db_config.TSTUSR) as con:
            con.execute("INSERT INTO with_table_connection1 VALUES (?,?)",
                        (1, "This is an example"))
            con.execute("INSERT INTO with_table_connection1 VALUES (?,?)",
                        (2, "on how to use"))
            con.execute("INSERT INTO with_table_connection1 VALUES (?,?)",
                        (3, "the with functionality."))
            con.commit()

        with mimerpy.connect(**db_config.TSTUSR) as con:
            con.execute("INSERT INTO with_table_connection1 VALUES (?,?)",
                        (4, "Commit forgotten"))

        cred = db_config.TSTUSR.copy()
        cred['autocommit'] = True
        with mimerpy.connect(**cred) as con:
            con.execute("INSERT INTO with_table_connection1 VALUES (?,?)",
                        (5, "Autocommitted"))

        with self.tstcon.cursor() as c:
            c.execute("SELECT * from with_table_connection1")
            self.assertEqual(c.fetchall(),
                             [(1, 'This is an example'),
                              (2, 'on how to use'),
                              (3, 'the with functionality.'),
                              (5, 'Autocommitted')])

    # Inconsistent errors, needs to be fixed!
    def test_invalid_NULL(self):
        with self.tstcon.cursor() as c:
            c.execute("create table boberror (c1 INTEGER not null,"
                      "                c2 NVARCHAR(10) not null) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("insert into boberror values (:a, :b)", (None, None))
            with self.assertRaises(ProgrammingError):
                c.execute("insert into boberror values (:a, :b)", (1, None))
            with self.assertRaises(ProgrammingError):
                c.execute("insert into boberror values (:a, :b)", (None, 'Hej'))
            with self.assertRaises(DataError):
                c.execute("insert into boberror values (NULL, NULL)")

            c.execute("SELECT * from boberror")
            self.assertEqual(c.fetchall(), [])

    def test_bool_null(self):
        with self.tstcon.cursor() as c:
            c.execute("create table boolbob3 (c1 boolean)")
            c.execute("insert into boolbob3 values (?)", (None))

            c.execute("SELECT * from boolbob3")
            self.assertEqual(c.fetchone(), (None,))

    def test_unsupported_data_type(self):
        with self.tstcon.cursor() as c:
            long = """
create table longboi (c1 char(10),
                      c2 varchar(10),
                      c3 CLOB(2000),
                      c4 nchar(10),
                      c5 nvarchar(30),
                      c6 nclob(2000),
                      c7 binary(2),
                      c8 varbinary(2),
                      c9 blob(1024),
                      c10 SMALLINT,
                      c11 INTEGER,
                      c12 BIGINT,
                      c13 INTEGER(2),
                      c14 DECIMAL(5,2),
                      c15 REAL,
                      c16 DOUBLE PRECISION,
                      c17 FLOAT,
                      c18 DATE,
                      c19 TIME(0),
                      c20 TIMESTAMP(6)) in pybank"""
            c.execute(long)
            c.execute("insert into longboi (c4) values (?)", ("dude", ))

# &&&& Add values in static SQL and then try to get individual columns
# &&&& Then try to set individual columns from Python

            c.execute("SELECT * from longboi")
            self.assertEqual(c.fetchone(), (None, None, None, 'dude      ',
                                            None, None, None, None, None,
                                            None, None, None, None, None,
                                            None, None, None, None, None, None))

    def test_data_type_varbinary(self):
        with self.tstcon.cursor() as c:
            long = "create table longboi_varbinary (c1 VARBINARY(10)) in pybank"
            c.execute(long)
            c.execute("insert into longboi_varbinary values (?)", (b"x'ABCD01"))

            c.execute("SELECT * from longboi_varbinary")
            self.assertEqual(c.fetchall(), [(b"x'ABCD01",)])

    def test_data_type_smallint(self):
        with self.tstcon.cursor() as c:
            long = "create table longboi_smallint (c1 SMALLINT) in pybank"
            c.execute(long)
            c.execute("insert into longboi_smallint values (?)", (32000))

            c.execute("SELECT * from longboi_smallint")
            self.assertEqual(c.fetchall(), [(32000,)])

    def test_data_type_bigint(self):
        with self.tstcon.cursor() as c:
            long = "create table longboi_bigint(c1 BIGINT) in pybank"
            c.execute(long)
            c.execute("insert into longboi_bigint values (?)", (-2**63))

            c.execute("SELECT * from longboi_bigint")
            self.assertEqual(c.fetchall(), [(-2**63,)])

    @unittest.skip
    def test_data_type_precision_integer(self):
        with self.tstcon.cursor() as c:
            long = "create table longboi_integer45(c1 INTEGER(45)) in pybank"
            c.execute(long)
            c.execute("insert into longboi_integer45 values (?)", str(2**145))

            c.execute("SELECT * from longboi_integer45")
            self.assertEqual(c.fetchall(), [(str(2**140),)])

    def test_parameter_name(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_name (c1 boolean,c2 nchar(10),"
                      "                       c3 int) in pybank")
            c.execute("insert into bob_name (c1,c3) values (:a,:b)",
                      {'a':True, 'b':3})

            c.execute("SELECT * from bob_name")
            self.assertEqual(c.fetchone(), (True, None, 3))

    def test_error_message(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_message (c1 nchar(10)) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("insert into bob_message (c1,c3) values (:a,:b)",
                        {'a':2,})
            print()
            self.assertEqual(c.messages[0][1], (-12202, 'c3 is not a column of an inserted table, updated table or any table identified in a FROM clause'))

    def test_error_exception_errno(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_message_1 (c1 nchar(10)) in pybank")
            with self.assertRaises(ProgrammingError) as e:
                c.execute("insert into bob_message_1 (c1,c3) values (:a,:b)",
                        {'a':2,})
            self.assertEqual(e.exception.errno, -12202)
    
    def test_error_exception_message(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_message_2 (c1 nchar(10)) in pybank")
            with self.assertRaises(ProgrammingError) as e:
                c.execute("insert into bob_message_2 (c1,c3) values (:a,:b)",
                        {'a':2,})
            self.assertEqual(e.exception.message, "c3 is not a column of an inserted table, updated table or any table identified in a FROM clause")
    
    def test_error_exception_str(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_message_3 (c1 nchar(10)) in pybank")
            with self.assertRaises(ProgrammingError) as e:
                c.execute("insert into bob_message_3 (c1,c3) values (:a,:b)",
                        {'a':2,})
            self.assertEqual(str(e.exception), "-12202 c3 is not a column of an inserted table, updated table or any table identified in a FROM clause")

    def test_parameter_name_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_name_2(c1 boolean, c2 nchar(10),"
                      "                        c3 int) in pybank")
            c.execute("insert into bob_name_2 (c1,c3,c2) values (:a,:b,:g)",
                      dict(a=True, b=3, g="bobs table"))

            c.execute("SELECT * from bob_name_2")
            self.assertEqual(c.fetchone(), (True, "bobs table", 3))

    def test_parameter_name_missing_key(self):
        with self.tstcon.cursor() as c:
            c.execute("create table pname_miss(c1 boolean,c2 nchar(10),"
                      "                        c3 int) in pybank")
            with self.assertRaises(ProgrammingError):
                c.execute("insert into pname_miss(c1,c2) values (:a,:b)",
                          {'a':True, 'g':3})

    def test_parameter_name_execute_many(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_name_e(c1 boolean,c2 nchar(10),"
                      "                        c3 int) in pybank")
            c.executemany("insert into bob_name_e(c1,c3) values (:a,:b)",
                          [{'a':True, 'b':1},
                           {'a':False, 'b':2},
                           {'a':True, 'b':3}])

            c.execute("SELECT * from bob_name_e")
            self.assertEqual(c.fetchall(),
                             [(True, None, 1),
                              (False, None, 2),
                              (True, None, 3)])

    def test_parameter_name_execute_many_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table pname__e2 (c1 boolean,c2 nchar(10),"
                      "                        c3 int) in pybank")
            c.executemany("insert into pname__e2 (c1,c3,c2) values (:a,:b,:g)",
                          [{'a': True, 'b': 1, 'g': "bob table1"},
                           {'a': False, 'b': 2, 'g': "bob table2"},
                           {'a': True, 'b': 3, 'g': "bob table3"}])
            c.execute("SELECT * from pname__e2")
            self.assertEqual(c.fetchall(),
                             [(True, 'bob table1', 1),
                              (False, 'bob table2', 2),
                              (True, 'bob table3', 3)])

    def test_parameter_name_execute_many_invalid_key(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_name_invalid(c1 boolean,c2 nchar(10),"
                      "                              c3 int) in pybank")
            with self.assertRaises(ProgrammingError):
                c.executemany("insert into bob_name_invalid (c1,c2)"
                              " values (:a,:b)",
                              [{'a':True, 'g':3},
                               {'a':True, 'g':3}])

    def test_parameter_name_execute_many_mixing(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_name__e3 (c1 boolean,c2 nvarchar(10),"
                      "                           c3 int) in pybank")
            c.executemany("insert into bob_name__e3 (c1,c2,c3)"
                          " values (:a,:b,:g)",
                          [{'a': True, 'g': 1, 'b': "bob table1"},
                           (True, "string ?", 5),
                           (True, "string", 5)])
            c.execute("SELECT * from bob_name__e3")
            self.assertEqual(c.fetchall(),
                             [(True, 'bob table1', 1),
                              (True, 'string ?', 5),
                              (True, 'string', 5)])

    def test_parameter_name_execute_many_mixing_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob_name__e4 (c1 boolean,c2 nvarchar(10),"
                      "                           c3 int) in pybank")
            c.executemany("insert into bob_name__e4 (c1,c3,c2)"
                          " values (:a,:b,:g)",
                          [(True, 5,"string"),
                           {'a': True, 'b': 1, 'g': "bob table1"},
                           (True, 5, "string ?")])
            c.execute("SELECT * from bob_name__e4")
            self.assertEqual(c.fetchall(),
                             [(True, 'string', 5),
                              (True, 'bob table1', 1),
                              (True, 'string ?', 5)])

    @unittest.skip
    def test_help(self):
        a = mimerpy.connect(dsn=self.dbName, user=self.usrName, password=self.psw)
        b = a.cursor()
        help(b)
        b.close()
        a.close()

    @unittest.skip
    def test_error(self):
        a = mimerpy.connect(dsn=self.dbName, user=self.usrName, password=self.psw)
        b = a.cursor()
        b.execute("create table boberror (c1 INTEGER,  c2 NVARCHAR(10)) in pybank")
        print("table created --------------- ")
        b.execute("insert into boberror values (:a, :b)", (3, 'bob'))
        a.close()


    if (mimerapi._level == 2):
        def test_datatype_float_p(self):
            with self.tstcon.cursor() as c:
                c.execute("create table floatptable (c1 FLOAT(5)) in pybank")
                floatnum = str(3.123)
                c.execute("insert INTO floatptable VALUES (?)", (floatnum))
                self.tstcon.commit()
                c.execute("select * from floatptable")
                r = c.fetchall()[0]
                self.assertEqual(r[0], decimal.Decimal(floatnum))

        def test_datatype_numeric(self):
            with self.tstcon.cursor() as c:
                c.execute("create table floatnumericptable (c1 numeric(5,2)) in pybank")
                floatnum = str(322.13)
                c.execute("insert INTO floatnumericptable VALUES (?)", (floatnum))
                self.tstcon.commit()
                c.execute("select * from floatnumericptable")
                r = c.fetchall()[0]
                self.assertEqual(r[0], decimal.Decimal(floatnum))

        @unittest.skipUnless(db_config.MIMERPY_STABLE == False, "Currently gives incorrect error message")
        def test_insert_decimal_invalid(self):
            with self.tstcon.cursor() as c:
                c.execute("create table jondecimal2 (c1 DECIMAL(5,2)) in pybank")
                floatnum = '32423.23234'
                #with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jondecimal2 VALUES (?)", (floatnum))


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
