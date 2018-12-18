import mimerpy
import unittest
import time
import random
import _thread

from mimerpy.mimPyExceptions import *
import db_config

class TestConnectionMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.dbName = db_config.DB_INFO['DBNAME']
        self.usrName = "TEST_IDENT"
        self.psw = "mimerPass"
        self.sysadmName = db_config.DB_INFO['SYSADM']
        self.sysadmpsw = db_config.DB_INFO['SYADMPSW']
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor()
        b.execute("CREATE IDENT TEST_IDENT AS USER USING 'mimerPass'")
        b.execute("create databank testbank")
        b.execute("Grant TABLE on databank testbank to TEST_IDENT")
        b.close()
        a.commit()
        a.close()

        print("set up up complete \n------------------------")

    @classmethod
    def tearDownClass(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor()
        b.execute("DROP DATABANK testbank CASCADE")
        b.execute("DROP IDENT TEST_IDENT CASCADE")
        b.close()
        a.close()
        print("Tear down complete")

    def test_connect(self):
        print("Running test_connect: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.close()
        print("------------------------\nTest complete: \n")


    def test_connect_many(self):
        print("Running test_connect_many: \n------------------------")
        for a in range(100):
            con = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
            con.close()
        print("------------------------\nTest complete: \n")

    # Ran with 1000 before, but with current version it is very slow
    # Mimer now uses fancy new password encryption, this is slower than before
    def test_connect_many_no_close(self):
        print("Running test_connect_many_no_close: \n------------------------")
        for a in range(100):
            con = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        print("------------------------\nTest complete: \n")


    def os_user(self):
        print("Running os_user: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor()
        b.execute("CREATE IDENT ergu AS OS_USER USING 'mimerPass'")
        for aa in range(1000):
            con = mimerpy.connect(dsn = self.dbName, user = "ergu", password = self.psw)
            con.close()
        b.execute("DROP IDENT ergu CASCADE")
        print("------------------------\nTest complete: \n")

    # Make sure you allow more than the user than the number_of_connections or problems occur
    def test_condis(self):
        print("Running test_condis: \n------------------------")
        mylist = []
        number_of_connections = 20
        for a in range(number_of_connections):
            con = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
            mylist.append([con, True])

        for a in range(100):
            rand = random.randint(0,number_of_connections - 1)
            if(not mylist[rand][1]):
                mylist.pop(rand)
                conn = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
                mylist.append([conn, True])
            else:
                mylist[rand][0].close()
                mylist[rand][1] = False

        for a in mylist:
            if (a[1]):
                a[0].close()

        print("------------------------\nTest complete: \n")

    def test_connect_2(self):
        print("Running test_connect_2: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.close()
        b.close()
        print("------------------------\nTest complete: \n")

    def test_connect_close(self):
        print("Running test_connect_close: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.close()
        with self.assertRaises(ProgrammingError):
            a.commit()
        print("------------------------\nTest complete: \n")

    def test_connect_invalid_login(self):
        print("Running test_connect_invalid_login: \n------------------------")
        with self.assertRaises(DatabaseError):
            a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = "InvalidPass")
        print("------------------------\nTest complete: \n")

    def test_connect_invalid_login_2(self):
        print("Running test_connect_invalid_login_2: \n------------------------")
        with self.assertRaises(IntegrityError):
            a = mimerpy.connect("self.d", "du","där")
        print("------------------------\nTest complete: \n")

    def test_connect_invalid_login_3(self):
        print("Running test_connect_invalid_login_3: \n------------------------")
        with self.assertRaises(IntegrityError):
            a = mimerpy.connect()
        print("------------------------\nTest complete: \n")

    def test_weakref(self):
        # Tagen från postgres tester
        from weakref import ref
        import gc
        conn = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        w = ref(conn)
        conn.close()
        del conn
        gc.collect()
        self.assertTrue(w() is None)

    def test_connect_cursor(self):
        print("Running test_connect_cursor: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor()
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_connect_cursor_close(self):
        print("Running test_connect_cursor_close: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor()
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("Hello")
        a.close()
        print("------------------------\nTest complete: \n")

    def test_connect_cursor_close_connection_only(self):
        print("Running test_connect_cursor_close_mimerpy.connect_only: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_connect_cursor_close_connection_only_2(self):
        print("Running test_connect_cursor_close_mimerpy.connect_only_2: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor()
        a.close()
        with self.assertRaises(ProgrammingError):
            b.execute("Hello")
        print("------------------------\nTest complete: \n")

    def test_mutiple_cursors(self):
        print("Running test_mutiple_cursors: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_with(self):
        print("Running test_with: \n------------------------")
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            c = a.cursor()
        print("------------------------\nTest complete: \n")

    def test_with_close(self):
        print("Running test_with_close: \n------------------------")
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob2(c1 INTEGER, c2 NVARCHAR(10)) in testbank");
        with self.assertRaises(ProgrammingError):
            b.execute("select * from cbob2")
        print("------------------------\nTest complete: \n")

    @unittest.skip
    #There is no rollback with DDL statements
    def test_with_no_commit(self):
        print("Running test_with_close: \n------------------------")
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob(c1 INTEGER, c2 NVARCHAR(10)) in testbank");
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            with self.assertRaises(ProgrammingError):
                b.execute("select * from cbob")
        print("------------------------\nTest complete: \n")


    def test_with_no_commit_insert(self):
        print("Running test_with_close: \n------------------------")
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbobc(c1 INTEGER, c2 NVARCHAR(10)) in testbank");
            a.commit()
            a.execute("insert into cbobc values (?, ?)", (11, 'aaa'))
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            b.execute("select * from cbobc")
            self.assertEqual(b.fetchall(), [])
        print("------------------------\nTest complete: \n")

    def test_with_commit(self):
        print("Running test_with_close: \n------------------------")
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob33(c1 INTEGER, c2 NVARCHAR(10)) in testbank");
            a.commit()
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            b.execute("select * from cbob33")
        print("------------------------\nTest complete: \n")

    def test_with_commit_insert(self):
        print("Running test_with_close: \n------------------------")
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob373(c1 INTEGER, c2 NVARCHAR(10)) in testbank");
            a.commit()
            a.execute("insert into cbob373 values (?, ?)", (11, 'aaa'))
            a.commit()
        with mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw) as a:
            b = a.cursor()
            b.execute("select * from cbob373")
            self.assertEqual(b.fetchall(), [(11, 'aaa')])
        print("------------------------\nTest complete: \n")

    def test_operate_after_closed(self):
        print("Running test_operate_after_closed: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.close()
        a.close()
        with self.assertRaises(ProgrammingError):
            a.execute("Kalle")
        with self.assertRaises(ProgrammingError):
            a.executemany("Kalle", ("Kula"))
        print("------------------------\nTest complete: \n")

    def test_execute(self):
        print("Running test_execute: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")


    def test_executemany(self):
        print("Running test_executemany: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob2(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b = a.executemany("insert into bob2 values (:a, :b)", ((11, 'aaa'),
                            (22, 'bb'),(33, 'cc'),(44, 'dd')))
        a.commit()
        b.execute("select * from bob2")
        self.assertEqual(b.fetchall(), [(11, 'aaa'),
                            (22, 'bb'),(33, 'cc'),(44, 'dd')])
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")



    def test_executemany_simple(self):
        print("Running test_executemany: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob2_simple(c1 INTEGER) in testbank")
        b = a.executemany("insert into bob2_simple values (:a)", ((11,),
                            (22,),(33,),(44,)))
        a.commit()
        b.execute("select * from bob2_simple")
        self.assertEqual(b.fetchall(), [(11,),
                            (22,),(33,),(44,)])
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")


    def test_executemany_no_closing(self):
        print("Running test_executemany_no_closing: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob3(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b.executemany("insert into bob3 values (:a, :b)", ((11, 'aaa'),
                            (22, 'bb'),(33, 'cc'),(44, 'dd')))
        a.commit()
        b.execute("select * from bob3")
        self.assertEqual(b.fetchall(), [(11, 'aaa'),
                            (22, 'bb'),(33, 'cc'),(44, 'dd')])
        a.close()
        print("------------------------\nTest complete: \n")

    def test_executemany_no_closing_dummy(self):
        print("Running test_executemany_no_closing_dummy: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob4(c1 INTEGER, c2 NVARCHAR(10)) in testbank")
        b = a.executemany("insert into bob4 values (:a, :b)", ((11, 'aaa'),
                            (22, 'bb'),(33, 'cc'),(44, 'dd')))
        a.commit()
        b.execute("select * from bob4")
        self.assertEqual(b.fetchall(), [(11, 'aaa'),
                            (22, 'bb'),(33, 'cc'),(44, 'dd')])
        a.close()
        print("------------------------\nTest complete: \n")

    def test_commit(self):
        print("Running test_commit: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob5(c1 INTEGER) in testbank")
        b.execute("insert into bob5 values (:a)", (11))
        a.commit()
        b.execute("select * from bob5")
        self.assertEqual(b.fetchone(), (11,))
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_rollback(self):
        print("Running test_rollback: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob6(c1 INTEGER) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("insert into bob6 values (:a)", (1133))
        a.rollback()
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("select * from bob6")
        self.assertEqual(b.fetchone(), [])
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_autocommit(self):
        print("Running test_autocommit: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob66(c1 INTEGER) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.autocommit(True)
        b = a.execute("insert into bob66 values (:a)", (1133))
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("select * from bob66")
        self.assertEqual(b.fetchone(), (1133,))
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_autocommit_2(self):
        print("Running test_autocommit_2: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bobr66(c1 INTEGER) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.autocommit(False)
        b = a.execute("insert into bobr66 values (:a)", (1133))
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        a.autocommit(True)
        b = a.execute("insert into bobr66 values (:a)", (23885))
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("select * from bobr66")
        self.assertEqual(b.fetchone(), (23885,))
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_autocommit_3(self):
        print("Running test_autocommit_2: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob63(c1 INTEGER) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw, autocommit = True)
        b = a.execute("insert into bob63 values (:a)", (1133))
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("select * from bob63")
        self.assertEqual(b.fetchone(), (1133,))
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")

    def test_autocommit_4(self):
        print("Running test_autocommit_2: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob64(c1 INTEGER) in testbank")
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("insert into bob64 values (:a)", (1133))
        a.autocommit(True)
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("select * from bob64")
        self.assertEqual(b.fetchone(), [])
        b.close()
        a.close()
        print("------------------------\nTest complete: \n")


    def test_threads(self):
        print("Running test_threads: \n------------------------")

        def thread_test(self):
            try:
                a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
                a.close()
                #print("closing")
            except Exception as e:
               print("Error: in thread: ", e)
               """ """
            try:
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )
               _thread.start_new_thread( thread_test,(self,) )

            except Exception as e:
               print("Error: unable to start thread: ", e)
               """ """

        print("------------------------\nTest complete: \n")

    def test_threads_2(self):
        print("Running test_threads_2: \n------------------------")

        def thread_test(self):
            try:
                a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
                cur = a.cursor()
                cur.execute("select * from threadbob")
                cur.fetchone()
                a.close()
                #print("closing")
            except Exception as e:
               ###print("Error: in thread: ", e)
              """ """

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table threadbob(c1 INTEGER) in testbank")
        b.execute("insert into threadbob values (:a)", (1133))
        a.commit()
        b.close()
        a.close()

        try:
           t1 = _thread.start_new_thread( thread_test,(self,) )
           t2 = _thread.start_new_thread( thread_test,(self,) )
           t3 = _thread.start_new_thread( thread_test,(self,) )
           t4 = _thread.start_new_thread( thread_test,(self,) )
           t5 = _thread.start_new_thread( thread_test,(self,) )
           t6 = _thread.start_new_thread( thread_test,(self,) )
           t7 = _thread.start_new_thread( thread_test,(self,) )
           t8 = _thread.start_new_thread( thread_test,(self,) )
           t9 = _thread.start_new_thread( thread_test,(self,) )
           t10 = _thread.start_new_thread( thread_test,(self,) )

        except Exception as e:
           print("Error: unable to start thread: ", e)
           """ """
        # Potato, needs later fix
        # Need to change this for a _thread.join() later
        time.sleep(2)

    #print("------------------------\nTest complete: \n")

    def test_xid(self):
        print("Running test_xid: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        with self.assertRaises(NotSupportedError):
            a.xid()
        with self.assertRaises(NotSupportedError):
            a.tpc_begin()
        with self.assertRaises(NotSupportedError):
            a.tpc_prepare()
        with self.assertRaises(NotSupportedError):
            a.tpc_commit()
        with self.assertRaises(NotSupportedError):
            a.tpc_rollback()
        with self.assertRaises(NotSupportedError):
            a.tpc_recover()
        print("------------------------\nTest complete: \n")

    @unittest.skip
    # Not working atm. cant mix ddl and dml statements in one transaction
    # When DDL and DML statements are mixed the behavior is not super clear
    def test_rollback_not_working(self):
        print("Running test_rollback: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("create table bob7(c1 INTEGER) in testbank")
        b.execute("insert into bob7 values (:a)", (1133))
        a.rollback()
        b.execute("select * from bob7")
        self.assertEqual(b.fetchone(), ())
        b.close()
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.execute("select * from bob6")
        print(b.fetchone())
        a.close()
        print("------------------------\nTest complete: \n")

    @unittest.skip
    def test_help(self):
        """ Enters help mode. Only suited for manual testing"""
        print("Running test_help: \n------------------------")
        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        help(a)
        a.close()
        print("------------------------\nTest complete: \n")


if __name__ == '__main__':
    unittest.main()
