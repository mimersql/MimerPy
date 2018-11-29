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

try:
    from exceptions import Exception, StandardError, Warning
except ImportError:
    # for Python3 
    StandardError = Exception

class Warning(StandardError):

    """
        Exception raised for important warnings like data truncations
        while inserting, etc.

    """
    def __init__(self, message):
        self.message = message

class Error(StandardError):

    """
        Exception that is the base class of all other error exceptions.
        Can be used to catch all errors with one single except statement.

    """
    def __init__(self, message):
        self.message = message

class InterfaceError(Error):

    """
        Exception raised for errors that are related to the database
        interface rather than the database itself. For example if a
        parameter is specified in the wrong format.

    """

class DatabaseError(Error):

    """
        Exception raised for errors that are related to the database.

    """

class DataError(DatabaseError):

    """
        Exception raised for errors that are due to problems with the
        processed data like division by zero, numeric value out of range, etc.

    """

class OperationalError(DatabaseError):

    """
        Exception raised for errors that are related to the database’s
        operation and not necessarily under the control of the programmer,
        e.g. an unexpected disconnect occurs, the data source name is not
        found, a transaction could not be processed, a memory allocation
        error occurred during processing, etc.

    """

class IntegrityError(DatabaseError):

    """
        Exception raised when the relational integrity of the database
        is affected, e.g. a foreign key check fails.

    """

class InternalError(DatabaseError):

    """
        Exception raised when the database encounters an internal error,
        e.g. the cursor is not valid anymore, the transaction is out of
        sync, etc.

    """

class ProgrammingError(DatabaseError):

    """
        Exception raised for programming errors, e.g. table not found
        or already exists, syntax error in the SQL statement, wrong
        number of parameters specified, etc.

    """


class NotSupportedError(DatabaseError):

    """
        Exception raised in case a method or database API was used which
        is not supported by the database.

    """
