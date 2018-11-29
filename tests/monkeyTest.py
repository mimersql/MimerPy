import unittest
import time
import math
import mimerpy
import random
import uuid
import threading

from mimerpy.mimPyExceptions import *
import db_config


class TestMonkey(unittest.TestCase):

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
        a.close()

        a = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        b = a.cursor()
        b.execute("create table monkeyTable (c1 INTEGER, c2 BIGINT, c3 SMALLINT, c4 NVARCHAR(256), c5 BLOB, c6 NCLOB, c7 BOOLEAN, c8 FLOAT) in testbank")
        a.close()
        print("set up up complete \n------------------------")

    @classmethod
    def tearDownClass(self):
        print("Tear down begun")
        a = mimerpy.connect(dsn = self.dbName, user = self.sysadmName, password = self.sysadmpsw)
        b = a.cursor()
        b.execute("DROP DATABANK testbank CASCADE")
        b.execute("DROP IDENT TEST_IDENT CASCADE")
        b.close()
        a.commit()
        a.close()
        print("Tear down complete")

    def test_cursor_dml(self):
        conn = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        cur = conn.cursor()

        for nu in range(0,2000):
            apa = random.randint(0,10)
            if(apa == 0):
                self.cursor_select(cur)
            elif(apa == 1):
                self.cursor_select_and_fetchone(cur)
            elif(apa == 2):
                self.cursor_select_and_fetchmany(cur, nu)
            elif(apa == 3):
                self.cursor_select_and_fetchall(cur)
            elif(apa == 4):
                self.cursor_insert_executemany(cur)
            elif(apa == 5):
                self.cursor_insert(cur)
            elif(apa == 6):
                self.cursor_insert_many(cur)
            elif(apa == 7):
                try:
                    self.cursor_next(cur)
                except StopIteration:
                    """Caught exception"""
            elif(apa == 8):
                self.cursor_commit(conn)
            elif(apa == 9):
                self.cursor_rollback(conn)
            elif(apa == 10):
                self.cursor_description_all(cur)


    def test_cursor_ddl_and_dml(self):
        conn = mimerpy.connect(dsn = self.dbName, user = self.usrName, password = self.psw)
        cur = conn.cursor()
        for nu in range(0,1000):
            apa = random.randint(0,15)
            if(apa == 0):
                try:
                    self.cursor_select(cur)
                except Exception:
                    """ Ok """
            elif(apa == 1):
                try:
                    self.cursor_select_and_fetchone(cur)
                except Exception:
                    """ Ok """
            elif(apa == 2):
                try:
                    self.cursor_select_and_fetchmany(cur, nu)
                except Exception:
                    """ Ok """

            elif(apa == 3):
                try:
                    self.cursor_select_and_fetchall(cur)
                except Exception:
                    """ Ok """
            elif(apa == 4):
                try:
                    self.cursor_insert_executemany(cur)
                except Exception:
                    """ Ok """
            elif(apa == 5):
                try:
                    self.cursor_insert(cur)
                except Exception:
                    """ Ok """
            elif(apa == 6):
                try:
                    self.cursor_insert_many(cur)
                except Exception:
                    """ Ok """
            elif(apa == 7):
                try:
                    self.cursor_next(cur)
                except Exception:
                    """Caught exception"""
            elif(apa == 8):
                try:
                    self.cursor_update(cur)
                except Exception:
                    """ Ok """
            elif(apa == 9):
                try:
                    self.monkey_insert(cur)
                except Exception:
                    """ Ok """
            elif(apa == 11):
                try:
                    self.monkey_select_and_fetchone(cur)
                except Exception:
                    """ Ok """
            elif(apa == 12):
                try:
                    self.cursor_delete(cur)
                except Exception:
                    """ Ok """
            elif(apa == 13):
                try:
                    self.cursor_commit(conn)
                except Exception:
                    """ Ok """
            elif(apa == 14):
                try:
                    self.cursor_rollback(conn)
                except Exception:
                    """ Ok """
            elif(apa == 15):
                try:
                    self.cursor_description_all(cur)
                except Exception:
                    """ Ok """

    def test_condis(self):
        print("Running test_connect_many_no_close: \n------------------------")

        def condis(self):
            mylist = []
            for ac in range(5):
                con = mimerpy.connect(dsn = "testDB11", user = "SYSADM", password = "SYSADM")
                mylist.append([con, True])

            for a in range(10000):
                rand = random.randint(0,4)
                if(not mylist[rand][1]):
                    mylist.pop(rand)
                    conn = mimerpy.connect(dsn = "testDB11", user = "SYSADM", password = "SYSADM")
                    mylist.append([conn, True])
                else:
                    mylist[rand][0].close()
                    mylist[rand][1] = False

            for ab in mylist:
                if(ab[1]):
                    ab[0].close()

        for i in range(9):
            t = threading.Thread(target = condis, args = (self,))
            t.start()
        while(threading.active_count() > 1):
            time.sleep(1)
        print("------------------------\nTest complete: \n")

    def cursor_insert(self, cur):
        a = random.randint(-2**31, 2**31 - 1)
        b = random.randint(-2**63, 2**63 - 1)
        c = random.randint(-2**15, 2**15 - 1)
        d = str(uuid.uuid4())
        e = str(uuid.uuid4())
        f = str(uuid.uuid4())
        g = random.randint(0,1)
        h = random.random()
        cur.execute("insert into monkeyTable values (?,?,?,?,?,?,?,?)",[(a),(b),(c),(d),(e),(f),(g),(h)])

    def monkey_insert(self, cur):
        a = random.randint(-2**100,2**100)
        d = str(uuid.uuid4() * random.randint(0,1000))
        g = random.randint(0,1)
        h = random.random() / 3
        cur.execute("insert into monkeyTable values (?,?,?,?,?,?,?,?)",[(a),(a),(a),(d),(d),(d),(d),(h)])

    def cursor_select(self, cur):
        cul = random.randint(1,8)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)

    def monkey_select(self, cur):
        cul = random.randint(0,10)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)

    def cursor_select_and_fetchone(self, cur):
        cul = random.randint(1,8)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)
        cur.fetchone()

    def monkey_select_and_fetchone(self, cur):
        cul = random.randint(1,8)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)
        laps = random.randint(0,100)
        for a in laps:
            cur.fetchone()

    def cursor_select_and_fetchmany(self, cur, numboflaps):
        cul = random.randint(1,8)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)
        up = random.randint(0,numboflaps)
        cur.fetchmany(up)

    def cursor_select_and_fetchall(self, cur):
        cul = random.randint(1,8)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)
        cur.fetchall()

    def cursor_insert_executemany(self, cur):
        monkeylist = []
        for m in range(0,10):
            a = random.randint(-2**31, 2**31 - 1)
            b = random.randint(-2**63, 2**63 - 1)
            c = random.randint(-2**15, 2**15 - 1)
            d = str(uuid.uuid4())
            e = str(uuid.uuid4())
            f = str(uuid.uuid4())
            g = random.randint(0,1)
            h = random.random()
            monkeylist.append((a,b,c,d,e,f,g,h))
        #print("monkeylist  ", monkeylist)
        cur.executemany("insert into monkeyTable values (?,?,?,?,?,?,?,?)", monkeylist)

    def cursor_insert_many(self, cur):
        a = random.randint(-2**31, 2**31 - 1)
        b = random.randint(-2**63, 2**63 - 1)
        c = random.randint(-2**15, 2**15 - 1)
        d = str(uuid.uuid4())
        e = str(uuid.uuid4())
        f = str(uuid.uuid4())
        g = random.randint(0,1)
        h = random.random()
        for a in range(0,10):
            cur.execute("insert into monkeyTable values (?,?,?,?,?,?,?,?)", ((a),(b),(c),(d),(e),(f),(g),(h)))

    def cursor_next(self, cur):
        cul = random.randint(1,8)
        a = "c" + str(cul)
        query = "select " + a + " from monkeyTable"
        cur.execute(query)
        cur.next()

    def cursor_update(self, cur):
        a = random.randint(-2**31, 2**31 - 1)
        cur.execute("update monkeyTable set where c1 = ? where c1 < ?", (a, a))

    def cursor_delete(self, cur):
        a = random.randint(-2**31, 2**31 - 1)
        cur.execute("delete from monkeyTable where c1 = ? where c1 < ?", (a, a))

    def cursor_next_StopIteration(self, cur):
        cul = random.randint(1,8)
        cur.execute("DELETE from monkeyTable")
        try:
            cur.next()
        except StopIteration:
            """Caught Exception"""

    def cursor_commit(self, conn):
        conn.commit()

    def cursor_rollback(self, conn):
        conn.rollback()

    def cursor_description_all(self,cur):
        cul = random.randint(1,8)
        cur.execute("select * from monkeyTable")
        self.assertEqual(cur.description,(('c1', 50, None, None, None, None, None),
                                        ('c2', 52, None, None, None, None, None),
                                        ('c3', 48, None, None, None, None, None),
                                        ('c4', 63, None, None, None, None, None),
                                        ('c5', 57, None, None, None, None, None),
                                        ('c6', 59, None, None, None, None, None),
                                        ('c7', 42, None, None, None, None, None),
                                        ('c8', 56, None, None, None, None, None),))


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
