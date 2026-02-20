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

from . import mimerapi
import weakref
from .cursorPy import *
from .mimPyExceptionHandler import *
import sys


class _AutocommitHelper:
    """
    Helper class that allows autocommit to work both as a callable (backward
    compatible) and as a boolean value (PEP-249 compliant).
    """
    def __init__(self, connection):
        self._connection = connection

    def __bool__(self):
        return self._connection.autocommitmode

    def __call__(self, mode):
        """Backward compatible method-style: conn.autocommit(True)"""
        self._connection._set_autocommit(mode)

    def __eq__(self, other):
        return self._connection.autocommitmode == other

    def __repr__(self):
        return repr(self._connection.autocommitmode)


class _AutocommitDescriptor:
    """
    Descriptor that allows autocommit to be used both as a property
    (PEP-249: conn.autocommit = True) and as a method (backward compatible:
    conn.autocommit(True)).
    """
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return _AutocommitHelper(obj)

    def __set__(self, obj, value):
        obj._set_autocommit(value)


def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    """
    If cursor is not None, (errorclass, errorvalue) is appended to
    cursor.messages; otherwise it is appended to
    connection.messages. Then errorclass is raised with errorvalue as
    the value.
    You can override this with your own error handler by assigning it
    to the instance.
    """
#    sys.tracebacklimit = 1
    error = errorclass, errorvalue
    if cursor:
        cursor.messages.append(error)
    else:
        connection.messages.append(error)

    raise errorclass(errorvalue)


class Connection:

    """

        MimerSQL database connection

        The class Connection is used to establish
        a connection with a Mimer database.

    """

    autocommit = _AutocommitDescriptor()

    def __init__(self, dsn='', user='', password='',
                 autocommit=False, errorhandler=None):
        """
        Creates a database connection.

        Use the mimerpy.connect() function to create a connection rather than
        calling this function.
        """
        self.autocommitmode = autocommit
        self.errorhandler = (errorhandler if errorhandler
                             else defaulterrorhandler)
        self.messages = []
        self._session = None
        self.__cursors = weakref.WeakSet()
        self._transaction = False

        dsn = dsn if dsn else ""
        user = user if user else ""
        password = password if password else ""

        (self._session, rc) = mimerapi.mimerBeginSession8(dsn, user, password)
        if rc:
            if rc == 90:
                rc = -25031     # Login failure
            (ec, ev) = get_mimerapi_exception(rc, self._session)
            mimerapi.mimerEndSession(self._session)
            self._session = None
            self.errorhandler(self, None, ec, ev)


    def __enter__(self):
        return self

    def __exit__(self,type, value, traceback):
        self.__check_if_open()
        self.close()

    def __del__(self):
        if (not self._session == None):
            self.close()

    def close(self):
        """

            Closes the database connection.

            Method is used for closing a connection.
            When using close() all cursors that are
            using the connection are also closed.

            If the auto-commit feature is turned off
            and a connection is closed before committing
            any changes, an implicit rollback is executed.
            Thus, before evoking close(), commit() should
            be used to prevent any changes being lost. However,
            if auto-commit is turned on, an implicit rollback
            is not performed.

            When a connection has been closed using close(),
            it is unusable and a ProgrammingError() is raised
            if any operations are attempted on the connection.

        """
        if (not self._session == None):
            for cur in self.__cursors:
                cur.close()

            if (self._transaction):
                rc_value = mimerapi.mimerEndTransaction(self._session, 1)
                if (rc_value != -24101):
                    self.__check_mimerapi_error(rc_value, self._session)
                self._transaction = False
            rc_value = mimerapi.mimerEndSession(self._session)
            self.__check_mimerapi_error(rc_value, self._session)
            self._session = None

    def rollback(self):
        """

            Rolls back any pending transaction. Causes the database
            to roll back to the start of any pending transaction.
            If a connection is closed without committing any changes
            made during the transaction, a rollback is implicitly performed.

        """
        self.__check_if_open()
        if (self._transaction):
            rc_value = mimerapi.mimerEndTransaction(self._session, 1)
            self.__check_mimerapi_error(rc_value, self._session)
        self._transaction = False

    def commit(self):
        """Commits any pending transaction."""
        self.__check_if_open()
        if (self._transaction):
            rc_value = mimerapi.mimerEndTransaction(self._session, 0)
            self.__check_mimerapi_error(rc_value, self._session)
        self._transaction = False

    def cursor(self, **kwargs):
        """

            Returns a new Cursor Object using the connection.
            If scrollable is unspecified, the default cursor class
            will be returned. If scrollable = True a scrollable
            cursor will be returned.

        """
        self.__check_if_open()
        kwargs2 = kwargs.copy()
        mode = kwargs2.pop('scrollable', False)
        if (mode):
             curs = ScrollCursor(self, self._session)
        else:
             curs = Cursor(self, self._session)

        self.__cursors.add(curs)
        return curs

    def execute(self, *arg):
        """
            Creates a cursor and executes a database operation.

            arg
                query to execute

            Returns a new Cursor object using the connection and executes
            a database operation.

        """
        self.__check_if_open()
        curs = Cursor(self, self._session)
        self.__cursors.add(curs)
        curs.execute(*arg)
        return curs

    def executemany(self, *arg):
        """
            Creates a cursor and executes a database operation.

            arg
                query to execute and parameter sequences.

            Returns a new Cursor object using the connection and executes
            a database operation against all parameter sequences or mappings
            found in args.

        """
        self.__check_if_open()
        curs = Cursor(self, self._session)
        self.__cursors.add(curs)
        curs.executemany(*arg)
        return curs

    def _set_autocommit(self, mode):
        """
        Internal method to set autocommit mode.
        Use the autocommit property instead: conn.autocommit = True/False
        For backward compatibility, conn.autocommit(True/False) also works.
        """
        if mode:
            self.autocommitmode = True
            if self._transaction:
                self.rollback()
        else:
            self.autocommitmode = False

    def reset(self):
        """
        Reset the connection. Close all cursors and do rollback if a transaction
        is running. Reset auto commit to default.
        """
        if self.__cursors:
            for cur in self.__cursors:
                cur.close()
        
        if self._transaction:
            self.rollback()
        
        self.autocommit(False)

    def __raise_exception(self, rc):
        self.errorhandler(self, None, get_error_class(rc),
                          (rc, mimerpy_error[rc]))

    def __check_if_open(self):
        if (self._session == None):
            self.__raise_exception(-25010)

    def __check_mimerapi_error(self, rc, handle):
        if rc < 0:
            (ec, ev) = get_mimerapi_exception(rc, handle)
            self.errorhandler(self, None, ec, ev)

    def xid(self):
        self.__raise_exception(-25001)

    def tpc_begin(self):
        self.__raise_exception(-25001)

    def tpc_prepare(self):
        self.__raise_exception(-25001)

    def tpc_commit(self):
        self.__raise_exception(-25001)

    def tpc_rollback(self):
        self.__raise_exception(-25001)

    def tpc_recover(self):
        self.__raise_exception(-25001)
