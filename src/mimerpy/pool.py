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

"""Connection pooling for MimerPy connections.

Usage:

Start by setting up the connection pool by creating
an instance of MimerPool with the following parameters (most are optional):

initialconnections: initial number of idle connections in the pool (Default: 0)
maxunused: maximum number of unused connections in the pool (Default: 0, unlimited pool size)
maxconnections: maximum number of connections allowed (Default: 0, unlimited number of connections)
block: determines behavior when exceeding the maximum number of connections. 
    If True, block and wait for a connection to become available
    (Default: False, will give error when maxconnections is exceeded)
deep_health_check: Don't only check that the connection seems to be ok, try it before getting it from the pool.
    This is a bit slower but guarantees that the connection is healty. Default True
dsn: The database name. If empty, MIMER_DATABASE is used
user: The database username
password: The database password
autocommit: Autocommit mode
errorhandler: Custom errorhandler

Example: If you want a pool of at least ten connections using the database 'mimerdb':

    from mimerpy import mimerapi 
    from MimerPool import MimerPool
    pool = MimerPool('mimerdb', 'username', 'password', 10)
    or
    pool = MimerPool(dsn='mimerdb', username='username', password='password', initialconnections=
    10)
Now you can getting connections and working with them as usual with the only difference than close()
will not actually close the connections but rather return them to the pool.
    conn = pool.get_connection()

    ...Do your work
    conn.close() #This will not necesarily close the connection, but it might depending on how the pool is configured

"""

from threading import Condition
from mimerpy import mimerapi
from mimerpy.connectionPy import Connection


class MimerPoolError(Exception):
    """General MimerPool error."""


class MimerPoolExhausted(MimerPoolError):
    """Too many database connections were opened."""


