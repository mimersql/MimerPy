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
import random
import uuid
import threading

from mimerpy.mimPyExceptions import *
import db_config


class TestMonkey(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.syscon, self.tstcon) = db_config.setup()

    @classmethod
    def tearDownClass(self):
        db_config.teardown(tstcon=self.tstcon, syscon=self.syscon)

    def setUp(self):
        self.tstcon.rollback()
        with self.tstcon.cursor() as c:
            c.execute("""
create table monkeyTable (c1 INTEGER,
                          c2 BIGINT,
                          c3 SMALLINT,
                          c4 NVARCHAR(256),
                          c5 BLOB,
                          c6 NCLOB,
                          c7 BOOLEAN,
                          c8 FLOAT) in pybank""")
        self.tstcon.commit()

    def tearDown(self):
        self.tstcon.rollback()
        with self.tstcon.cursor() as c:
            c.execute("drop table monkeyTable")
        self.tstcon.commit()

########################################################################
## Tests below
########################################################################

    def test_cursor_dml(self):
        cur = self.tstcon.cursor()
        for nu in range(0,2000):
            apa = random.randint(0,10)
            if (apa == 0):
                self.cursor_select(cur)
            elif (apa == 1):
                self.cursor_select_and_fetchone(cur)
            elif (apa == 2):
                self.cursor_select_and_fetchmany(cur, nu)
            elif (apa == 3):
                self.cursor_select_and_fetchall(cur)
            elif (apa == 4):
                self.cursor_insert_executemany(cur)
            elif (apa == 5):
                self.cursor_insert(cur)
            elif (apa == 6):
                self.cursor_insert_many(cur)
            elif (apa == 7):
                try:
                    self.cursor_next(cur)
                except StopIteration:
                    """Caught exception"""
            elif (apa == 8):
                self.cursor_commit(self.tstcon)
            elif (apa == 9):
                self.cursor_rollback(self.tstcon)
            elif (apa == 10):
                self.cursor_description_all(cur)
        cur.close()

    def test_cursor_ddl_and_dml(self):
        cur = self.tstcon.cursor()
        for nu in range(0,1000):
            apa = random.randint(0,15)
            if (apa == 0):
                try:
                    self.cursor_select(cur)
                except Exception:
                    """ Ok """
            elif (apa == 1):
                try:
                    self.cursor_select_and_fetchone(cur)
                except Exception:
                    """ Ok """
            elif (apa == 2):
                try:
                    self.cursor_select_and_fetchmany(cur, nu)
                except Exception:
                    """ Ok """

            elif (apa == 3):
                try:
                    self.cursor_select_and_fetchall(cur)
                except Exception:
                    """ Ok """
            elif (apa == 4):
                try:
                    self.cursor_insert_executemany(cur)
                except Exception:
                    """ Ok """
            elif (apa == 5):
                try:
                    self.cursor_insert(cur)
                except Exception:
                    """ Ok """
            elif (apa == 6):
                try:
                    self.cursor_insert_many(cur)
                except Exception:
                    """ Ok """
            elif (apa == 7):
                try:
                    self.cursor_next(cur)
                except Exception:
                    """Caught exception"""
            elif (apa == 8):
                try:
                    self.cursor_update(cur)
                except Exception:
                    """ Ok """
            elif (apa == 9):
                try:
                    self.monkey_insert(cur)
                except Exception:
                    """ Ok """
            elif (apa == 11):
                try:
                    self.monkey_select_and_fetchone(cur)
                except Exception:
                    """ Ok """
            elif (apa == 12):
                try:
                    self.cursor_delete(cur)
                except Exception:
                    """ Ok """
            elif (apa == 13):
                try:
                    self.cursor_commit(self.tstcon)
                except Exception:
                    """ Ok """
            elif (apa == 14):
                try:
                    self.cursor_rollback(self.tstcon)
                except Exception:
                    """ Ok """
            elif (apa == 15):
                try:
                    self.cursor_description_all(cur)
                except Exception:
                    """ Ok """
        cur.close()

    def test_condis(self):

        def condis(self):
            mylist = []
            for ac in range(5):
                con = mimerpy.connect(**db_config.TSTUSR)
                mylist.append([con, True])

            for a in range(100):
                rand = random.randint(0,4)
                if (not mylist[rand][1]):
                    mylist.pop(rand)
                    conn = mimerpy.connect(**db_config.TSTUSR)
                    mylist.append([conn, True])
                else:
                    mylist[rand][0].close()
                    mylist[rand][1] = False

            for ab in mylist:
                if (ab[1]):
                    ab[0].close()

        for i in range(9):
            t = threading.Thread(target = condis, args = (self,))
            t.start()
        while (threading.active_count() > 1):
            time.sleep(1)


########################################################################
## No Tests below
## Support routines follow
########################################################################


    def cursor_insert(self, cur):
        a = random.randint(-2**31, 2**31 - 1)
        b = random.randint(-2**63, 2**63 - 1)
        c = random.randint(-2**15, 2**15 - 1)
        d = str(uuid.uuid4())
        e = uuid.uuid4().bytes
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
            e = uuid.uuid4().bytes
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
        e = uuid.uuid4().bytes
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
