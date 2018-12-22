import unittest
import time
import math
import mimerpy

from mimerpy.mimPyExceptions import *
import db_config


# noinspection SqlDialectInspection
class TestCursorMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.syscon, self.tstcon) = db_config.setup()

    @classmethod
    def tearDownClass(self):
        self.tstcon.close()
        with self.syscon.cursor() as c:
            c.execute("DROP IDENT MIMERPY CASCADE")
        self.syscon.commit()
        self.syscon.close()

    def tearDown(self):
        self.tstcon.rollback()

########################################################################
## Tests below
########################################################################

    def test_privilege(self):
        with self.tstcon.cursor() as c:
            with self.assertRaises(DatabaseError):
                c.execute("create ident gurra as user using '123'")

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
            #print(c.description)
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
            c.executemany("insert into bob13 values (:a, :b, :c)",
                          ((1, 'pi', 14.345),
                           (2, 'pii', 14.345),
                           (-3, 'piii', 14.345),
                           (7, 'piii', 14.345),
                           (1121231, 'piiii', 14.345)))
            self.tstcon.commit()
            ## &&&& Fetch and test result?

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
            with self.assertRaises(InterfaceError):
                c.executemany("insert into bob4 values (:a)", [(1)])
            with self.assertRaises(InterfaceError):
                c.executemany("insert into bob4 values (:a)", (1))
            with self.assertRaises(InterfaceError):
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

    ### &&&& Vad exakt testas nedan?
    def test_commit(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob7d (c1 INTEGER, c2 NVARCHAR(10))"
                      " in pybank")
            c.executemany("insert into bob7d values (:a, :b)",
                          ((1, 'bob1'), (2, 'bob2'),
                           (3, 'bob3')))

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
## &&&& Fixme: The following should work !?!
##            self.assertEqual(c.fetchmany(2), [(11, 'bob11')])

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


    @unittest.skip
    def test_fetchall_correct_number_of_rows3(self):
        with self.tstcon.cursor() as c:
            c.execute("create table bob103(c1 INTEGER, c2 NVARCHAR(100),"
                      "                    c3 FLOAT) in pybank")
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
            with self.assertRaises(ProgrammingError):
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
                c.execute("create table bob6566(c1 INTEGER) in pybank")
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

    # Not 100% sure if InterfaceError is the correct error to be raised here
    def test_executemany_DDL(self):
        with self.tstcon.cursor() as c:
            # Currently not throwing any exception
            with self.assertRaises(InterfaceError):
                b = c.executemany("create table bob6(c1 INTEGER) in pybank",
                                  (3))

    def test_insert_exceeded(self):
        with self.tstcon.cursor() as c:
            b = c.execute("create table bob16(c1 BIGINT) in pybank")
            big = pow(2, 100)
            with self.assertRaises(ProgrammingError):
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
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jon31 VALUES (?)", (nvar))

    def test_invalid_int32_insert_too_big(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon33 (c1 INTEGER) in pybank")
            var = 2 ** 31
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jon33 VALUES (?)", (var))

    def test_valid_int64_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon64 (c1 BIGINT, c2 BIGINT) in pybank")
            nvar = -2 ** 63
            var = 2 ** 63 - 1
            c.execute("insert INTO jon64 VALUES (?,?)", (nvar, var))

    def test_overflow_int64_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table intjon4 (c1 BIGINT, c2 BIGINT) in pybank")
            nvar = -2 ** 633
            var = 2 ** 63 - 1
            with self.assertRaises(ProgrammingError):
                c.executemany("insert INTO intjon4 VALUES (?,?)",
                              ((nvar, var), (nvar, var)))

    def test_invalid_int64_insert_too_small(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon63 (c1 BIGINT) in pybank")
            nvar = -2 ** 63 - 1
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jon63 VALUES (?)", (nvar))

    def test_invalid_int64_insert_too_big(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon65 (c1 BIGINT) in pybank")
            var = 2 ** 63
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jon65 VALUES (?)", (var))

    def test_valid_int16_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon26 (c1 SMALLINT, c2 SMALLINT) in pybank")
            nvar = -2 ** 15
            var = 2 ** 15 - 1
            c.execute("insert INTO jon26 VALUES (?, ?)", (nvar, var))

    def test_invalid_int16_insert_too_small(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon15 (c1 SMALLINT) in pybank")
            nvar = -2 ** 15 - 1
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jon15 VALUES (?)", (nvar))

    def test_invalid_int16_insert_too_small(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon17 (c1 SMALLINT) in pybank")
            nvar = 2 ** 15
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jon17 VALUES (?)", (nvar))

    # &&&& Gives a Warning we dont catch atm
    def test_valid_double_insert(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon16 (c1 REAL, c2 DOUBLE PRECISION)"
                      " in pybank")
            var = 2 / 3
            c.execute("insert INTO jon16 VALUES (?, ?)", (var, var))
            self.tstcon.commit()

    # &&&& Works now, I will have to look at how the test looked in older version - Erik 2018-08
    # @unittest.skip
    def test_invalid_double_insert(self):
        b = self.tstcon.cursor()
        c = self.tstcon.cursor()
        d = self.tstcon.cursor()
        e = self.tstcon.cursor()
        f = self.tstcon.cursor()
        b.execute("create table jondd (c1 FLOAT) in pybank")
        var = 10 ** 309
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jondd VALUES (?)", (var))

        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jondd VALUES (?, ?)", (-var, -var))

        b.close()

    def test_valid_double_insert_none(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jon18 (c1 REAL, c2 DOUBLE PRECISION)"
                      " in pybank")
            var = None
            c.execute("insert INTO jon18 VALUES (?, ?)", (var, var))
            self.tstcon.commit()
            ### &&&& Should fetch and check result

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
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jonwas17 VALUES (?)", (nvar))
            c.execute("insert INTO jonwas17 VALUES (?)", (5))
            self.assertEqual(c.messages, [])

    def test_message_cleared_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonwas173 (c1 SMALLINT) in pybank")
            nvar = 2 ** 15
            with self.assertRaises(ProgrammingError):
                c.execute("insert INTO jonwas173 VALUES (?)", (nvar))
            self.assertEqual(c.messages[0][1], 'MicroAPI error -24010')

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
        # a1.commit()
        # a2.commit()
        # b3 = a2.cursor()
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
            # self.tstcon.commit()
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
    # &&&& need to find a picture to put in the repo
    # Nä, gör en psudorandom-blob
    def test_insert_blob(self):
        with self.tstcon.cursor() as c:
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
        with self.tstcon.cursor() as c:
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
        with self.tstcon.cursor() as c:
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
        with self.tstcon.cursor() as c:
            c.execute("create table jonblob4 (c1 BLOB(3000000)) in pybank")
            with open("../kappa.jpg", 'rb') as input_file:
                ablob = input_file.read()
                c.execute("insert INTO jonblob4 VALUES (?)", (ablob))
                self.tstcon.commit()
                c.execute("select * from jonblob4")
                r = c.fetchall()[0][0]
            self.assertEqual(r, ablob)

    # Bug in mimerAPI - Erik 2018-08
    # Still there?? &&&&
    def test_insert_nclob(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonnclob (c1 NCLOB(50000)) in pybank")
            anclob = "mimer" * 1000
            c.execute("insert INTO jonnclob VALUES (?)", (anclob))
            self.tstcon.commit()
            c.execute("select * from jonnclob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], anclob)

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
            bob = "0x53"
            c.execute("insert INTO jonbinary2 VALUES (?)", (bob))
            self.tstcon.commit()
            c.execute("select * from jonbinary2")
            r = c.fetchall()[0]
            self.assertEqual(r[0], b'0x53')

    @unittest.skip
    # &&&& need to find a picture to put in the repo
    # Nä, gör en psudorandom-blob
    def test_insert_nclob_2(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonnclob2 (c1 Nclob(450000)) in pybank")
            with open("../book2.txt", "r") as input_file:
                anclob = input_file.read()
                c.execute("insert INTO jonnclob2 VALUES (?)", (anclob))
                self.tstcon.commit()
                c.execute("select * from jonnclob2")
                r = c.fetchall()[0]
                self.assertEqual(r[0], anclob)

    def test_insert_clob(self):
        with self.tstcon.cursor() as c:
            c.execute("create table jonclob (c1 clob(30000)) in pybank")
            aclob = "mimer" * 5
            c.execute("insert INTO jonclob VALUES (?)", (aclob))
            self.tstcon.commit()
            c.execute("select * from jonclob")
            r = c.fetchall()[0]
            self.assertEqual(r[0], aclob)

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
            #print(r)

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

    # Blob's not working??? 2017-12-22
    #  &&&& ?
    @unittest.skip
    def test_test_test(self):
        with self.tstcon.cursor() as c:
            c.execute("CREATE TABLE blob_table (blobcolumn BLOB)")

            # reading from the .jpg file in binary mode
            with open("../sphinx/mimerhd.png", 'rb') as input_file:
                insert_blob = input_file.read()
            c.execute("INSERT INTO blob_table VALUES (?)", (insert_blob))

            # committing and closing the cursor and connection
            self.tstcon.commit()
            c.execute("SELECT * FROM blob_table")
            self.assertEqual(c.fetchall()[0], (insert_blob,))

    def test_test_test2(self):
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
    def test_test_test3(self):
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
            c.execute("insert into longboi_varbinary values (?)", ("x'ABCD01"))

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
            c.execute("insert into longboi_integer45 values (?)", (str(2**140)))

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


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
