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

from mimerpy.mimPyExceptionHandler import *
import mimerapi
import collections

get_funcs = {1: mimerapi.mimerGetString8, 2: mimerapi.mimerGetString8, 3: mimerapi.mimerGetString8, 6: mimerapi.mimerGetInt32,
             10: mimerapi.mimerGetDouble,
             11: mimerapi.mimerGetString8, 12: mimerapi.mimerGetString8, 13: mimerapi.mimerGetString8,
             14: mimerapi.mimerGetString8, 34: mimerapi.mimerGetBinary, 35: mimerapi.mimerGetBinary,
             39: mimerapi.mimerGetString8, 40: mimerapi.mimerGetString8,
             42: mimerapi.mimerGetBoolean, 48: mimerapi.mimerGetInt32, 50: mimerapi.mimerGetInt32, 52: mimerapi.mimerGetInt64,
             63: mimerapi.mimerGetString8,
             56: mimerapi.mimerGetDouble, 54: mimerapi.mimerGetDouble, 57: mimerapi.mimerGetBlobData,
             58: mimerapi.mimerGetNclobData8, 59: mimerapi.mimerGetNclobData8}
set_funcs = {1: mimerapi.mimerSetString8, 2: mimerapi.mimerSetString8, 3: mimerapi.mimerSetString8, 6: mimerapi.mimerSetInt32,
             10: mimerapi.mimerSetDouble,
             11: mimerapi.mimerSetString8, 12: mimerapi.mimerSetString8, 13: mimerapi.mimerSetString8,
             14: mimerapi.mimerSetString8, 34: mimerapi.mimerSetBinary, 35: mimerapi.mimerSetBinary,
             39: mimerapi.mimerSetString8,
             40: mimerapi.mimerSetString8, 42: mimerapi.mimerSetBoolean, 48: mimerapi.mimerSetInt32,
             50: mimerapi.mimerSetInt32, 52: mimerapi.mimerSetInt64, 63: mimerapi.mimerSetString8, 56: mimerapi.mimerSetDouble,
             54: mimerapi.mimerSetDouble,
             57: mimerapi.mimerSetBlobData, 58: mimerapi.mimerSetNclobData8, 59: mimerapi.mimerSetNclobData8,
             501: mimerapi.mimerSetNull}


