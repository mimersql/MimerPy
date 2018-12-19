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
        (self.syscon, self.tstcon) = db_config.setup()

    @classmethod
    def tearDownClass(self):
        self.tstcon.close()
        with self.syscon.cursor() as c:
            c.execute("DROP IDENT MIMERPY CASCADE")
        self.syscon.commit()
        self.syscon.close()

    def tearDown(self):
        self.tstcon.commit()

    def test_connect(self):
        con = mimerpy.connect(**db_config.TSTUSR)
        con.close()


    def test_connect_many(self):
        for a in range(100):
            con = mimerpy.connect(**db_config.TSTUSR)
            con.close()

    # Ran with 1000 before, but with current version it is very slow
    # Mimer now uses fancy new password encryption, this is slower than before
    def test_connect_many_no_close(self):
        for a in range(100):
            con = mimerpy.connect(**db_config.TSTUSR)


    # &&&& Fixme
    def os_user(self):
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor()
        b.execute("CREATE IDENT ergu AS OS_USER USING 'mimerPass'")
        for aa in range(1000):
            con = mimerpy.connect(dsn = self.dbName, user = "ergu", password = self.psw)
            con.close()
        b.execute("DROP IDENT ergu CASCADE")

    # Make sure you allow more than the user than the number_of_connections or problems occur
    def test_condis(self):
        mylist = []
        number_of_connections = 20
        for a in range(number_of_connections):
            con = mimerpy.connect(**db_config.TSTUSR)
            mylist.append([con, True])

        for a in range(100):
            rand = random.randint(0,number_of_connections - 1)
            if(not mylist[rand][1]):
                mylist.pop(rand)
                con = mimerpy.connect(**db_config.TSTUSR)
                mylist.append([con, True])
            else:
                mylist[rand][0].close()
                mylist[rand][1] = False

        for a in mylist:
            if (a[1]):
                a[0].close()

    def test_connect_2(self):
        a = mimerpy.connect(**db_config.TSTUSR)
        b = mimerpy.connect(**db_config.TSTUSR)
        a.close()
        b.close()

    def test_connect_close(self):
        a = mimerpy.connect(**db_config.TSTUSR)
        a.close()
        with self.assertRaises(ProgrammingError):
            a.commit()

    @unittest.skip("Connection cleanup failure")
    def test_connect_invalid_login(self):
        with self.assertRaises(DatabaseError):
            wrong = db_config.TSTUSR
            wrong['password'] = 'wrong'
            a = mimerpy.connect(**wrong)

    @unittest.skip("Connection cleanup failure")
    def test_connect_invalid_login_2(self):
        with self.assertRaises(IntegrityError):
            a = mimerpy.connect("self.d", "du", "där")

    @unittest.skip("Connection cleanup failure")
    def test_connect_invalid_login_3(self):
        with self.assertRaises(IntegrityError):
            a = mimerpy.connect()

    def test_weakref(self):
        from weakref import ref
        import gc
        con = mimerpy.connect(**db_config.TSTUSR)
        w = ref(con)
        con.close()
        del con
        gc.collect()
        self.assertTrue(w() is None)

    def test_connect_cursor(self):
        con = mimerpy.connect(**db_config.TSTUSR)
        b = con.cursor()
        b.close()
        con.close()

    def test_connect_cursor_close(self):
        con = mimerpy.connect(**db_config.TSTUSR)
        b = con.cursor()
        b.close()
        with self.assertRaises(ProgrammingError):
            b.execute("Hello")
        con.close()

    def test_connect_cursor_close_connection_only(self):
        con = mimerpy.connect(**db_config.TSTUSR)
        b = con.cursor()
        con.close()

    def test_connect_cursor_close_connection_only_2(self):
        con = mimerpy.connect(**db_config.TSTUSR)
        b = con.cursor()
        con.close()
        with self.assertRaises(ProgrammingError):
            b.execute("Hello")

    def test_multiple_cursors(self):
        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        b = a.cursor()
        a.close()

    def test_with(self):
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            c = a.cursor()

    def test_with_close(self):
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob2(c1 INTEGER, c2 NVARCHAR(10)) in pybank")
        with self.assertRaises(ProgrammingError):
            b.execute("select * from cbob2")

    @unittest.skip("not yet")
    #There is no rollback with DDL statements
    def test_with_no_commit(self):
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob(c1 INTEGER, c2 NVARCHAR(10)) in pybank");
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            with self.assertRaises(ProgrammingError):
                b.execute("select * from cbob")


    # &&&& Ska vi verkligen autocommitta?
    def test_with_no_commit_insert(self):
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbobc(c1 INTEGER, c2 NVARCHAR(10)) in pybank");
            a.commit()
            a.execute("insert into cbobc values (?, ?)", (11, 'aaa'))
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            b.execute("select * from cbobc")
            self.assertEqual(b.fetchall(), [])

    def test_with_commit(self):
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob33(c1 INTEGER, c2 NVARCHAR(10)) in pybank");
            a.commit()
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            b.execute("select * from cbob33")

    def test_with_commit_insert(self):
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            c = a.cursor()
            b.execute("create table cbob373(c1 INTEGER, c2 NVARCHAR(10)) in pybank");
            a.commit()
            a.execute("insert into cbob373 values (?, ?)", (11, 'aaa'))
            a.commit()
        with mimerpy.connect(**db_config.TSTUSR) as a:
            b = a.cursor()
            b.execute("select * from cbob373")
            self.assertEqual(b.fetchall(), [(11, 'aaa')])

    def test_operate_after_closed(self):
        a = mimerpy.connect(**db_config.TSTUSR)
        a.close()
        a.close()
        with self.assertRaises(ProgrammingError):
            a.execute("Kalle")
        with self.assertRaises(ProgrammingError):
            a.executemany("Kalle", ("Kula"))

    def test_execute(self):
        b = self.tstcon.execute("create table bob(c1 INTEGER, c2 NVARCHAR(10))"
                                "in pybank")
        b.close()


    def test_executemany(self):
        b = self.tstcon.execute("create table bob2(c1 INTEGER, c2 NVARCHAR(10))"
                                "in pybank")
        b = self.tstcon.executemany("insert into bob2 values (:a, :b)",
                                    ((11, 'aaa'), (22, 'bb'),
                                     (33, 'cc'), (44, 'dd')))
        self.tstcon.commit()
        b.execute("select * from bob2")
        self.assertEqual(b.fetchall(),
                         [(11, 'aaa'), (22, 'bb'), (33, 'cc'), (44, 'dd')])
        b.close()


    def test_executemany_simple(self):
        b = self.tstcon.execute("create table bob2_simple(c1 INTEGER)"
                                "in pybank")
        b = self.tstcon.executemany("insert into bob2_simple values (:a)",
                                    ((11,),(22,),(33,),(44,)))
        self.tstcon.commit()
        b.execute("select * from bob2_simple")
        self.assertEqual(b.fetchall(),
                         [(11,),(22,),(33,),(44,)])
        b.close()


    def test_executemany_no_closing(self):
        b = self.tstcon.execute("create table bob3(c1 INTEGER, c2 NVARCHAR(10))"
                                "in pybank")
        b.executemany("insert into bob3 values (:a, :b)",
                      ((11, 'aaa'), (22, 'bb'), (33, 'cc'), (44, 'dd')))
        self.tstcon.commit()
        b.execute("select * from bob3")
        self.assertEqual(b.fetchall(),
                         [(11, 'aaa'), (22, 'bb'), (33, 'cc'), (44, 'dd')])

    def test_executemany_no_closing_dummy(self):
        b = self.tstcon.execute("create table bob4(c1 INTEGER, c2 NVARCHAR(10))"
                                "in pybank")
        b = self.tstcon.executemany("insert into bob4 values (:a, :b)",
                                    ((11, 'aaa'), (22, 'bb'),
                                     (33, 'cc'),  (44, 'dd')))
        self.tstcon.commit()
        b.execute("select * from bob4")
        self.assertEqual(b.fetchall(),
                         [(11, 'aaa'), (22, 'bb'), (33, 'cc'), (44, 'dd')])

    def test_commit(self):
        b = self.tstcon.execute("create table bob5(c1 INTEGER) in pybank")
        b.execute("insert into bob5 values (:a)", (11))
        self.tstcon.commit()
        b.execute("select * from bob5")
        self.assertEqual(b.fetchone(), (11,))
        b.close()

    def test_rollback(self):
        b = self.tstcon.execute("create table bob6(c1 INTEGER) in pybank")
        self.tstcon.commit()

        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.execute("insert into bob6 values (:a)", (1133))
        a.rollback()
        a.close()

        b = self.tstcon.execute("select * from bob6")
        self.assertEqual(b.fetchone(), [])
        b.close()

    def test_autocommit(self):
        b = self.tstcon.execute("create table bob66(c1 INTEGER) in pybank")
        self.tstcon.commit()

        a = mimerpy.connect(**db_config.TSTUSR)
        a.autocommit(True)
        b = a.execute("insert into bob66 values (:a)", (1133))
        a.close()

        b = self.tstcon.execute("select * from bob66")
        self.assertEqual(b.fetchone(), (1133,))
        b.close()

    def test_autocommit_2(self):
        b = self.tstcon.execute("create table bobr66(c1 INTEGER) in pybank")
        self.tstcon.commit()

        a = mimerpy.connect(**db_config.TSTUSR)
        a.autocommit(False)
        b = a.execute("insert into bobr66 values (:a)", (1133))
        a.close()

        a = mimerpy.connect(**db_config.TSTUSR)
        a.autocommit(True)
        b = a.execute("insert into bobr66 values (:a)", (23885))
        a.close()

        b = self.tstcon.execute("select * from bobr66")
        self.assertEqual(b.fetchone(), (23885,))
        b.close()

    def test_autocommit_3(self):
        b = self.tstcon.execute("create table bob63(c1 INTEGER) in pybank")
        self.tstcon.commit()

        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.execute("insert into bob63 values (:a)", (1133))
        a.close()

        b = self.tstcon.execute("select * from bob63")
        self.assertEqual(b.fetchone(), [])
        b.close()

    def test_autocommit_4(self):
        b = self.tstcon.execute("create table bob64(c1 INTEGER) in pybank")
        self.tstcon.commit()

        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.execute("insert into bob64 values (:a)", (1133))
        a.autocommit(True)
        a.close()

        b = self.tstcon.execute("select * from bob64")
        self.assertEqual(b.fetchone(), [])
        b.close()


    def test_threads(self):

        def thread_test(self):
            try:
                a = mimerpy.connect(**db_config.TSTUSR)
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


    def test_threads_2(self):

        def thread_test(self):
            try:
                a = mimerpy.connect(**db_config.TSTUSR)
                cur = a.cursor()
                cur.execute("select * from threadbob")
                cur.fetchone()
                a.close()
                #print("closing")
            except Exception as e:
               ###print("Error: in thread: ", e)
              """ """

        b = self.tstcon.execute("create table threadbob(c1 INTEGER) in pybank")
        b.execute("insert into threadbob values (:a)", (1133))
        self.tstcon.commit()
        b.close()

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

    def test_xid(self):
        with self.assertRaises(NotSupportedError):
            self.tstcon.xid()
        with self.assertRaises(NotSupportedError):
            self.tstcon.tpc_begin()
        with self.assertRaises(NotSupportedError):
            self.tstcon.tpc_prepare()
        with self.assertRaises(NotSupportedError):
            self.tstcon.tpc_commit()
        with self.assertRaises(NotSupportedError):
            self.tstcon.tpc_rollback()
        with self.assertRaises(NotSupportedError):
            self.tstcon.tpc_recover()

    @unittest.skip("not yet")
    # Not working atm. cant mix ddl and dml statements in one transaction
    # When DDL and DML statements are mixed the behavior is not super clear
    def test_rollback_not_working(self):
        b = self.tstcon.execute("create table bob7(c1 INTEGER) in pybank")
        b.execute("insert into bob7 values (:a)", (1133))
        self.tstcon.rollback()
        b.execute("select * from bob7")
        self.assertEqual(b.fetchone(), ())
        b.close()

        a = mimerpy.connect(**db_config.TSTUSR)
        b = a.execute("select * from bob6")
        print(b.fetchone())
        a.close()

if __name__ == '__main__':
    unittest.main()
