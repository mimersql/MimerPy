/* *********************************************************************/
/**
* Copyright (c) 2017 Mimer Information Technology
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* See license for more details.
 */
/* *********************************************************************/

/* *********************************************************************/
/**
 *   @brief   C interface for accessing Mimer from Python
 *
 *   @file
 *
 *   @par   File information
 *          - Mimer Information Technology
 *          - System:    Mimer SQL
 *          - Module:    DRIVERS
 *          - Submodule: MIMERPY
 */
/* *********************************************************************/

// #define Py_LIMITED_API  ???

#include "Python.h"
#include "mimerapi.h"

/**
 * We must pass pointers between the C layer and Python. We use the "L"
 * format character which specified the "long long" C type.
 */
typedef long long pyptr;


/**
 *  Size of default buffer that is allocated on stack. If the buffer is not
 *  enough, a larger buffer will be allocated with malloc().
 *  The size is large enough to be usable in most cases and small enough to not
 *  waste cycles filling a too small buffer.
 */
#define BUFLEN 128



/**
 *  Internal constant to document that something is done because of the size of
 *  the terminating NUL, rather than using an ambiguous numerical value.
 */
static const int lengthof_Terminating_NUL = 1;



static PyObject* mimerBeginSession8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Starts a session with the database.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in]     args       Arguments.
 *                 args 1:    Name of database.
 *                 args 2:    Name of ident.
 *                 args 3:    Password.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 */
/* *********************************************************************/
{
    int rc;
    char *db_name, *user, *password;
    MimerSession session;

    if (!PyArg_ParseTuple(args, "sss", &db_name, &user, &password)) {
        return NULL;
    }

    rc = MimerBeginSession8(db_name, user, password, &session);

    return Py_BuildValue("Li", (pyptr)session, rc);
}



static PyObject* mimerEndSession(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Ends a database session.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in,out] args       Arguments.
 *                 args 1:    Sessionhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    If there are any active transactions, these are
 *              rollbacked.
 */
/* *********************************************************************/
{
    int rc;
    pyptr session;

    if (!PyArg_ParseTuple(args, "L", &session)) {
        return NULL;
    }

    rc = MimerEndSession((MimerSession*)&session);

    return Py_BuildValue("i", rc);
}



static PyObject* mimerBeginTransaction(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Starts a transaction.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in,out] args       Arguments.
 *                 args 1:    Sessionhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    This routine only needs to be called if two or more
 *              database operations should participate in the
 *              transaction.
 */