class MimerPool:
    """The connection pool class.

    After you have created the connection pool, you can use
    get_connection() to get pooled MimerPy connections.

    """

    def __init__(
            self, dsn:str = '', user:str = '', password:str ='', initialconnections:int = 0, maxunused:int = 0, maxconnections:int = 0, block:bool = False,
            deep_health_check:bool = False, autocommit:bool = False, errorhandler=None):
        """Set up the MimerPy connection pool.

        Args:
            initialconnections(str): initial number of idle connections in the pool (Default: 0)
            maxunused(int): maximum number of unused connections in the pool (Default: 0, unlimited pool size)
            maxconnections(int): maximum number of connections allowed (Default: 0, unlimited number of connections)
            block(bool): determines behavior when exceeding the maximum number of connections. 
                If True, block and wait for a connection to become available
                (Default: False, will give error when maxconnections is exceeded)
            deep_health_check(bool): Don't only check that the connection seems to be ok, try it before getting it from the pool.
                This is a bit slower but guarantees that the connection is healty. Default False
            dsn(str): The database name
            user(str): The database username
            password(str): The database password
            autocommit(bool): Autocommit mode
            errorhandler: Custom errorhandler

        Returns:
            An initialized MimerPool

        """
        self._dsn = dsn
        self._user = user
        self._password = password
        self._autocommit = autocommit
        self._errorhandler = errorhandler
        self._block = block
        self._initialconnections = initialconnections
        self._deep_health_check = deep_health_check
        if maxunused > 0 and maxunused < initialconnections:
            self._maxunused = initialconnections
        else:
            self._maxunused = maxunused
        if maxconnections > 0 and maxconnections < self._maxunused:
            self._maxconnections = self._maxunused
        else:
            self._maxconnections = maxconnections
        self.__cached_connections = []  # The connection pool
        self.__used_connections = [] # Used connections
        self.__pool_lock = Condition()
        # Start initial connections if any
        initial_cons = [self.get_connection() for cnt in range(initialconnections)]
        while initial_cons:
            self.store_or_close(initial_cons.pop())

    @property
    def cached_connections(self):
        """The number of available connections in the pool."""
        return len(self.__cached_connections)

    @property
    def used_connections(self):
        """The number of used connections."""
        return len(self.__used_connections)

    @property
    def connections(self):
        """Total number of active connections."""
        return len(self.__used_connections) + len(self.__cached_connections)

    def get_connection(self):
        """Get a pooled MimerPy connection.

        Returns:
            A PooledConnection that can be used as a standard MimerPy Connection

        """
        self.__pool_lock.acquire()
        try:
            if self._block and self._maxconnections > 0:
                while self.used_connections >= self._maxconnections:
                    self.__pool_lock.wait()
            elif self._maxconnections > 0 and self.used_connections >= self._maxconnections:
                raise MimerPoolExhausted
            # Connection limit not reached, get a connection
            # Try to get it from the connection pool
            if len(self.__cached_connections) > 0:
                con = self.__cached_connections.pop(0)
                if not con.is_open():
                    #The connection is not healthy, throw it away and create a new one
                    con = PooledConnection(self)
                elif con._transaction:
                    con.rollback()
                self.__used_connections.append(con)
            else:  # No more connections in the pool, create a new one
                con = PooledConnection(self)
                self.__used_connections.append(con)
        finally:
            self.__pool_lock.release()

        return con

    def store_or_close(self, con):
        """Put a connection back into the pool or close it if the cache is full/big enough.

        Args:
            con(PooledConnection): The connection to put back into the pool.

        """
        self.__pool_lock.acquire()
        try:
            #Only cache connections that are ok
            if con.is_open() and (
                not self._maxunused or (
                    len(self.__cached_connections) < self._maxunused and self.connections <= self._maxconnections)
            ):
                con.reset()
                con.autocommit(self._autocommit) # Set autocommit back to how the pool was at setup
                # The connection pool is not full, so append it to the pool and keep it alive
                self.__cached_connections.append(con)
            else:  # The connection pool is full, close the connection and discard it.
                con._close()
            self.__used_connections.remove(con)
            self.__pool_lock.notify()
        finally:
            self.__pool_lock.release()

    def close(self):
        """Close all connections in the pool."""
        self.__pool_lock.acquire()
        try:
            while self.__cached_connections:  # Close all connections in the pool
                con = self.__cached_connections.pop(0)
                try:
                    con._close()
                except Exception:
                    pass
            while self.__used_connections:  # Close all connections that haven't been returned
                con = self.__used_connections.pop(0)
                try:
                    con._close()
                except Exception:
                    pass
            self.__pool_lock.notify_all()
        finally:
            self.__pool_lock.release()

    def __del__(self):
        """Delete the pool."""
        try:
            self.close()
        except Exception:
            pass

    def __enter__(self):
        """Support for the with statement

        Returns:
            MimerPool: The connection pool itself
        """
        return self

    def __exit__(self,type, value, traceback):
        """Support for the with statement

        Close all connections
        """
        self.close()

class PooledConnection(Connection):
    """The mimerpy.Connection wrapper class that override the close method."""

    def __init__(self, pool: MimerPool):
        """ Create a PooledConnection.

        This will also open the actual connection to the database and the pool will start manage the connection

        Args:
            pool(MimerPool): The connection pool that manages the connection
        """
        super().__init__(dsn = pool._dsn, user = pool._user, password = pool._password, autocommit = pool._autocommit, errorhandler = pool._errorhandler)
        #Create a MimerPy connection

        #Keep track of the pool so we can put the connection back
        self._pool = pool

    def close(self):
        """Close the pooled connection.

        Instead of actually closing the connection, return it to the pool for future reuse.
        """
        self._pool.store_or_close(self)

    def _close(self):
        """Truly close the connection"""
        super().close()

    def is_open(self):
        #if not super().is_open():
        if self._session is None: 
            return False
        else:
            if self._pool._deep_health_check:
                try:
                    cur = self.execute("select m from system.onerow")
                    r = cur.fetchone()
                    cur.close()
                    if self.autocommitmode != True:
                        self.rollback()
                    if r:
                        return True
                    else:
                        return False
                except(Exception):
                    return False
            else:
                return True

    def __del__(self):
        """Delete the pooled connection."""
        try:
            self.close()
        except Exception:
            pass
    
    def __enter__(self):
        """Support for the with statement

        Returns:
            PooledConnection: The connection itself
        """
        return self

    def __exit__(self,type, value, traceback):
        """Support for the with statement
        """
        self.close()