class Cursor:
    """
        MimerSQL Cursor.

        The class cursor is used to execute MimerSQL statements and manage data result sets.

    """

    def __init__(self, connection, session):
        """
            Creates a cursor . For more information please visit
            http://developer.mimer.com/python.

            session
                reference to MimerSession sessionhandle.

        """
        self.connection = connection
        self.arraysize = 1
        self.rowcount = -1
        self.errorhandler = connection.errorhandler
        self.messages = []
        self.description = None

        self._number_of_parameters = None
        self._number_of_columns = None
        self._last_query = None
        self._DDL_rc_value = None

        self.__session = session
        self.__statement = None
        self.__mimcursor = False

    def __enter__(self):
        self.__check_if_open()
        return self

    def __exit__(self, type, value, traceback):
        self.connection.commit()
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        self.__check_if_open()
        return_value = self.fetchone()
        if return_value == []:
            raise StopIteration
        return return_value

    def __del__(self):
        self.close()

    def close(self):
        """
            Closes the cursor.

            From this point onwards the cursor is unusable and a
            ProgrammingError is raised if any operations are attempted
            on the connection.

        """
        self.__close_statement()
        self.__session = None

    def execute(self, *arg):
        """
            Executes a database operation.

            arg
                query to execute

            Executes a database operation.

        """
        rc_value = 0
        self.__check_if_open()
        self.__check_for_transaction()
        parameter_markers = ()

        # I would like to look over this at some point, the type control is not ideal - Erik 2018-10
        if (len(arg) > 1):
            if (isinstance(arg[1], dict)):
                parameter_markers = arg[1]
            # this is the problem, should be more strict on what the input can be - Erik 2018-10
            elif (not isinstance(arg[1], tuple) and (not isinstance(arg[1], list))):
                parameter_markers = [arg[1]]
            else:
                parameter_markers = arg[1]
        query = arg[0]


        # If same query is used twice there is not need for a new statement
        if (query != self._last_query or self.__mimcursor):
            self.__close_statement()
            values = mimerapi.mimerBeginStatement8(self.__session, query, 0)
            rc_value = values[0]
            self._DDL_rc_value = values[0]

            # -24005 indicates a DDL statement
            if (self._DDL_rc_value != -24005):
                self.__check_for_exception(rc_value, self.__session)
                self.__statement = values[1]

        self._last_query = query

        # Return value -24005 is given when a DDL query query is passed through
        # mimerBeginStatementC.
        if (self._DDL_rc_value == -24005):
            self.connection.transaction = False
            self.messages = []
            rc_value = mimerapi.mimerExecuteStatement8(self.__session, query)
            self.__check_for_exception(rc_value, self.__session)
        else:
            rc_value = mimerapi.mimerParameterCount(self.__statement)
            self.__check_for_exception(rc_value, self.__statement)

            # Return value of mimerParameterCount = 0 implies a query with no
            # parameters.
            if (rc_value > 0):
                self._number_of_parameters = rc_value
                try:

                    if (len(parameter_markers) != self._number_of_parameters):
                        self.__check_for_exception(-25103, "Invalid number of parameters")

                    # Column number starts a 1
                    for cur_column in range(1, self._number_of_parameters + 1):
                        parameter_type = mimerapi.mimerParameterType(self.__statement, cur_column)
                        self.__check_for_exception(parameter_type, self.__statement)

                        if (isinstance(parameter_markers, dict)):
                            rc_value, parameter_name = mimerapi.mimerParameterName8(self.__statement, cur_column)
                            self.__check_for_exception(rc_value, self.__statement)
                            if parameter_name in parameter_markers:
                                parameter = parameter_markers.get(parameter_name)
                                if (parameter == None):
                                    parameter_type = 501
                                rc_value = set_funcs[parameter_type](self.__statement, cur_column, parameter)
                            else:
                                self.__check_for_exception(-25108, "KeyError in parameters, key: " + str(parameter_name)
                                                           + " does not exist in dictionary")
                        else:
                            # If the parameter marker is None, we use mimerSetNull
                            if (parameter_markers[cur_column - 1] == None):
                                parameter_type = 501
                            rc_value = set_funcs[parameter_type](self.__statement,
                                                                       cur_column, parameter_markers[cur_column - 1])
                        self.__check_for_exception(rc_value, self.__statement)

                # Catching error for errorhandler
                except KeyError as e:
                    self.__check_for_exception(-28100, e)
                # Catching error for errorhandler
                except TypeError as e:
                    self.__check_for_exception(-25107, e)
                # Catching error for errorhandler
                except OverflowError as e:
                    self.__check_for_exception(-25107, e)

            self.__check_for_exception(rc_value, self.__statement)
            rc_value = mimerapi.mimerColumnCount(self.__statement)

            # Return value of mimerColumnCount <= 0 implies a query with no
            # result set.
            if (rc_value <= 0):
                self.__check_for_exception(rc_value, self.__statement)
                self.messages = []
                rc_value = mimerapi.mimerExecute(self.__statement)
                self.__check_for_exception(rc_value, self.__statement)
                self.rowcount = rc_value
            else:
                # Return value of mimerColumnCount > 0 implies a query with a
                # result set.
                self.rowcount = rc_value
                self._number_of_columns = rc_value
                rc_value = mimerapi.mimerOpenCursor(self.__statement)
                self.__check_for_exception(rc_value, self.__statement)
                self.__mimcursor = True
                description = collections.namedtuple('Column_description',
                                                     'name type_code display_size internal_size precision scale null_ok')
                self.description = ()

                for cur_column in range(1, self._number_of_columns + 1):
                    func_tuple = mimerapi.mimerColumnName8(self.__statement, cur_column)
                    rc_value = func_tuple[0]
                    self.__check_for_exception(rc_value, self.__statement)
                    name = func_tuple[1]
                    rc_value = mimerapi.mimerColumnType(self.__statement, cur_column)
                    self.__check_for_exception(rc_value, self.__statement)
                    type_code = rc_value
                    self.description = self.description + (description(name=name,
                                                                       type_code=type_code,
                                                                       display_size=None,
                                                                       internal_size=None,
                                                                       precision=None,
                                                                       scale=None,
                                                                       null_ok=None),)

    def executemany(self, query, params):
        """
            Executes a database operation.

            query
                query with parameter markers to execute.

            params
                sequence of parameters.

            Executes a database operation against all parameter sequences or mappings
            found in params.

        """
        self.__check_if_open()
        self.__check_for_transaction()
        rc_value = 0
        self._last_query = None
        values = []

        # I would like to look over this at some point
        # Checking for invalid parameter structure
        if (not isinstance(params, tuple) and not isinstance(params, list)):
            self.__check_for_exception(-26001, "Invalid parameter format")

        else:
            if (not isinstance(params[0], tuple) and not isinstance(params[0], dict)):
                self.__check_for_exception(-26001, "Invalid parameter format")

        self.__close_statement()
        values = mimerapi.mimerBeginStatement8(self.__session, query, 0)
        rc_value = values[0]

        self.__check_for_exception(rc_value, self.__session)
        self.__statement = values[1]
        self.__check_for_exception(rc_value, self.__statement)

        rc_value = mimerapi.mimerParameterCount(self.__statement)
        self._number_of_parameters = rc_value

        self.rowcount = 0
        self.__check_for_exception(rc_value, self.__statement)

        try:
            for laps in range(0, len(params)):
                cur_param = params[laps]

                # Column number starts a 1
                for cur_column in range(1, self._number_of_parameters + 1):
                    parameter_type = mimerapi.mimerParameterType(self.__statement, cur_column)
                    self.__check_for_exception(parameter_type, self.__statement)

                    if (isinstance(cur_param, dict)):
                        rc_value, parameter_name = mimerapi.mimerParameterName8(self.__statement, cur_column)
                        self.__check_for_exception(rc_value, self.__statement)
                        if parameter_name in cur_param:
                            parameter = cur_param.get(parameter_name)
                            if (parameter == None):
                                parameter_type = 501
                            rc_value = set_funcs[parameter_type](self.__statement, cur_column, parameter)
                        else:
                            self.__check_for_exception(-25108, "KeyError in parameters, key: " + str(parameter_name)
                                                       + ", does not exist in dictionary")
                    else:
                        # If the parameter marker is None, we use mimerSetNull
                        if (cur_param[cur_column - 1] == None):
                            parameter_type = 501
                        rc_value = set_funcs[parameter_type](self.__statement,
                                                                   cur_column, cur_param[cur_column - 1])
                self.messages = []

                # Batching after all parameters are set
                if (laps != len(params) - 1):
                    rc_value = mimerapi.mimerAddBatch(self.__statement)
                    self.__check_for_exception(rc_value, self.__statement)
                self.rowcount = self.rowcount + rc_value

            rc_value = mimerapi.mimerExecute(self.__statement)
            self.__check_for_exception(rc_value, self.__statement)

        # Catching error for errorhandler
        except TypeError as e:
            self.__check_for_exception(-25107, e)
        # Catching error for errorhandler
        except OverflowError as e:
            self.__check_for_exception(-25107, e)

    def fetchone(self):
        """
            Fetch next row of a query result set.

            The row is returned as a tuple. If no more data is available,
            None is returned. If fetchone is called and the previous call
            to execute did not produce a result set, a ProgrammingError
            is raised.

        """
        self.__check_if_open()
        self.__check_for_transaction()

        if (not self.__mimcursor):
            self.__check_for_exception(-25107, "Previous execute did not produce any result set")

        rc_value = mimerapi.mimerFetch(self.__statement)
        self.__check_for_exception(rc_value, self.__statement)
        return_tuple = ()

        # Return value of mimerFetch == 100 implies end of result set
        if (rc_value == 100):
            return []

        for cur_column in range(1, self._number_of_columns + 1):
            rc_value = mimerapi.mimerColumnType(self.__statement, cur_column)
            self.__check_for_exception(rc_value, self.__statement)
            func_tuple = get_funcs[rc_value](self.__statement, cur_column)
            self.__check_for_exception(func_tuple[0], self.__statement)

            # Conversion from C int to Python boolean
            if (rc_value == 42 and not func_tuple[1] == None):
                if (func_tuple[1] == 0):
                    return_tuple = return_tuple + (False,)
                else:
                    return_tuple = return_tuple + (True,)
            else:
                return_tuple = return_tuple + (func_tuple[1],)

        return return_tuple

    def fetchmany(self, *arg):
        """Fetch next row of a query result set.

        arg
            sets the arraysize

        The number of rows to fetch per call is specified by the parameter.
        If it is not given, the cursor's arraysize determines the number of
        rows to be fetched. The method should try to fetch as many rows as
        indicated by the size parameter. If this is not possible due to the
        specified number of rows not being available, fewer rows may be returned.
        Arraysize is retained after each call to fetchmany.

        """
        values = []
        return_tuple = ()

        self.__check_if_open()
        self.__check_for_transaction()

        if (not self.__mimcursor):
            self.__check_for_exception(-25107, "Previous execute did not produce any result set")

        # If arg is provided, arraysize is set
        if (len(arg) > 0):
            self.arraysize = arg[0]

        fetch_length = self.arraysize
        rc_value = mimerapi.mimerFetch(self.__statement)
        fetch_value = rc_value
        while (fetch_value != 100 and fetch_length > 0):
            self.__check_for_exception(fetch_value, self.__statement)
            return_tuple = ()
            # Column number starts a 1
            for cur_column in range(1, self._number_of_columns + 1):
                rc_value = mimerapi.mimerColumnType(self.__statement, cur_column)
                self.__check_for_exception(rc_value, self.__statement)
                func_tuple = get_funcs[rc_value](self.__statement, cur_column)
                self.__check_for_exception(func_tuple[0], self.__statement)

                # Conversion from C int to Python boolean
                if (rc_value == 42 and not func_tuple[1] == None):
                    if (func_tuple[1] == 0):
                        return_tuple = return_tuple + (False,)
                    else:
                        return_tuple = return_tuple + (True,)
                else:
                    return_tuple = return_tuple + (func_tuple[1],)

            values.append(return_tuple)
            fetch_length = fetch_length - 1
            fetch_value = mimerapi.mimerFetch(self.__statement)
        return values

    def fetchall(self):
        """
            Fetch all (remaining) row of a query result set.

            The rows are returned as a list of tuples. If no more data is
            available, an empty list is returned. If fetchall is called and
            the previous call to execute did not produce a result set,
            a ProgrammingError is raised.

        """
        self.__check_if_open()
        self.__check_for_transaction()
        if (not self.__mimcursor):
            self.__check_for_exception(-25107, "Previous execute did not produce any result set")
        values = []
        rc_value = mimerapi.mimerFetch(self.__statement)
        fetch_value = rc_value
        while (fetch_value != 100):
            self.__check_for_exception(fetch_value, self.__statement)
            return_tuple = ()
            # Column number starts a 1
            for cur_column in range(1, self._number_of_columns + 1):
                rc_value = mimerapi.mimerColumnType(self.__statement, cur_column)
                self.__check_for_exception(rc_value, self.__statement)
                func_tuple = get_funcs[rc_value](self.__statement, cur_column)
                self.__check_for_exception(func_tuple[0], self.__statement)

                # Conversion from C int to Python boolean
                if (rc_value == 42 and not func_tuple[1] == None):
                    if (func_tuple[1] == 0):
                        return_tuple = return_tuple + (False,)
                    else:
                        return_tuple = return_tuple + (True,)
                else:
                    return_tuple = return_tuple + (func_tuple[1],)

            values.append(return_tuple)
            fetch_value = mimerapi.mimerFetch(self.__statement)
        return values

    def setinputsizes(self):
        """Does nothing but required by the DB API."""

    def setoutputsizes(self):
        """Does nothing but required by the DB API."""

    def next(self):
        """
            Returns the next row in a result set, with the same semantics
            as fetchone. If there is no more data available in the result
            set, a StopIteration exception is raised.

        """
        return_tuple = self.fetchone()
        if (return_tuple):
            return return_tuple
        else:
            raise StopIteration

    def __close_statement(self):
        # Private method for closing MimerStatement.
        if (self.__statement != None):
            rc_value = mimerapi.mimerEndStatement(self.__statement)
            self.__statement = None
            self.__mimcursor = False
            self.__check_for_exception(rc_value, self.__statement)

    def __check_if_open(self):
        if (self.__session == None):
            self.__check_for_exception(-25000, "Cursor not open")

    def __check_for_transaction(self):
        if (not self.connection._transaction and not self.connection.autocommitmode):
            rc_value = mimerapi.mimerBeginTransaction(self.__session)
            self.__check_for_exception(rc_value, self.__session)
            self.connection._transaction = True

    def __check_for_exception(self, *arg):
        error_tuple = check_for_exception(arg[0], arg[1])
        if (isinstance(error_tuple, tuple)):
            if (error_tuple[0]):
                self.errorhandler(None, self, error_tuple[0], (error_tuple[1]))

    def nextset(self):
        self.__check_for_exception(-28002, "Not suppported")

    def callproc(self):
        self.__check_for_exception(-28003, "Not suppported")


