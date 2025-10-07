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
import mimerpy
import sys
import pathlib
import db_config

#To be able to run without installing the package
m_path = str(pathlib.Path(__file__).parent.parent.absolute())
sys.path.append(m_path)


from mimerpy.pool import (
    MimerPool, MimerPoolError, MimerPoolExhausted)

__version__ = '1.0'

class TestMimerPool(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        (self.syscon, self.tstcon) = db_config.setup()
        self.DSN = db_config.TSTUSR['dsn']
        self.USER = db_config.TSTUSR['user']
        self.PASSWORD = db_config.TSTUSR['password']

    @classmethod
    def tearDownClass(self):
        db_config.teardown(tstcon=self.tstcon, syscon=self.syscon)


    def test_pool1_CreateConnection(self):
        pool = MimerPool(
            initialconnections=1, maxunused=2, maxconnections=3, block=False,
            dsn=self.DSN, user=self.USER, password=self.PASSWORD)
        self.assertEqual(pool.cached_connections, 1)
        con = pool.get_connection()
        from mimerpy.pool import PooledConnection
        self.assertTrue(isinstance(con, PooledConnection))
        con.close()
        db = pool.get_connection()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 1)
        db2 = pool.get_connection()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 2)
        db3 = pool.get_connection()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 3)
        db.autocommit(True)
        cur = db.execute('select * from system.onerow')
        r = cur.fetchone()
        cur.close()
        db.close()
        self.assertEqual(pool.cached_connections, 1)
        self.assertEqual(pool.used_connections, 2)
        db2.close()
        self.assertEqual(pool.cached_connections, 2)
        self.assertEqual(pool.used_connections, 1)
        db3.close()
        self.assertEqual(pool.cached_connections, 2)
        self.assertEqual(pool.used_connections, 0)
        db = pool.get_connection()
        self.assertEqual(pool.cached_connections, 1)
        self.assertEqual(pool.used_connections, 1)
        pool.close()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 0)
        pool = None

    def test_pool2_CreateConnectionNoMaxCache(self):
        pool = MimerPool(
            initialconnections=1, maxunused=0, maxconnections=3, block=False,
            dsn=self.DSN, user=self.USER, password=self.PASSWORD)
        del(pool)
        pool = MimerPool(
            initialconnections=1, maxunused=0, maxconnections=3, block=False,
            dsn=self.DSN, user=self.USER, password=self.PASSWORD)
        self.assertEqual(pool.cached_connections, 1)
        self.assertEqual(pool.used_connections, 0)
        con = pool.get_connection()
        from mimerpy.pool import PooledConnection
        self.assertTrue(isinstance(con, PooledConnection))
        con.close()
        db = pool.get_connection()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 1)
        db2 = pool.get_connection()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 2)
        db3 = pool.get_connection()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 3)
        db.autocommit(True)
        cursor = db.cursor()
        cursor.execute('select * from system.onerow')
        r = cursor.fetchone()
        cursor.close()
        db.close()
        self.assertEqual(pool.cached_connections, 1)
        self.assertEqual(pool.used_connections, 2)
        db2.close()
        self.assertEqual(pool.cached_connections, 2)
        self.assertEqual(pool.used_connections, 1)
        db3.close()
        self.assertEqual(pool.cached_connections, 3)
        self.assertEqual(pool.used_connections, 0)
        pool.close()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 0)

    def test_pool3_CreateManyConnections(self):
        #See how many connections the database allows, but no more than max_cons
        max_cons = 100
        available_cons = 0
        cons = []
        try:
            while True and available_cons < max_cons:
                c = mimerpy.connect(dsn = self.DSN, user=self.USER, password=self.PASSWORD)
                cons.append(c)
                available_cons = available_cons +1
        except (mimerpy.mimPyExceptions.OperationalError):
            pass
        finally:
            for c in cons:
                c.close()                
                
        self.assertGreaterEqual(available_cons, 50, "50 available connections ore more needed")
        pool = MimerPool(
            initialconnections=5, maxunused=0, maxconnections=10, block=False,
            dsn=self.DSN, user=self.USER, password=self.PASSWORD)
        self.assertEqual(pool.cached_connections, 5)
        self.assertEqual(pool.used_connections, 0)

        cons = [pool.get_connection() for cnt in range(10)]
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 10)

        for con in cons:
            con.close()

        self.assertEqual(pool.cached_connections, 10)
        self.assertEqual(pool.used_connections, 0)

        cons = [pool.get_connection() for cnt in range(10)]
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 10)
        self.assertRaises(MimerPoolExhausted, pool.get_connection)
        pool.close()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 0)
        del pool

        pool = MimerPool(
            initialconnections=5, maxunused=0, maxconnections=available_cons+1, block=False,
            dsn=self.DSN, user=self.USER, password=self.PASSWORD)
        #This will be slow since we have to create all the connection
        cons = [pool.get_connection() for cnt in range(available_cons)]
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, available_cons)

        for con in cons:
            con.close()

        self.assertEqual(pool.cached_connections, available_cons)
        self.assertEqual(pool.used_connections, 0)
        #This will be quick since the connections are already open
        cons = [pool.get_connection() for cnt in range(available_cons)]
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, available_cons)
        
        self.assertRaises(mimerpy.mimPyExceptions.OperationalError, pool.get_connection)
        for con in cons:
            con.close()

        self.assertEqual(pool.cached_connections, available_cons)
        self.assertEqual(pool.used_connections, 0)

        pool.close()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 0)

    def test_pool4_PoolWithStatement(self):
        with MimerPool(initialconnections=1, maxunused=2, maxconnections=3, block=False,
                dsn=self.DSN, user=self.USER, password=self.PASSWORD) as pool:
            self.assertEqual(pool.cached_connections, 1)
            con = pool.get_connection()
            from mimerpy.pool import PooledConnection
            self.assertTrue(isinstance(con, PooledConnection))
            con.close()
            db = pool.get_connection()
            self.assertEqual(pool.cached_connections, 0)
            self.assertEqual(pool.used_connections, 1)
            db2 = pool.get_connection()
            self.assertEqual(pool.cached_connections, 0)
            self.assertEqual(pool.used_connections, 2)
            db3 = pool.get_connection()
            self.assertEqual(pool.cached_connections, 0)
            self.assertEqual(pool.used_connections, 3)
            db.autocommit(True)
            cur = db.execute('select * from system.onerow')
            r = cur.fetchone()
            cur.close()
            db.close()
            self.assertEqual(pool.cached_connections, 1)
            self.assertEqual(pool.used_connections, 2)
            db2.close()
            self.assertEqual(pool.cached_connections, 2)
            self.assertEqual(pool.used_connections, 1)
            db3.close()
            self.assertEqual(pool.cached_connections, 2)
            self.assertEqual(pool.used_connections, 0)
            db = pool.get_connection()
            self.assertEqual(pool.cached_connections, 1)
            self.assertEqual(pool.used_connections, 1)
 
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 0)
 
    def test_pool5_PoolConnectionWithStatement(self):
        pool = MimerPool(
            initialconnections=1, maxunused=2, maxconnections=3, block=False,
            dsn=self.DSN, user=self.USER, password=self.PASSWORD)
        self.assertEqual(pool.cached_connections, 1)
        with pool.get_connection() as con:
            from mimerpy.pool import PooledConnection
            self.assertTrue(isinstance(con, PooledConnection))

        db2 = None
        with pool.get_connection() as db:
            self.assertEqual(pool.cached_connections, 0)
            self.assertEqual(pool.used_connections, 1)
            db2 = pool.get_connection()
            self.assertEqual(pool.cached_connections, 0)
            self.assertEqual(pool.used_connections, 2)
            cur = db.execute('select * from system.onerow')
            r = cur.fetchone()
            cur.close()

        self.assertEqual(pool.cached_connections, 1)
        self.assertEqual(pool.used_connections, 1)
        db2.close()
        self.assertEqual(pool.cached_connections, 2)
        self.assertEqual(pool.used_connections, 0)

        pool.close()
        self.assertEqual(pool.cached_connections, 0)
        self.assertEqual(pool.used_connections, 0)

if __name__ == '__main__':
    unittest.main()
