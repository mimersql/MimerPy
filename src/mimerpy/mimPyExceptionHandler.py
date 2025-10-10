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

from mimerpy.mimPyExceptions import *
from mimerpy import mimerapi

# When adding new MimerAPI error codes:
#  - Use the range -25xxx
#  - Check the dictionaries below so that the right exception is thrown
#  - Update env/gblsym/message.sym in the Mimer trunk
#  - Update dbl/sdb/syscat.ddi in the Mimer trunk
#  - Tell Jarl

mimerpy_error = {
    -25000:"Unsupported method",
    -25001:"TPC is unsupported",
    -25010:"Connection not open",
    -25011:"Invalid number of parameters",
    -25012:"KeyError in parameters, key: %s does not exist in dictionary",
    -25013:"Invalid parameter format",
    -25014:"Previous execute did not produce a result set",
    -25015:"Cursor not open",
    -25016:"Illegal scroll mode",
    -25020:"Data conversion error",
    -25030:"Out of memory",
    -25031:"Login failure",
    -25101:("The operation requires Mimer API version 11.0.5A or newer. You have %s." % mimerapi.__version__),
    -25102:("The operation requires Mimer API version 11.0.5B or newer. You have %s." % mimerapi.__version__),
}

py_error_nnnnn = {10001:TransactionAbortError,10003:TransactionAbortError,24010:DataError,24011:DataError
}

py_error_nnnnx = {2500:NotSupportedError,
                  2501:ProgrammingError,
                  2502:DataError,
                  2503:OperationalError,
                  2510:NotSupportedError,
}

py_error_nnxxx = {10:DataError, 11:OperationalError, 12:ProgrammingError,
                  14:ProgrammingError, 16:OperationalError, 18:DatabaseError,
                  19:InternalError, 21:IntegrityError, 23:InternalError,
                  24:ProgrammingError,
                  25:ProgrammingError, 26:InterfaceError,
                  27:DataError, 28: NotSupportedError}

py_error_xxxxx = InternalError

def get_error_class(rc):
    """
    Return a suitable error class from an error number.
    """
    rc = -rc;
    if rc in py_error_nnnnn:
        return py_error_nnnnn[rc]
    rc = rc // 10
    if rc in py_error_nnnnx:
        return py_error_nnnnx[rc]
    rc = rc // 100
    if rc in py_error_nnxxx:
        return py_error_nnxxx[rc]
    return py_error_xxxxx


def get_mimerapi_exception(rc, mimerapi_handle):
    """
    Return (errorclass, errorvalue) from a failed MimerAPI call.
    """
    if -25999 <= rc <= -25000:
        return (get_error_class(rc), (rc, mimerpy_error[rc]))
    (rc0, _, msg) = mimerapi.mimerGetError8(mimerapi_handle)
    if rc0:
        msg = "Unknown error %d" % rc
    return (get_error_class(rc), (rc, msg))