class ScrollCursor(Cursor):
    """
        Subclass to the Cursor-class where the cursor can be scrolled to
        new positions in the result set.

    """

    def __init__(self, connection, session):
        super(ScrollCursor, self).__init__(connection, session)
        self.__result_set = None
        self.rownumber = None

    def execute(self, *arg):
        """
            Executes a database operation.

            arg
                query to execute

            Executes a database operation.

        """
        super(ScrollCursor, self).execute(*arg)

        # If a resulet set is produced, it is fetched.
        if (self._Cursor__mimcursor):
            self.__result_set = super(ScrollCursor, self).fetchall()
            self.rowcount = len(self.__result_set)
            self.rownumber = 0
        else:
            self.__result_set = None

    def fetchone(self):
        """
            Fetch next row of a query result set.

            The row is returned as a tuple. If no more data is available,
            None is returned. If fetchone is called and the previous call
            to execute did not produce a result set, a ProgrammingError
            is raised.

        """
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()

        if (self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        values = ()
        try:
            values = values + self.__result_set[self.rownumber]
            self.rownumber = self.rownumber + 1
        except IndexError:
            return []
        return values

    def fetchmany(self, *arg):
        """
            Fetch next row of a query result set.

            arg
                sets the arraysize

            The number of rows to fetch per call is specified by the parameter.
            If it is not given, the cursor's arraysize determines the number of
            rows to be fetched. The method should try to fetch as many rows as
            indicated by the size parameter. If this is not possible due to the
            specified number of rows not being available, fewer rows may be returned.
            Arraysize is retained after each call to fetchmany.

        """
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()

        if (self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")

        if (len(arg) > 0):
            self.arraysize = arg[0]

        fetch_size = self.arraysize
        values = []

        while (fetch_size):
            try:
                values.append(self.__result_set[self.rownumber])
                fetch_size = fetch_size - 1
                self.rownumber = self.rownumber + 1
            except IndexError:
                break
        return values

    def fetchall(self):
        """
            Fetch all (remaining) row of a query result set.

            The rows are returned as a list of tuples. If no more data is
            available, an empty list is returned. If fetchall is called and
            the previous call to execute did not produce a result set,
            a ProgrammingError is raised.

        """
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()
        values = []
        if (self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        if (not self.rownumber):
            self.rownumber = len(self.__result_set)
            return self.__result_set
        else:
            values = self.__result_set[self.rownumber:len(self.__result_set)]
            self.rownumber = len(self.__result_set)
            return values

    def next(self):
        """
            Returns the next row in a result set, with the same semantics
            as fetchone. If there is no more data available in the result
            set, a StopIteration exception is raised.

        """
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()

        if (self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        if (self.__result_set == []):
            return self.__result_set

        values = ()
        try:
            values = values + self.__result_set[self.rownumber]
            self.rownumber = self.rownumber + 1
        except IndexError:
            raise StopIteration
        return values

    def scroll(self, value, mode='relative'):
        """
            Method scrolls the cursor to a new position according to the
            mode of the scroll.

            The mode of the cursor is set to relative by default. This
            changes the cursor’s position by value number of rows in
            relation to the current position of the cursor. If mode is
            set to absolute the cursor is moved value number of rows down
            from the absolute position.

            If the method is called upon and desired position in the result
            set does not exist, an IndexError is raised.

        """
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()

        if (mode == 'relative'):
            new_row = self.rownumber + value
            if (new_row >= len(self.__result_set)):
                raise IndexError
            else:
                self.rownumber = new_row
        elif (mode == 'absolute'):
            if (value >= len(self.__result_set)):
                raise IndexError
            else:
                self.rownumber = value
        else:
            self._Cursor__check_for_exception(-25000, "Not a possible scroll mode")
