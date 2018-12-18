import unittest
import time
import math
import mimerpy

from mimerpy.mimPyExceptions import *
import db_config

class TestScrollCursorMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.dbName = db_config.DB_INFO['DBNAME']
        self.usrName = "TEST_IDENT"
        self.psw = "mimerPass"
        self.sysadmName = db_config.DB_INFO['SYSADM']
        self.sysadmpsw = db_config.DB_INFO['SYADMPSW']
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor(scrollable = 'True')
        b.execute("CREATE IDENT TEST_IDENT AS USER USING 'mimerPass'")
        b.execute("create databank testbank")
        b.execute("Grant TABLE on databank testbank to TEST_IDENT")

    @classmethod
    def tearDownClass(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor(scrollable = 'True')
        b.execute("DROP DATABANK testbank CASCADE")
        b.execute("DROP IDENT TEST_IDENT CASCADE")
        b.close()
        a.commit()
        a.close()

    def test_createTable(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

    def test_createTable_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobcr1(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.execute("create table bobcr2(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.execute("create table bobcr3(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.execute("create table bobcr4(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

    def test_createTable_DropTable(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob2(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.execute("drop table bob2 CASCADE")
        a.close()

    def test_create_invalid_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon (c1 INTEGER, c2 INTEGER) in testbank")
        with self.assertRaises(ProgrammingError):
            b.execute("banana INTO jon VALUES (3, 14)")
        a.close()

    def test_create_rollback_table(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonnynothere (c1 INTEGER, c2 INTEGER) in testbank")
        a.rollback()
        b.execute("select * from jonnynothere")
        a.close()

    def test_two_select(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonny (c1 INTEGER, c2 INTEGER) in testbank")
        b.execute("select c1 from jonny where c1 = (?)",(2))
        b.execute("select * from jonny")
        a.close()

    def test_many_select(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob356 (c1 INTEGER) in testbank")
        for val in range(100):
            b.execute("insert into bob356 values (:a)", (val))
        for gal in range(100):
            b.execute("select c1 from bob356 where c1 > (?)",(gal))
        a.close()

    def test_select_no_commit(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobc (c1 INTEGER, c2 FLOAT) in testbank")
        for val in range(100):
            b.execute("insert into bobc values (:a, :b)", (val, val + 0.5))
        b.execute("select * from bobc where c1 = 99")
        self.assertEqual(b.fetchall(),[(99,99.5)])
        a.close()

    def test_select_description(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table description (columnone INTEGER) in testbank")
        for val in range(10):
            b.execute("insert into description values (?)", val)
        b.execute("select * from description")
        self.assertEqual(b.description, (('columnone', 50, None, None, None, None, None),))
        a.close()

    def test_select_description2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table description2 (c1 INTEGER, c2 FLOAT) in testbank")
        for val in range(10):
            b.execute("insert into description2 values (?,?)", (val, val/3))
        b.execute("select * from description2")
        self.assertEqual(b.description, (('c1', 50, None, None, None, None, None),
                                        ('c2', 56, None, None, None, None, None)))
        b.execute("select c1 from description2")
        self.assertEqual(b.description, (('c1', 50, None, None, None, None, None),))
        b.execute("select c2 from description2")
        self.assertEqual(b.description, (('c2', 56, None, None, None, None, None),))
        b.execute("select * from description2")
        self.assertEqual(b.description, (('c1', 50, None, None, None, None, None),
                                        ('c2', 56, None, None, None, None, None)))
        a.close()

    def test_select_description3(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table description3 (price INTEGER, currentvalue FLOAT, currency NVARCHAR(128),rate BIGINT, currentyear INTEGER) in testbank")
        for val in range(10):
            b.execute("insert into description3 values (?,?,?,?,?)", (val, val/3, 'SEK', 2**61, val+2000))
        b.execute("select * from description3")
        self.assertEqual(b.description, (('price', 50, None, None, None, None, None),
                                        ('currentvalue', 56, None, None, None, None, None),
                                        ('currency', 63, None, None, None, None, None),
                                        ('rate', 52, None, None, None, None, None),
                                        ('currentyear', 50, None, None, None, None, None)))
        b.execute("select price, currentyear, currency, rate from description3")
        self.assertEqual(b.description, (('price', 50, None, None, None, None, None),
                                        ('currentyear', 50, None, None, None, None, None),
                                        ('currency', 63, None, None, None, None, None),
                                        ('rate', 52, None, None, None, None, None)))
        b.execute("select rate, rate, rate, rate from description3")
        self.assertEqual(b.description, (('rate', 52, None, None, None, None, None),
                                        ('rate', 52, None, None, None, None, None),
                                        ('rate', 52, None, None, None, None, None),
                                        ('rate', 52, None, None, None, None, None)))
        b.execute("select * from description3")
        self.assertEqual(b.description, (('price', 50, None, None, None, None, None),
                                        ('currentvalue', 56, None, None, None, None, None),
                                        ('currency', 63, None, None, None, None, None),
                                        ('rate', 52, None, None, None, None, None),
                                        ('currentyear', 50, None, None, None, None, None)))

    def test_select_description4(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        name1 = "e"*127+"q"
        name2 = "m"*127+"q"
        query = "create table description4 (" + name1 + " INTEGER, " + name2 + " BOOLEAN) in testbank"
        b.execute(query)
        for val in range(10):
            b.execute("insert into description4 values (?,?)", (val,val%2))
        b.execute("select * from description4")
        self.assertEqual(b.description, ((name1, 50, None, None, None, None, None),
                                        (name2, 42, None, None, None, None, None)))

    def test_select_description5(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        name1 = "e"*127+"q"
        name2 = "m"*127+"q"
        query = "create table description5 (" + name1 + " INTEGER, " + name2 + " BOOLEAN) in testbank"
        b.execute(query)
        for val in range(10):
            b.execute("insert into description5 values (?,?)", (val,val%2))
        b.execute("select * from description5")
        self.assertEqual(b.description, ((name1, 50, None, None, None, None, None),
                                        (name2, 42, None, None, None, None, None)))

    def test_invalid_create(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("creat table jon")
        a.close()

    def test_insert_parametermarkers(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob1 (c1 INTEGER,  c2 NVARCHAR(10)) in testbank")
        b.execute("insert into bob1 values (:a, :b)", (3, 'bob'))
        a.close()

    def test_insert_parametermarkers_longs_string(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobstring (c1 INTEGER,  c2 NVARCHAR(256)) in testbank")
        string = "mimer" * 40
        b.execute("insert into bobstring values (:a, :b)", (3, string))
        a.commit()
        b.execute("select c2 from bobstring")
        b.fetchall()
        a.close()

    def test_insert_parametermarkers_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob13 (c1 INTEGER, c2 NVARCHAR(10), c3 FLOAT) in testbank")
        a.commit()
        b.executemany("insert into bob13 values (:a, :b, :c)", ((1,'pi',14.345),(2,'pii',14.345),(-3,'piii',14.345),(7,'piii',14.345),(1121231,'piiii',14.345)))
        a.commit()
        a.close()

    def test_insert_parametermarkers_russian(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob14 (c1 INTEGER, c2 NVARCHAR(128), c3 FLOAT) in testbank")
        a.commit()
        b.executemany("insert into bob14 values (:a, :b, :c)", ((1,'продиктованной ангелом',14.345),(2,'安排他們參',14.345)))
        a.commit()
        b.execute("select * from bob14")
        self.assertEqual(b.fetchall(), [(1,'продиктованной ангелом',14.345),(2,'安排他們參',14.345)])
        a.close()


    def test_insert_parametermarkers_unicode(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table boby14 (c1 INTEGER, c2 NVARCHAR(128), c3 FLOAT) in testbank")
        a.commit()
        b.executemany("insert into boby14 values (:a, :b, :c)", ((1,'продиктованной ангелом',14.345),(2,'安排他們參‱',14.345)))
        a.commit()
        b.execute("select * from boby14")
        self.assertEqual(b.fetchall(), [(1,'продиктованной ангелом',14.345),(2,'安排他們參‱',14.345)])
        a.close()

    def test_insert_parametermarkers_too_long(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob15 (c1 NVARCHAR(10)) in testbank")
        a.commit()
        with self.assertRaises(DatabaseError):
            b.execute("insert into bob15 values (:a)", ('This sentence is too long'))
        a.commit()
        a.close()

    def test_insert_too_few_parametermarkers(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob3 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        with self.assertRaises(DatabaseError):
            b.execute("insert into bob3 values (:a, :b)", (3))
        a.close()

    def test_insert_too_many_parametermarkers(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob33 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        with self.assertRaises(ProgrammingError):
            b.executemany("insert into bob33 values (:a, :b)", ((3,'pi',14),(3)))
        a.close()

    def test_insert_many_times(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob34(c1 INTEGER, c2 NVARCHAR(10), c3 FLOAT) in testbank")
        for c in range(0, 101):
            b.execute("insert into bob34 values (5,'ウィキペディ', 4.4543543)")
        a.close()

    def test_executemany_one_value(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob4 (c1 INTEGER) in testbank")
        b.executemany("insert into bob4 values (:a)", [(1,)])
        with self.assertRaises(InterfaceError):
            b.executemany("insert into bob4 values (:a)", [(1)])
        with self.assertRaises(InterfaceError):
            b.executemany("insert into bob4 values (:a)", (1))
        with self.assertRaises(InterfaceError):
            b.executemany("insert into bob4 values (:a)", [1])
        b.close()
        a.close()

    def test_executemany_one_tuple(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob5 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.executemany("insert into bob5 values (:a, :b)", ((1,'bob1'),))
        b.close()
        a.close()

    def test_executemany_several_tuples(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobe6 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.executemany("insert into bobe6 values (:a, :b)", [(1,'bob1'), (2, 'bob2'),
                                                (3,'bob3')])
        b.close()
        a.close()

    def test_commit(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob7 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.executemany("insert into bob7 values (:a, :b)", ((1,'bob1'), (2, 'bob2'),
                                                (3,'bob3')))
        a.commit()
        a.close()

    def test_fetchone(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob8 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("insert into bob8 values (:a, :b)", (8, 'bob'))
        a.commit()
        b.execute("select * from bob8")
        self.assertEqual(b.fetchone(), (8, 'bob'))
        a.close()

    def test_fetchmany(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob9 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.executemany("insert into bob9 values (:a, :b)", ((9, 'bob9'), (10, 'bob10'),
                                            (11, 'bob11')))
        a.commit()
        b.execute("select * from bob9")
        self.assertEqual(b.fetchmany(3), [(9, 'bob9'), (10, 'bob10'), (11, 'bob11')])
        a.close()

    def test_fetchmany_too_many(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob11 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.executemany("insert into bob11 values (:a, :b)", ((9, 'bob9'), (10, 'bob10'),
                                            (11, 'bob11')))
        a.commit()
        b.execute("select * from bob11")
        self.assertEqual(b.fetchmany(5), [(9, 'bob9'), (10, 'bob10'), (11, 'bob11')])
        a.close()

    def test_fetchmany_notall(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob12 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.executemany("insert into bob12 values (:a, :b)", ((9, 'bob9'), (10, 'bob10'),
                                            (11, 'bob11')))
        a.commit()
        b.execute("select * from bob12")
        self.assertEqual(b.fetchmany(2), [(9, 'bob9'), (10, 'bob10')])
        a.close()


    def test_fetchall(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob10 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.executemany("insert into bob10 values (:a, :b)", ((10, 'bob10'),
                                            (11, 'bob11'), (12, 'bob12'),))
        a.commit()
        b.execute("select * from bob10")
        self.assertEqual(b.fetchall(), [(10, 'bob10'),(11, 'bob11'), (12, 'bob12')])
        a.close()

    def test_fetchall_correct_number_of_rows(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob101(c1 INTEGER, c2 NVARCHAR(100), c3 FLOAT) in testbank")
        a.close()
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        for c in range(1, 101):
            b.execute("insert into bob101 values (5,'ウィキペディ', 4.4543543)")
        a.commit()
        b.execute("select * from bob101")
        c = b.fetchall()
        self.assertEqual(len(c), 100)
        b.close()
        a.close()

    def test_fetchall_correct_number_of_rows2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob102(c1 INTEGER, c2 NVARCHAR(100), c3 FLOAT) in testbank")
        a.close()
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        for c in range(1, 101):
            b.execute("insert into bob102 values (5,'ウィキペディ', 4.4543543)")
        a.rollback()
        b.execute("select * from bob102")
        c = b.fetchall()
        self.assertEqual(len(c), 0)
        b.close()
        a.close()

    def test_use_next(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobnext(c1 INTEGER) in testbank")
        for c in range(0, 10):
            b.execute("insert into bobnext values (?)", c)
        a.commit()
        b.execute("select * from bobnext")
        for c in range(0,10):
            val = b.next()
            self.assertEqual(val, (c,))
        b.close()
        a.close()

    def test_use_next_StopIteration(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobstop(c1 INTEGER) in testbank")
        for c in range(0, 10):
            b.execute("insert into bobstop values (?)", c)
        a.commit()
        b.execute("select * from bobstop")
        for c in range(0,10):
            b.next()
        with self.assertRaises(StopIteration):
            b.next()
        b.close()
        a.close()

    def test_insert_wrong_type_parametermarkers(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob1337 (c1 INTEGER, c2 INTEGER) in testbank")
        with self.assertRaises(ProgrammingError):
            b.execute("insert into bob1337  values (:a, :b)", (3, 3.14))
        a.close()

    def test_operate_after_closed(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("select * from jon")
        a.close()

    def test_operate_after_closed_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
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
        a.close()

    def test_invalide_select(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        with self.assertRaises(ProgrammingError):
            b.execute("select * from jonisnotatablejo where c1 = ?", (5))
        a.close()

    def test_same_table_twice(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob2437(c1 INTEGER) in testbank")
        with self.assertRaises(ProgrammingError):
            b.execute("create table bob2437(c1 INTEGER) in testbank")
        a.close()

    def test_invalid_sequence_select(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob6565(c1 INTEGER) in testbank")
        a.commit()
        b.execute("select * from bob6565")
        c = b.fetchone()
        with self.assertRaises(ProgrammingError):
            b.execute("create table bob6569(c1 INTEGER) in testbank")
        a.rollback()
        a.close()

    #borde bli fel men blir rätt....
    def test_invalid_sequence_select_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob555(c1 INTEGER) in testbank")
        a.commit()
        b.execute("select * from bob555")
        with self.assertRaises(ProgrammingError):
            b.execute("create table bob556(c1 INTEGER) in testbank")
        a.rollback()
        b.execute("create table bob556(c1 INTEGER) in testbank")
        b.execute("insert into bob556 values (3)")
        b.execute("select * from bob556")
        self.assertEqual(b.fetchone(), (3,))
        a.close()

    def test_invalid_sequence_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob6567(c1 INTEGER) in testbank")
        a.commit()
        b.execute("insert into bob6567 values (3)")
        with self.assertRaises(ProgrammingError):
            b.execute("create table bob6566(c1 INTEGER) in testbank")
        a.rollback()
        a.close()

    def test_invalid_sequence_insert_parametermarkers(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob6568(c1 INTEGER) in testbank")
        a.commit()
        b.execute("insert into bob6568 values (?)", (3))
        with self.assertRaises(ProgrammingError):
            b.execute("create table bob6566(c1 INTEGER) in testbank")
        a.rollback()
        a.close()

    def test_executemany_DDL(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        with self.assertRaises(InterfaceError):
            b = a.executemany("create table bob6(c1 INTEGER) in testbank", (3))
        a.close()

    def test_insert_exceeded(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob16(c1 INTEGER) in testbank")
        big = pow(2,100)
        with self.assertRaises(ProgrammingError):
            b.execute("insert into bob16 values (?)", big)
        a.close()

    def test_insert_too_long(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob17(c1 NVARCHAR(10)) in testbank")
        a.commit()
        with self.assertRaises(DataError):
            b.execute("insert into bob17 values ('ウィキペデBobWasAYoungBoy')")
        a.commit()
        b.close()
        a.close()

    def test_valid_int32_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon32 (c1 INTEGER, c2 INTEGER) in testbank")
        nvar = -2**31
        var = 2**31 - 1
        b.execute("insert INTO jon32 VALUES (?, ?)", (nvar, var))
        a.close()

    def test_invalid_int32_insert_too_small(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon31 (c1 INTEGER) in testbank")
        nvar = -2**31 - 1
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jon31 VALUES (?)", (nvar))
        a.close()

    def test_invalid_int32_insert_too_big(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon33 (c1 INTEGER) in testbank")
        var = 2**31
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jon33 VALUES (?)", (var))
        a.close()

    def test_valid_int64_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon64 (c1 BIGINT, c2 BIGINT) in testbank")
        nvar = -2**63
        var = 2**63 - 1
        b.execute("insert INTO jon64 VALUES (?,?)", (nvar,var))
        a.close()

    def test_overflow_int64_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table intjon4 (c1 BIGINT, c2 BIGINT) in testbank")
        nvar = -2**633
        var = 2**63 - 1
        with self.assertRaises(ProgrammingError):
            b.executemany("insert INTO intjon4 VALUES (?,?)", ((nvar,var),(nvar,var)))
        a.close()

    def test_invalid_int64_insert_too_small(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon63 (c1 BIGINT) in testbank")
        nvar = -2**63 - 1
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jon63 VALUES (?)", (nvar))
        a.close()

    def test_invalid_int64_insert_too_big(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon65 (c1 BIGINT) in testbank")
        var = 2**63
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jon65 VALUES (?)", (var))
        a.close()

    def test_valid_int16_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon26 (c1 SMALLINT, c2 SMALLINT) in testbank")
        nvar = -2**15
        var = 2**15 - 1
        b.execute("insert INTO jon26 VALUES (?, ?)", (nvar, var))
        a.close()

    def test_invalid_int16_insert_too_small(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon15 (c1 SMALLINT) in testbank")
        nvar = -2**15 - 1
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jon15 VALUES (?)", (nvar))
        a.close()

    def test_invalid_int16_insert_too_small(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon17 (c1 SMALLINT) in testbank")
        nvar = 2**15
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jon17 VALUES (?)", (nvar))
        a.close()

    # Gives a Warning we dont catch atm
    def test_valid_double_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon16 (c1 REAL, c2 DOUBLE PRECISION) in testbank")
        var = 2/3
        b.execute("insert INTO jon16 VALUES (?, ?)", (var, var))
        a.commit()
        a.close()

    def test_valid_double_insert_none(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon18 (c1 REAL, c2 DOUBLE PRECISION) in testbank")
        var = None
        b.execute("insert INTO jon18 VALUES (?, ?)", (var, var))
        a.commit()
        a.close()

    def test_valid_double_select_none(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jon19 (c1 REAL, c2 DOUBLE PRECISION) in testbank")
        var = None
        b.execute("insert INTO jon19 VALUES (?, ?)", (var, var))
        a.commit()
        b.execute("select * from jon19")
        self.assertEqual(b.fetchall(),[(None, None)])
        a.close()

    def test_message_cleared(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonwas17 (c1 SMALLINT) in testbank")
        nvar = 2**15
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jonwas17 VALUES (?)", (nvar))
        b.execute("insert INTO jonwas17 VALUES (?)", (5))
        self.assertEqual(b.messages, [])
        a.close()

    def test_message_cleared_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonwas173 (c1 SMALLINT) in testbank")
        nvar = 2**15
        with self.assertRaises(ProgrammingError):
            b.execute("insert INTO jonwas173 VALUES (?)", (nvar))
        self.assertEqual(b.messages[0][1], 'MicroAPI error -24010')
        a.close()

    def test_None_is_returned(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonNone (c1 INTEGER) in testbank")
        for c in range(1,10):
            b.execute("Insert INTO jonNone VALUES (?)", (c))
        a.commit()
        b.execute("SELECT * from jonNone")
        for c in range(1,10):
            b.fetchone()
        self.assertEqual(b.fetchone(), [])
        a.close()

    def test_empty_sequence_is_returned_many(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonEmpty (c1 INTEGER) in testbank")
        for c in range(1,10):
            b.execute("Insert INTO jonEmpty VALUES (?)", (c))
        a.commit()
        b.execute("SELECT * from jonEmpty")
        b.fetchmany(10)
        self.assertEqual(b.fetchmany(10), [])
        a.close()

    def test_empty_sequence_is_returned_all(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonEmpty2 (c1 INTEGER) in testbank")
        for c in range(1,10):
            b.execute("Insert INTO jonEmpty2 VALUES (?)", (c))
        a.commit()
        b.execute("SELECT * from jonEmpty2")
        b.fetchall()
        self.assertEqual(b.fetchall(), [])
        a.close()

    def test_empty_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonEmp (c1 NVARCHAR(128)) in testbank")
        b.executemany("Insert INTO jonEmp VALUES (?)", (('',),("",),(" ",)))
        a.commit()
        b.execute("select * from jonEmp")
        self.assertEqual(b.fetchall(), [('',), ('',), (' ',)])
        a.close()

    def test_empty_insert2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonEmp2 (c1 NVARCHAR(128)) in testbank")
        b.execute("Insert INTO jonEmp2 VALUES (?)", (''))
        b.execute("Insert INTO jonEmp2 VALUES (?)", (""))
        b.execute("Insert INTO jonEmp2 VALUES (?)", (" "))
        a.commit()
        b.execute("select * from jonEmp2")
        self.assertEqual(b.fetchall(), [('',), ('',), (' ',)])
        a.close()

    def test_invalide_databank(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        with self.assertRaises(ProgrammingError):
            b.execute("create table bjonEmp2 (c1 NVARCHAR(128)) in potato")
        a.close()

    def test_insert_rowcount_update(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobrowcount (c1 INTEGER,  c2 NVARCHAR(256)) in testbank")
        string = "mimer"
        b.execute("insert into bobrowcount values (:a, :b)", (3, string))
        self.assertEqual(b.rowcount, 1)
        b.executemany("insert into bobrowcount values (:a, :b)", ((5,string),(2,string)))
        b.execute("select * from bobrowcount")
        c = b.fetchall()
        self.assertEqual(b.rowcount, 3)
        b.close()
        a.close()

    def test_delete(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobrowcount2(c1 INTEGER) in testbank")
        for c in range(1,11):
            b.execute("INSERT into bobrowcount2 values (?)", 10)
            b.execute("INSERT into bobrowcount2 values (?)", 20)
        b.execute("INSERT into bobrowcount2 values (?)", 10)
        b.execute("SELECT * from bobrowcount2")
        self.assertEqual(len(b.fetchall()), 21)
        b.execute("DELETE from bobrowcount2 where c1 = 10")
        self.assertEqual(b.rowcount, 11)
        b.execute("SELECT * from bobrowcount2")
        self.assertEqual(len(b.fetchall()), 10)

    def test_update(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobupdate(c1 INTEGER) in testbank")
        for c in range(1,11):
            b.execute("INSERT into bobupdate values (?)", 10)
            b.execute("INSERT into bobupdate values (?)", 20)
        b.execute("INSERT into bobupdate values (?)", 10)
        b.execute("SELECT * from bobupdate")
        self.assertEqual(len(b.fetchall()), 21)
        b.execute("UPDATE bobupdate SET c1 = ? WHERE c1 = 20", 30)
        self.assertEqual(b.rowcount, 10)
        b.execute("SELECT * from bobupdate")
        self.assertEqual(len(b.fetchall()), 21)

    def test_invalid_sequence_fetchone(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonfetchone (c1 INTEGER) in testbank")
        for c in range(1,10):
            b.execute("Insert INTO jonfetchone VALUES (?)", (c))
        a.commit()
        with self.assertRaises(ProgrammingError):
            b.fetchone()
        a.close()

    def test_isolated(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b1 = a.cursor()
        b2 = a.cursor()
        b1.execute("create table jonisolated (c1 INTEGER) in testbank")
        for c in range(1,6):
            b1.execute("Insert INTO jonisolated VALUES (?)", (c))
        b2.execute("SELECT * FROM jonisolated")
        c2 = b2.fetchall()
        self.assertEqual(len(c2), 5)
        self.assertEqual(c2, [(1,),(2,),(3,),(4,),(5,),])
        a.close()

    def test_isolated2(self):
        #fråga per
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonisolated2 (c1 INTEGER) in testbank")
        a.commit()
        a.close()

        a1 = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw, autocommit = True)
        a2 = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw, autocommit = True)
        b1 = a1.cursor()
        b2 = a2.cursor()
        for c in range(1,6):
            b1.execute("Insert INTO jonisolated2 VALUES (?)", (c))
        b2.execute("SELECT * FROM jonisolated2 WHERE c1 < ?", 3)
        c2 = b2.fetchall()
        self.assertEqual(len(c2), 2)
        self.assertEqual(c2, [(1,), (2,)])
        #a1.commit()
        #a2.commit()
        #b3 = a2.cursor()
        b2.execute("SELECT * FROM jonisolated2")
        c3 = b2.fetchall()
        self.assertEqual(len(c3), 5)
        self.assertEqual(c3, [(1,),(2,),(3,),(4,),(5,),])
        a1.close()
        a2.close()

    #fråga per
    def test_isolated3(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonisolated3 (c1 INTEGER) in testbank")
        a.commit()
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        for c in range(1,6):
            b.execute("Insert INTO jonisolated3 VALUES (?)", (c))
        b.execute("SELECT * FROM jonisolated3")
        c1 = b.fetchall()
        self.assertEqual(c1, [(1,),(2,),(3,),(4,),(5,),])
        #a.commit()
        b.execute("SELECT * FROM jonisolated3")
        c2 = b.fetchall()
        self.assertEqual(c2, [(1,),(2,),(3,),(4,),(5,),])
        a.close()

    #blir fel
    def test_invalid_sequence_fetchmany(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonfetchmany (c1 INTEGER) in testbank")
        for c in range(1,10):
            b.execute("Insert INTO jonfetchmany VALUES (?)", (c))
        a.commit()
        with self.assertRaises(ProgrammingError):
            b.fetchmany(10)
        a.close()

    #blir fel, samma som ovan
    #@unittest.skip
    def test_invalid_sequence_fetchall(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonfetchall (c1 INTEGER) in testbank")
        for c in range(1,10):
            b.execute("Insert INTO jonfetchall VALUES (?)", (c))
        a.commit()
        with self.assertRaises(ProgrammingError):
            b.fetchall()
        a.close()

    @unittest.skip
    def test_insert_blob(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonblob (c1 BLOB(18389)) in testbank")
        with open("../minikappa.jpg", 'rb') as input_file:
            ablob = input_file.read()
            b.execute("insert INTO jonblob VALUES (?)", (ablob))
            a.commit()
            b.execute("select * from jonblob")
            c = b.fetchall()[0]
            self.assertEqual(c[0], ablob)
        a.close()

    @unittest.skip
    def test_insert_blob_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonblob2 (c1 BLOB(64111)) in testbank")
        with open("../mimerss.png", 'rb') as input_file:
            ablob = input_file.read()
            b.execute("insert INTO jonblob2 VALUES (?)", (ablob))
            a.commit()
            b.execute("select * from jonblob2")
            c = b.fetchall()[0]
            self.assertEqual(c[0], ablob)
        a.close()

    @unittest.skip
    def test_insert_blob_3(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonblob3 (c1 BLOB(3000000)) in testbank")
        with open("../mimerd.jpg", 'rb') as input_file:
            ablob = input_file.read()
            b.execute("insert INTO jonblob3 VALUES (?)", (ablob))
            a.commit()
            b.execute("select * from jonblob3")
            c = b.fetchall()[0][0]
            self.assertEqual(c, ablob)
        a.close()

    @unittest.skip
    def test_insert_blob_4(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonblob4 (c1 BLOB(3000000)) in testbank")
        with open("../kappa.jpg", 'rb') as input_file:
            ablob = input_file.read()
            b.execute("insert INTO jonblob4 VALUES (?)", (ablob))
            a.commit()
            b.execute("select * from jonblob4")
            c = b.fetchall()[0][0]
            self.assertEqual(c, ablob)
        a.close()

    # bug reported -erik 201808
    @unittest.skip
    def test_insert_nclob(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonnclob (c1 NCLOB(50000)) in testbank")
        anclob = "mimer" * 10000
        b.execute("insert INTO jonnclob VALUES (?)", (anclob))
        a.commit()
        b.execute("select * from jonnclob")
        c = b.fetchall()[0]
        self.assertEqual(c[0], anclob)
        a.close()

    def test_insert_binary(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonbinary (c1 BINARY(3)) in testbank")
        b.execute("insert INTO jonbinary VALUES (x'ABCD01')")
        b.execute("insert INTO jonbinary VALUES (?)", (b'A01'))
        a.commit()
        b.execute("select * from jonbinary")
        c = b.fetchall()
        #self.assertEqual(c[0], [])
        a.close()

    @unittest.skip
    def test_insert_binary_parameter_markers(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonbinary2 (c1 BINARY(2)) in testbank")
        bob = "0x51, 0x53"
        b.execute("insert INTO jonbinary2 VALUES (?)",(bob))
        a.commit()
        #b.execute("select * from jonbinary")
        #c = b.fetchall()[0]
        #self.assertEqual(c[0], anclob)
        a.close()

    @unittest.skip
    def test_insert_nclob_2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonnclob2 (c1 Nclob(450000)) in testbank")
        with open("../book2.txt", "r") as input_file:
            anclob = input_file.read()
            b.execute("insert INTO jonnclob2 VALUES (?)", (anclob))
            a.commit()
            b.execute("select * from jonnclob2")
            c = b.fetchall()[0]
            self.assertEqual(c[0], anclob)
        a.close()

    def test_insert_clob(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table jonclob (c1 clob(30000)) in testbank")
        anclob = "mimer" * 5
        b.execute("insert INTO jonclob VALUES (?)", (anclob))
        a.commit()
        b.execute("select * from jonclob")
        c = b.fetchall()[0]
        self.assertEqual(c[0], anclob)
        a.close()


    def test_insert_bool(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobybool (c1 boolean) in testbank")
        false = 0
        b.execute("insert INTO bobybool VALUES (?)", (False))
        b.execute("insert INTO bobybool VALUES (?)", (45))
        a.commit()
        a.close()

    def test_select_bool(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobybool2 (c1 boolean) in testbank")
        false = 0
        b.execute("insert INTO bobybool2 VALUES (?)", (False))
        b.execute("insert INTO bobybool2 VALUES (?)", (45))
        a.commit()
        b.execute("select * from bobybool2")
        c = b.fetchone()
        self.assertEqual(c[0], False)
        c = b.fetchone()
        self.assertEqual(c[0], True)
        a.close()

    def test_get_connection(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        self.assertEqual(b.connection, a)
        b.close()
        a.close()

    def test_with(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        with a.cursor() as b:
            b.execute("create table withtable (c1 INTEGER) in testbank")
        a.close()

    def test_for(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table fortable (c1 INTEGER) in testbank")
        b.execute("insert INTO fortable VALUES (?)", (45))
        b.execute("select * from fortable")
        for val in b:
            self.assertEqual(val[0], 45)
        a.close()

    def test_result_set_twice(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table kor (c1 INTEGER) in testbank")
        b.execute("insert INTO kor VALUES (?)", (45))
        b.execute("select * from kor")
        for val in b:
            self.assertEqual(val[0], 45)
        b.execute("select * from kor")
        b.execute("select c1 from kor")
        a.close()

    def test_executemany_none(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table manytable (c1 INTEGER) in testbank")
        b.executemany("insert INTO manytable VALUES (?)", [(2,),(34,),(435,),(34,),(63,),(47,),(None,)])
        a.commit()
        a.close()

        a.close()

    def test_select_executemany(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobyselect (c1 INTEGER) in testbank")
        a.commit()
        b.execute("insert INTO bobyselect VALUES (?)", (1))
        with self.assertRaises(ProgrammingError):
            b.executemany("select * from bobyselect where c1 = (?)", ((5,),(10,)))
        b.close()
        a.close()

    def test_select_twice(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bananaselect (c1 INTEGER) in testbank")
        b.execute("select * from bananaselect where c1 = (?)", (5))
        b.execute("select c1 from bananaselect where c1 = (?)", (7))
        b.close()
        a.close()

    def test_fetchall_no_select(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        with self.assertRaises(ProgrammingError):
            b.fetchone()
        with self.assertRaises(ProgrammingError):
            b.fetchmany()
        with self.assertRaises(ProgrammingError):
            b.fetchall()
        b.close()
        a.close()

    def test_bool_insert(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table boolt (c1 BOOLEAN) in testbank")
        b.executemany("insert into boolt values (?)", [(None,), (1,), (0,), (3.1415,), ("potato",), ('code',)])
        b.execute("select * from boolt")
        b.close()
        a.close()

    def test_insert_parametermarkers_different_types(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bob176(c1 NVARCHAR(128)) in testbank")
        b.execute("INSERT INTO bob176 VALUES (?)", "bar")    # correct
        b.execute("INSERT INTO bob176 VALUES (?)", ("bar"))  # correct
        b.execute("INSERT INTO bob176 VALUES (?)", ("bar",)) # correct
        b.execute("INSERT INTO bob176 VALUES (?)", ["bar"])  # correct
        a.commit()
        b.execute("select * from bob176")
        self.assertEqual(b.fetchall(), [("bar",),("bar",),("bar",),("bar",)])
        b.close()
        a.close()

    def test_insert_bigint(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobbig17(c1 BIGINT) in testbank")
        a.commit()
        b.execute("insert into bobbig17 values (234)")
        a.commit()
        b.close()
        a.close()

    @unittest.skip
    def test_help(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        help(b)
        b.close()
        a.close()

    @unittest.skip
    def test_error(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table boberror (c1 INTEGER,  c2 NVARCHAR(10)) in testbank")
        b.execute("inser into boberror values (:a, :b)", (3, 'bob'))
        a.close()

    #ScrollCursor specific tests

    def test_create_scrollcursor(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.close()
      #a.close()

    def test_fetchone_2(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bob853 (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.executemany("insert into bob853 values (:a, :b)", ((9, 'bob9'), (10, 'bob10'),
                                          (11, 'bob11')))
      a.commit()
      b.execute("select * from bob853")
      self.assertEqual(b.fetchone(), (9, 'bob9'))
      self.assertEqual(b.fetchone(), (10, 'bob10'))
      self.assertEqual(b.fetchone(), (11, 'bob11'))
      self.assertEqual(b.fetchone(), [])
      b.close()
      a.close()

    def test_fetchone_rownumber(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow (c1 INTEGER, c2 NVARCHAR(10)) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.executemany("insert into bobrow values (:a, :b)", ((9, 'bob9'), (10, 'bob10'),
                                          (11, 'bob11')))
      a.commit()
      b.execute("select * from bobrow")
      self.assertEqual(b.rownumber, 0)
      self.assertEqual(b.fetchone(), (9, 'bob9'))
      self.assertEqual(b.rownumber, 1)
      self.assertEqual(b.fetchone(), (10, 'bob10'))
      self.assertEqual(b.rownumber, 2)
      self.assertEqual(b.fetchone(), (11, 'bob11'))
      self.assertEqual(b.rownumber, 3)
      self.assertEqual(b.fetchone(), [])
      self.assertEqual(b.rownumber, 3)
      b.close()
      a.close()

    def test_fetchmany_rownumber(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow2(c1 INTEGER, c2 NVARCHAR(100)) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      for c in range(1, 11):
          b.execute("insert into bobrow2 values (:a, :b)", (c, 'bob' + str(c) ))
      a.commit()
      b.execute("select * from bobrow2")
      self.assertEqual(b.rownumber, 0)
      self.assertEqual(b.fetchmany(3), [(1, 'bob1'),(2, 'bob2'),(3, 'bob3')])
      self.assertEqual(b.rownumber, 3)
      self.assertEqual(b.fetchmany(3), [(4, 'bob4'),(5, 'bob5'),(6, 'bob6')])
      self.assertEqual(b.rownumber, 6)
      self.assertEqual(b.fetchmany(10), [(7, 'bob7'),(8, 'bob8'),(9, 'bob9'),(10, 'bob10')])
      self.assertEqual(b.rownumber, 10)
      self.assertEqual(b.fetchmany(2), [])
      b.close()
      a.close()

    def test_fetchall_rownumber(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow3(c1 INTEGER, c2 NVARCHAR(100)) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      for c in range(1, 6):
          b.execute("insert into bobrow3 values (:a, :b)", (c, 'bob' + str(c) ))
      a.commit()
      b.execute("select * from bobrow3")
      self.assertEqual(b.rownumber, 0)
      self.assertEqual(b.fetchall(), [(1, 'bob1'),(2, 'bob2'),(3, 'bob3'),
                                          (4, 'bob4'),(5, 'bob5')])
      self.assertEqual(b.rownumber, 5)
      self.assertEqual(b.fetchall(), [])
      b.close()
      a.close()

    def test_mixfetch_rownumber(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow4(c1 INTEGER, c2 NVARCHAR(100)) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      for c in range(1, 11):
          b.execute("insert into bobrow4 values (:a, :b)", (c, 'bob' + str(c) ))
      a.commit()
      b.execute("select * from bobrow4")
      self.assertEqual(b.rownumber, 0)
      self.assertEqual(b.fetchone(), (1, 'bob1'))
      self.assertEqual(b.rownumber, 1)
      self.assertEqual(b.fetchmany(3), [(2, 'bob2'),(3, 'bob3'),
                                          (4, 'bob4')])
      self.assertEqual(b.rownumber, 4)
      self.assertEqual(b.fetchone(), (5, 'bob5'))
      self.assertEqual(b.rownumber, 5)
      self.assertEqual(b.fetchall(), [(6, 'bob6'),(7, 'bob7'),(8, 'bob8'),(9, 'bob9'),(10, 'bob10')])
      self.assertEqual(b.rownumber, 10)
      self.assertEqual(b.fetchone(), [])
      self.assertEqual(b.fetchmany(21), [])
      self.assertEqual(b.fetchall(), [])
      b.close()
      a.close()

    def test_mixfetch_rowcount(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow5(c1 INTEGER) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      for c in range(1, 101):
          b.execute("insert into bobrow5 values (?)", (c))
      a.commit()
      b.execute("select * from bobrow5")
      self.assertEqual(b.rowcount, 100)
      b.execute("select c1 from bobrow5 where c1 >= ?", (50))
      self.assertEqual(b.rowcount, 51)
      b.execute("select c1 from bobrow5 where c1 < ?", (10))
      self.assertEqual(b.rowcount, 9)
      b.close()
      a.close()

    def test_scroll(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow6(c1 INTEGER) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      for c in range(1, 101):
          b.execute("insert into bobrow6 values (?)", (c))
      a.commit()
      b.execute("select * from bobrow6")
      b.scroll(2,mode='relative')
      self.assertEqual(b.rownumber, 2)
      self.assertEqual(b.fetchone(), (3,))
      b.scroll(3,mode='relative')
      self.assertEqual(b.rownumber, 6)
      self.assertEqual(b.fetchone(), (7,))
      b.scroll(3,mode='absolute')
      self.assertEqual(b.rownumber, 3)
      b.scroll(5,mode='relative')
      self.assertEqual(b.rownumber, 8)
      b.close()
      a.close()

    def test_scroll_error(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow7(c1 INTEGER) in testbank")
      a.close()
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      for c in range(1, 101):
          b.execute("insert into bobrow7 values (?)", (c))
      a.commit()
      b.execute("select * from bobrow7")
      with self.assertRaises(ProgrammingError):
          b.scroll(5,mode='nonexistingmode')
      with self.assertRaises(IndexError):
          b.scroll(101,mode='absolute')
      b.close()
      a.close()

    def test_next(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow8(c1 INTEGER, c2 NVARCHAR(100)) in testbank")
      for c in range(1, 11):
          b.execute("insert into bobrow8 values (:a, :b)", (c, 'bob' + str(c) ))
      a.commit()
      b.execute("select * from bobrow8")
      self.assertEqual(b.next(), (1, 'bob1'),)
      b.scroll(5,mode='relative')
      self.assertEqual(b.next(), (7, 'bob7'),)
      b.scroll(9, mode='absolute')
      b.close()
      a.close()

    def test_next_fetch(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow10(c1 INTEGER, c2 NVARCHAR(100)) in testbank")
      for c in range(1, 11):
          b.execute("insert into bobrow10 values (:a, :b)", (c, 'bob' + str(c) ))
      a.commit()
      b.execute("select * from bobrow10")
      self.assertEqual(b.fetchone(), (1, 'bob1'),)
      self.assertEqual(b.next(), (2, 'bob2'),)
      self.assertEqual(b.fetchmany(2), [(3, 'bob3'), (4, 'bob4')])
      self.assertEqual(b.next(), (5, 'bob5'),)
      b.scroll(1,mode='relative')
      self.assertEqual(b.fetchall(), [(7, 'bob7'), (8, 'bob8'), (9, 'bob9'),
                                          (10, 'bob10')])
      b.close()
      a.close()

    def test_next_error(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table bobrow9(c1 INTEGER, c2 NVARCHAR(100)) in testbank")
      for c in range(1, 11):
          b.execute("insert into bobrow9 values (:a, :b)", (c, 'bob' + str(c) ))
      a.commit()
      b.execute("select * from bobrow9")
      b.scroll(9, mode='absolute')
      with self.assertRaises(StopIteration):
          b.next()
          b.next()
      b.close()
      a.close()

    def test_fetchall_IndexError(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table indexerror (c1 INTEGER) in testbank")
      for val in range(0,10):
          b.execute("insert INTO indexerror VALUES (?)", (val))
      b.execute("select * from indexerror")
      c = b.fetchmany(9)
      c = b.fetchall()
      a.close()

    def test_fetchall_Scroll_outside(self):
      a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
      b = a.cursor(scrollable = 'True')
      b.execute("create table scrolloutside (c1 INTEGER) in testbank")
      for val in range(0,10):
          b.execute("insert INTO scrolloutside VALUES (?)", (val))
      b.execute("select * from scrolloutside")
      with self.assertRaises(IndexError):
          c = b.scroll(100)
      a.close()

    def test_no_select(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobnoselect(c1 INTEGER) in testbank")
        a.close()
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        for c in range(1, 11):
            b.execute("insert into bobnoselect values (5)")
        a.rollback()
        b.execute("select * from bobnoselect")
        c = b.fetchone()
        self.assertEqual(len(c), 0)
        b.close()
        a.close()

    def test_no_select2(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobnoselect2(c1 INTEGER) in testbank")
        a.close()
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        for c in range(1, 11):
            b.execute("insert into bobnoselect2 values (5)")
        a.rollback()
        b.execute("select * from bobnoselect2")
        c = b.fetchmany(5)
        self.assertEqual(len(c), 0)
        b.close()
        a.close()

    def test_no_select3(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        b.execute("create table bobnoselect3(c1 INTEGER) in testbank")
        a.close()
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        for c in range(1, 11):
            b.execute("insert into bobnoselect3 values (5)")
        a.rollback()
        b.execute("select * from bobnoselect3")
        c = b.next()
        self.assertEqual(len(c), 0)
        b.close()
        a.close()

    def test_next_noselect(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor(scrollable = 'True')
        with self.assertRaises(ProgrammingError):
            b.next()
        b.close()
        a.close()


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
