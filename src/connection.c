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


#include "mimerapi.h"
#include "Python.h"

/**
 * We must pass pointers between the C layer and Python. We use the "L"
 * format character which specified the "long long" C type.
 */
typedef long long pyptr;



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



/**
* Describes all methods of connection extension.
*/
static PyMethodDef connectionMethods[] =
{
    {"mimerBeginSession8", (PyCFunction)mimerBeginSession8, METH_VARARGS,
     "Starts a session with the database."},
    {"mimerEndSession", (PyCFunction)mimerEndSession, METH_VARARGS,
     "End the database session."},
    {"mimerBeginTransaction", (PyCFunction)mimerBeginTransaction, METH_VARARGS,
     "Starts a transaction."},
    {"mimerEndTransaction", (PyCFunction)mimerEndTransaction, METH_VARARGS,
     "Ends a transaction."},
    {NULL, NULL, 0, NULL}
};

/**
* Module defintion struct.
*/
static struct PyModuleDef connection = {
    PyModuleDef_HEAD_INIT,
    "connection",
    "connection module",
    -1,
    connectionMethods
};

PyMODINIT_FUNC PyInit_connection(void)
{
     return PyModule_Create(&connection);
}