/* *********************************************************************/
{
    int rc;
    pyptr session;

    if (!PyArg_ParseTuple(args, "L", &session)){
        return NULL;
    }

    rc = MimerBeginTransaction((MimerSession)session, 0);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerEndTransaction(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Commmits or rollbacks a transaction.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in,out] args       Arguments.
 *                 args 1:    Sessionhandle.
 *                 args 2:    Integer specifying transaction operation.
 *                            0 for commit or 1 for rollback.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    Open cursors are automatically closed.
 */
/* *********************************************************************/
{
    int rc, commit_rollback;
    pyptr session;

    if (!PyArg_ParseTuple(args, "Li", &session, &commit_rollback)) {
        return NULL;
    }

    rc = MimerEndTransaction((MimerSession)session, commit_rollback);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerBeginStatement8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Prepares an SQL statement for execution.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in] args           Arguments.
 *                 args 1:    Sessionhandle.
 *                 args 2:    SQL statement to execute.
 *                 args 3:    Specifies a cursor being scrollable, or forward
 *                            only. 0 indicate forward only, 1 scrollable.
 *
 *  @returns    Tuple.
 *              Tuple[0]: Return code 0 = OK, < 0 if error.
 *              Tuple[1]: Statmenthandle.
 *
 *  @remarks    Between the preparation and the time of execution, the
 *              the application may supply any number of parameters to be
 *              used when executing the statement.
 *  @remarks    The same statement does not need to prepared again, even
 *              if it is executed multiple times.
 *  @remarks    There is no need to prepare all statements at the start of
 *              the application.
 */
/* *********************************************************************/
{
    pyptr session;
    char *query;
    int rc, opt;
    MimerStatement statement;

    if (!PyArg_ParseTuple(args, "Lsi", &session, &query, &opt)) {
        return NULL;
    }

    rc = MimerBeginStatement8((MimerSession)session, query, opt, &statement);

    return Py_BuildValue("iL", rc, (pyptr)statement);
}



static PyObject* mimerEndStatement(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Closes a prepared statement.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in]     args       Arguments.
 *                 args 1:    Statementhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    If there is an open cursor on this statement, it is
 *              automatically closed.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerEndStatement((MimerStatement*)&statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerOpenCursor(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Opens a cursor to be used when reading a result set.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in]     args       Arguments.
 *                 args 1:    Statementhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    Result sets are produced either by SELECT queries, or by
 *              calls to result set procedures.
 *  @remarks    All input parameters must be set prior to calling
 *              mimerOpenCursor, or else an error will occur.
 *  @remarks    If this routine returns successfully, the cursor is opened
 *              and positioned before the first row.
 *  @remarks    The first row can then be fetched by calling mimerFetch.
 *              After that column data may be retrieved using data
 *              output routines.
 *  @remarks    If the statement does not return a result set, this
 *              routine will return with a failure.
 */
/* *********************************************************************/
{
    int rc;
    pyptr statement;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerOpenCursor((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerCloseCursor(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Closes an open cursor.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in]     args       Arguments.
 *                 args 1:    Statementhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    When the cursor is closed, all resources held by the
 *              result set are released.
 *  @remarks    After the cursor is closed, the cursor may be reopened
 *              using a call to mimerOpenCursor or the statement should
 *              be released using mimerEndStatement.
 *  @remarks    Before the cursor is reopened, a new set of parameters
 *              may be supplied using any of the data input functions.
 */
/* *********************************************************************/
{
    int rc;
    pyptr statement;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerCloseCursor((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerAddBatch(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Adds a batch to load more parameters before execute.
 *
 *  @author     Erik Gunne
 *  @date       2017-12-22
 *
 *  @param[in]     self       Pointer to python object that function is
 *                            called from.
 *  @param[in]     args       Arguments.
 *                 args 1:    Statementhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 */
/* *********************************************************************/
{
    int rc;
    pyptr statement;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerAddBatch((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerExecuteStatement8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Executes a statement directly without parameters.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self       Pointer to python object that function is
 *                           called from.
 *  @param[in]    args       Arguments.
 *                args 1:    Sessionhandle.
 *                args 2:    SQL statement to execute.
 *
 *  @returns    Return code 0 = OK, < 0 if error, > 0 indicates an update
 *              row count returned by the database.
 *
 *  @remarks    This routine is mainly intended for data definition
 *              statements but can also be used for regular INSERT,
 *              UPDATE and DELETE statements with no input or output
 *              parameters.
 */
/* *********************************************************************/
{
    pyptr session;
    char *query;
    int rc;

    if (!PyArg_ParseTuple(args, "Ls", &session, &query)) {
        return NULL;
    }

    rc = MimerExecuteStatement8((MimerSession)session, query);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerExecute(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Execute a statement that does not return a result set.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error, > 0 indicates an update
 *              row count returned by the database.
 *
 *  @remarks    This routine is mainly intended for data definition
 *              statements but can also be used for regular INSERT,
 *              UPDATE and DELETE statements with no input or output
 *              parameters.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerExecute((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerParameterCount(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Obtains the number of parameters of a statement.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *
 *  @returns    Return code >= 0 the number of parameters, < 0 if error.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerParameterCount((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}


static PyObject* mimerParameterName8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Obtains the name of a parameter.
 *
 *  @author     Erik Gunne
 *  @date       2018-09-18
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Parameter number.
 *
 *  @returns    Return code >= 0 the number of parameters, < 0 if error.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    char value[BUFLEN];

    if (!PyArg_ParseTuple(args, "Li", &statement, &parameter_number)) {
        return NULL;
    }

    rc = MimerParameterName8((MimerStatement)statement, parameter_number,
                             value, BUFLEN);

    if (rc >= BUFLEN) {
        int buffer_size = rc + 1;
        PyObject* return_object;
        char *bigvalue = (char*) calloc(buffer_size, sizeof(char));
        rc = MimerParameterName8((MimerStatement)statement, parameter_number,
                                 bigvalue, buffer_size);
        return_object = Py_BuildValue("is", rc, bigvalue);
        free(bigvalue);
        return return_object;
    }

    return Py_BuildValue("is", rc, &value);
}



static PyObject* mimerParameterType(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Obtains the type of a parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Parameter number.
 *
 *  @returns    Return code > 0 indicates parameter type, < 0 if error.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;

    if (!PyArg_ParseTuple(args, "Li", &statement, &parameter_number)) {
        return NULL;
    }

    rc = MimerParameterType((MimerStatement)statement, parameter_number);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerColumnCount(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Obtains the number of columns in a result set.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *
 *  @returns    Return code >= 0 number of result set columns, < 0 if error.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerColumnCount((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerColumnType(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Returns the type of a column.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Column number.
 *
 *  @returns    Return code > 0 indicates column type, < 0 if error.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, column_number;

    if (!PyArg_ParseTuple(args, "Li", &statement, &column_number)) {
        return NULL;
    }

    rc = MimerColumnType((MimerStatement)statement, column_number);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerColumnName8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Obtains the name of a column in a multibyte character
 *              string.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-07-20
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the column number.
 *
 *  @returns    Return code 0 >= Length of column name, < 0 if error.
 *
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, column_number;
    char value[BUFLEN];

    if (!PyArg_ParseTuple(args, "Li", &statement, &column_number)) {
        return NULL;
    }

    rc = MimerColumnName8((MimerStatement)statement, column_number,
                          value, BUFLEN);

    if (rc >= BUFLEN) {
        int buffer_size = rc + 1;
        PyObject* return_object;
        char *bigvalue = (char*) calloc(buffer_size, sizeof(char));
        rc = MimerColumnName8((MimerStatement)statement, column_number,
                              bigvalue, buffer_size);
        return_object = Py_BuildValue("is", rc, bigvalue);
        free(bigvalue);
        return return_object;
    }

    return Py_BuildValue("is", rc, &value);
}



static PyObject* mimerFetch(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Advances to the next row of a result set.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    If the routine returns successfully, the current row has
 *              been advanced one row down the result set. Column data
 *              may be retrieved using data output routines.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc;

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerFetch((MimerStatement)statement);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerGetInt32(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets integer data from a result set or output parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Parameter of column number to get data from.
 *
 *  @returns   Tuple.
 *             Tuple[0]: Return code 0 = OK, < 0 if error.
 *             Tuple[1]: The value of the integer.
 *
 *  @remarks   Only the database type INTEGER, INTEGER(n), BIGINT and SMALLINT
 *             may be retrieved using this call.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, value, column_number;

    if (!PyArg_ParseTuple(args, "Li", &statement, &column_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, column_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetInt32((MimerStatement)statement, column_number, &value);
    return Py_BuildValue("ii", rc, value);
}



static PyObject* mimerGetInt64(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets integer data from a result set or output parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Parameter of column number to get data from.
 *
 *  @returns   Tuple.
 *             Tuple[0]: Return code 0 = OK, < 0 if error.
 *             Tuple[1]: The value of the integer.
 *
 *  @remarks   Only the database type INTEGER, INTEGER(n), BIGINT and SMALLINT
 *             may be retrieved using this call.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, column_number;
    int64_t value;

    if (!PyArg_ParseTuple(args, "Li", &statement, &column_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, column_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetInt64((MimerStatement)statement, column_number, &value);
    return Py_BuildValue("iL", rc, value);
}



static PyObject* mimerGetString8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets character data from a result set or output parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Parameter of column number to get data from.
 *
 *  @returns   Tuple.
 *             Tuple[0]: Return code >= 0 indicates number of characters in
 *                       column(not counting terminating zero), < 0 if error.
 *             Tuple[1]: The character data.
 *
 *  @remarks   Only SQL data types CHARACTER, CHARACTER VARYING, NATIONAL
 *             CHARACTER, and NATIONAL CHARACTER VARYING may be retrieved
 *             using this function.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, column_number;
    char value[BUFLEN];

    if (!PyArg_ParseTuple(args, "Li", &statement, &column_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, column_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetString8((MimerStatement)statement, column_number,
                         value, BUFLEN);

    if (rc >= BUFLEN) {
        int buffer_size = rc + 1;
        PyObject* return_object;
        char *bigvalue = (char*) calloc(buffer_size, sizeof(char));
        rc = MimerGetString8((MimerStatement)statement, column_number,
                             bigvalue, buffer_size);
        return_object = Py_BuildValue("is", rc, bigvalue);
        free(bigvalue);
        return return_object;
    }
    return Py_BuildValue("is", rc, &value);
}



static PyObject* mimerGetDouble(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets double precision float data from a result set or an
 *              output parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     Parameter of column number to get data from.
 *
 *  @returns   Tuple.
 *             Tuple[0]: Return code 0 = OK, < 0 if error.
 *             Tuple[1]: The double precision value.
 *
 *  @remarks   Only the database data types DOUBLE PRECISION, FLOAT(n), FLOAT
 *             and REAL may be retrieved using this call.
 *
 *  @remarks   Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, column_number;
    double value;

    if (!PyArg_ParseTuple(args, "Li", &statement, &column_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, column_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetDouble((MimerStatement)statement, column_number, &value);
    return Py_BuildValue("id", rc, value);
}



static PyObject* mimerSetInt32(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets an integer parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     An integer value.
 *
 *  @returns   Return code 0 = OK, < 0 if error.
 *
 *  @remarks   Only the database data types INTEGER, INTEGER(n), BIGINT and
 *             SMALLINT may be set using this call.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    int32_t val;

    if (!PyArg_ParseTuple(args, "Lii", &statement, &parameter_number, &val)) {
        return NULL;
    }
    rc = MimerSetInt32((MimerStatement)statement, parameter_number, val);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerSetInt64(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets an integer parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     An integer value.
 *
 *  @returns   Return code 0 = OK, < 0 if error.
 *
 *  @remarks   Only the database data types INTEGER, INTEGER(n), BIGINT and
 *             SMALLINT may be set using this call.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    int64_t val;

    if (!PyArg_ParseTuple(args, "LiL", &statement, &parameter_number, &val)) {
        return NULL;
    }

    rc = MimerSetInt64((MimerStatement)statement, parameter_number, val);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerSetString8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a string parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     An pointer to buffer holding UTF-16 or UTF-32
 *                            character string.
 *
 *  @returns   Return code 0 = OK, < 0 if error.
 *
 *  @remarks   Only the database data types CHARACTER, CHARACTER VARYING,
 *             NATIONAL CHARACTER, and NATIONAL CHARACTER VARYING may be
 *             set using this call.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    char* val;

    if (!PyArg_ParseTuple(args, "Lis", &statement, &parameter_number, &val)) {
        return NULL;
    }

    rc = MimerSetString8((MimerStatement)statement, parameter_number, val);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerSetDouble(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a double floating point parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     A double floating point value.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    double val;

    if (!PyArg_ParseTuple(args, "Lid", &statement, &parameter_number, &val)) {
        return NULL;
    }

    rc = MimerSetDouble((MimerStatement)statement, parameter_number, val);

    return Py_BuildValue("i", rc);
}



static PyObject* mimerGetError8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets an error message from a mimer session or mimer
 *              statement.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle or sessionhandle.
 *
 *  @returns    Tuple.
 *              Tuple[0]: Return code 0 = OK, < 0 if error.
 *              Tuple[1]: The number of the error found.
 *              Tuple[2]: The message from above error.
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 *              Not all errors are supported by this function.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, evalue;
    char message[BUFLEN];

    if (!PyArg_ParseTuple(args, "L", &statement)) {
        return NULL;
    }

    rc = MimerGetError8((MimerStatement)statement, &evalue, message, BUFLEN);
    /* TODO &&&& What if BUFLEN is not enough? */
    if (rc) {
        /* No error returned */
        message[0] = '\0';
    }
    return Py_BuildValue("iis", rc, evalue, message);
}



static PyObject* mimerSetBlobData(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a blob data parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     A string containing the blob data.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number, parse_length;
    MimerLob lobhandle;
    const char *data;

    if (!PyArg_ParseTuple(args, "Liz#", &statement, &parameter_number, &data,
                          &parse_length)) {
        return NULL;
    }

    if (data == NULL) {
        rc = MimerSetNull((MimerStatement)statement, parameter_number);
        return Py_BuildValue("i", rc);
    }

    rc = MimerSetLob((MimerStatement)statement,
                     parameter_number, parse_length, &lobhandle);

    if (rc < 0) {
        return Py_BuildValue("i", rc);
    }

    rc = 0;
    while (rc == 0 && parse_length > 0) {
        int len = parse_length < 9900000 ? parse_length : 9900000;
        rc = MimerSetBlobData(&lobhandle, data, len);
        data += len;
        parse_length -= len;
    }
    return Py_BuildValue("i", rc);
}



static PyObject* mimerSetNclobData8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a nclob data parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     A string containing the nclob data.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number, parse_length;
    MimerLob lobhandle;
    const char *data;

    // parse_length is a outparameter returning the length of the string data
    if (!PyArg_ParseTuple(args, "Liz#", &statement, &parameter_number, &data,
                          &parse_length)) {
        return NULL;
    }

    if (data == NULL) {
        rc = MimerSetNull((MimerStatement)statement, parameter_number);
        return Py_BuildValue("i", rc);
    }

    rc = MimerSetLob((MimerStatement)statement, parameter_number, parse_length,
                     &lobhandle);

    // Checking for possible errors after MimerSetLob
    if (rc < 0) {
        return Py_BuildValue("i", rc);
    }

    rc = MimerSetNclobData8(&lobhandle, data, parse_length);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerGetBlobData(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets a blob data parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle or sessionhandle.
 *                args 2:     A number identifying the parameter.
 *
 *  @returns    Tuple.
 *              Tuple[0]: Return code 0 = OK, < 0 if error.
 *              Tuple[1]: The blob data
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    MimerLob lobhandle;
    size_t length;
    char *data;
    PyObject* return_object;

    if (!PyArg_ParseTuple(args, "Li", &statement, &parameter_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, parameter_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetLob((MimerStatement)statement, parameter_number, &length,
                     &lobhandle);

    if (rc < 0) {
        return Py_BuildValue("i", rc);
    }

    data = (char*) calloc(length, sizeof(char));
    rc = MimerGetBlobData(&lobhandle, data, length);
    return_object = Py_BuildValue("iy#", rc, data,length);
    free(data);
    return return_object;
}



static PyObject* mimerGetNclobData8(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets a nclob data parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle or sessionhandle.
 *                args 2:     A number identifying the parameter.
 *
 *  @returns    Tuple.
 *              Tuple[0]: Return code 0 = OK, < 0 if error.
 *              Tuple[1]: The nclob data
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    MimerLob lobhandle;
    size_t length;
    char *data;
    PyObject *return_object;

    if (!PyArg_ParseTuple(args, "Li", &statement, &parameter_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, parameter_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }


    rc = MimerGetLob((MimerStatement)statement, parameter_number, &length,
                     &lobhandle);

    if (rc < 0) {
        return Py_BuildValue("i", rc);
    }

    data = (char*) calloc(length + lengthof_Terminating_NUL, sizeof(char));
    rc = MimerGetNclobData8(&lobhandle, data, length + lengthof_Terminating_NUL);
    return_object = Py_BuildValue("is", rc, data);
    free(data);
    return return_object;
}



static PyObject* mimerSetBinary(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a binary parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     A bytes-like object.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number, parse_length;
    char *value;

    if (!PyArg_ParseTuple(args, "Liz#", &statement, &parameter_number, &value,
                          &parse_length)){
        return NULL;
    }

    rc = MimerSetBinary((MimerStatement)statement, parameter_number, value,
                        parse_length);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerGetBinary(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets a binary data parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *
 *  @returns    Tuple.
 *              Tuple[0]: Return code 0 = OK, < 0 if error.
 *              Tuple[1]: The binary data
 *
 *  @remarks    Only supported in version 11 or above of the Micro C API.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    char value[BUFLEN];

    if (!PyArg_ParseTuple(args, "Li", &statement, &parameter_number)) {
        return NULL;
    }

    if (MimerIsNull((MimerStatement)statement, parameter_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetBinary((MimerStatement)statement, parameter_number,
                        value, BUFLEN);

    if (rc > BUFLEN) {
        PyObject* return_object;
        char *bigvalue = malloc(rc);
        rc = MimerGetBinary((MimerStatement)statement, parameter_number,
                            bigvalue, rc);
        return_object = Py_BuildValue("iy#", rc, bigvalue, rc);
        free(bigvalue);
        return return_object;
    }

    return Py_BuildValue("iy#", rc, &value[0], rc);
}



static PyObject* mimerSetBoolean(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a boolean parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *                args 3:     A boolean value.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 *  @remarks    In python any object can be a boolean. This function accepts
 *              any python object type in args 3.
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, val, parameter_number;

    if (!PyArg_ParseTuple(args, "Lip", &statement, &parameter_number, &val)) {
        return NULL;
    }

    rc = MimerSetBoolean((MimerStatement)statement, parameter_number, val);
    return Py_BuildValue("i", rc);
}



static PyObject* mimerGetBoolean(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Gets a boolean parameter.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle.
 *                args 2:     A number identifying the parameter.
 *
 *  @returns    Tuple.
 *              Tuple[0]: Return code 0 = OK, < 0 if error.
 *              Tuple[1]: Same as Tuple[0].
 *
 *  @remarks    Py_BuildValue does not support returning a python bool object.
 *              The reutrn value is given as a int bool(0 == ture, 1 == false).
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;

    if (!PyArg_ParseTuple(args, "Li", &statement, &parameter_number)) {
        return NULL;
    }
    if (MimerIsNull((MimerStatement)statement, parameter_number) > 0) {
        return Py_BuildValue("is", 0, NULL);
    }

    rc = MimerGetBoolean((MimerStatement)statement, parameter_number);

    /* Expected output from get funtions is always two values. */
    return Py_BuildValue("ii", rc, rc);
}



static PyObject* mimerSetNull(PyObject* self, PyObject* args)
/* *********************************************************************/
/**
 *  @brief      Sets a parameter to sql NULL.
 *
 *  @author     Erik Gunne & Magdalena Boström
 *  @date       2017-06-16
 *
 *  @param[in]    self        Pointer to python object that function is
 *                            called from.
 *  @param[in]    args        Arguments.
 *                args 1:     Statementhandle or sessionhandle.
 *                args 2:     A number identifying the parameter.
 *
 *  @returns    Return code 0 = OK, < 0 if error.
 *
 */
/* *********************************************************************/
{
    pyptr statement;
    int rc, parameter_number;
    char *dum;

    if (!PyArg_ParseTuple(args, "Liz", &statement, &parameter_number, &dum)) {
        return NULL;
    }

    rc = MimerSetNull((MimerStatement)statement, parameter_number);
    return Py_BuildValue("i", rc);
}



/**
* Describes all methods of the mimerapi extension.
*/
static PyMethodDef mimerapiMethods[] =
{
    {"mimerBeginSession8", (PyCFunction)mimerBeginSession8, METH_VARARGS,
     "Starts a session with the database."},
    {"mimerEndSession", (PyCFunction)mimerEndSession, METH_VARARGS,
     "End the database session."},
    {"mimerBeginTransaction", (PyCFunction)mimerBeginTransaction, METH_VARARGS,
     "Starts a transaction."},
    {"mimerEndTransaction", (PyCFunction)mimerEndTransaction, METH_VARARGS,
     "Ends a transaction."},
    {"mimerBeginStatement8", (PyCFunction)mimerBeginStatement8, METH_VARARGS,
     "Prepares an SQL statement for execution"},
    {"mimerEndStatement", (PyCFunction)mimerEndStatement, METH_VARARGS,
     "Closes a prepared statement."},
    {"mimerOpenCursor", (PyCFunction)mimerOpenCursor, METH_VARARGS,
     "Opens a cursor."},
    {"mimerCloseCursor", (PyCFunction)mimerCloseCursor, METH_VARARGS,
     "Closes an open cursor."},
    {"mimerAddBatch", (PyCFunction)mimerAddBatch, METH_VARARGS,
     "Adds a batch to load more parameters before execute."},
    {"mimerExecuteStatement8", (PyCFunction)mimerExecuteStatement8, METH_VARARGS,
     "Executes a statement directly without parameters."},
    {"mimerExecute", (PyCFunction)mimerExecute, METH_VARARGS,
     "Executes a statement that does not return a result set."},
    {"mimerParameterCount", (PyCFunction)mimerParameterCount, METH_VARARGS,
     "Returns the number of parameters of a statement."},
    {"mimerParameterName8", (PyCFunction)mimerParameterName8, METH_VARARGS,
     "Returns the name of a parameter."},
    {"mimerParameterType", (PyCFunction)mimerParameterType, METH_VARARGS,
     "Obtains the data type of a parameter"},
    {"mimerColumnCount", (PyCFunction)mimerColumnCount, METH_VARARGS,
     "Obtains the number of columns in a result set."},
    {"mimerColumnType", (PyCFunction)mimerColumnType, METH_VARARGS,
     "Returns the type of a column."},
    {"mimerFetch", (PyCFunction)mimerFetch, METH_VARARGS,
     "Advances to the next row of the result set."},
    {"mimerGetInt32", (PyCFunction)mimerGetInt32, METH_VARARGS,
     "Get int32 data from a result set or output parameter."},
    {"mimerGetInt64", (PyCFunction)mimerGetInt64, METH_VARARGS,
     "Get int64 data from a result set or output parameter."},
    {"mimerGetString8", (PyCFunction)mimerGetString8, METH_VARARGS,
     "Get character data from a result set or output parameter."},
    {"mimerGetDouble", (PyCFunction)mimerGetDouble, METH_VARARGS,
     "Get double precision float data from a result set or output parameter."},
    {"mimerSetInt32", (PyCFunction)mimerSetInt32, METH_VARARGS,
     "Sets an int32 parameter."},
    {"mimerSetInt64", (PyCFunction)mimerSetInt64, METH_VARARGS,
     "Sets an int64 parameter."},
    {"mimerSetString8", (PyCFunction)mimerSetString8, METH_VARARGS,
     "Sets an string parameter."},
    {"mimerSetDouble", (PyCFunction)mimerSetDouble, METH_VARARGS,
     "Sets an double folating point parameter."},
    {"mimerGetError8", (PyCFunction)mimerGetError8, METH_VARARGS,
     "Returns error message."},
    {"mimerSetBlobData", (PyCFunction)mimerSetBlobData, METH_VARARGS,
     "Sets blob data."},
    {"mimerGetBlobData", (PyCFunction)mimerGetBlobData, METH_VARARGS,
     "Gets blob data."},
    {"mimerSetNclobData8", (PyCFunction)mimerSetNclobData8, METH_VARARGS,
     "sets Nclob data."},
    {"mimerGetNclobData8", (PyCFunction)mimerGetNclobData8, METH_VARARGS,
     "Gets Nclob data."},
    {"mimerSetBinary", (PyCFunction)mimerSetBinary, METH_VARARGS,
     "Sets binary data."},
    {"mimerSetBoolean", (PyCFunction)mimerSetBoolean, METH_VARARGS,
     "Sets boolean data."},
    {"mimerGetBoolean", (PyCFunction)mimerGetBoolean, METH_VARARGS,
     "Gets boolean data."},
    {"mimerSetNull", (PyCFunction)mimerSetNull, METH_VARARGS,
     "Sets parameter to null."},
    {"mimerColumnName8", (PyCFunction)mimerColumnName8, METH_VARARGS,
     "Obtains name of a column."},
    {"mimerGetBinary", (PyCFunction)mimerGetBinary, METH_VARARGS,
     "Obtains name of a column."},
    {NULL, NULL, 0, NULL}
};

/**
* Module defintion struct.
*/
static struct PyModuleDef mimerapi = {
    PyModuleDef_HEAD_INIT,
    "mimerapi",
    "mimerapi module",
    -1,
    mimerapiMethods
};

PyMODINIT_FUNC PyInit_mimerapi(void)
{
     return PyModule_Create(&mimerapi);
}
