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
import mimerapi

mimerpy_error = {
    -25001:(NotSupportedError, "Operation is unsupported"),
}

py_error_xxxxx = {}

py_error_nnxxx = {10:DataError, 11:OperationalError, 12:ProgrammingError,
                  14:ProgrammingError, 16:OperationalError, 18:DatabaseError,
                  19:InternalError, 21:IntegrityError, 23:InternalError,
                  24:ProgrammingError,
                  25:ProgrammingError, 26:InterfaceError,
                  27:DataError, 28: NotSupportedError}

def get_error_class(rc):
    """
    Return a suitable error class from an error number.
    Mimerpy internal errors (-25xxx) are not recognized here.
    """
    rc = -rc;
    return py_error_xxxxx.get(rc,
                              py_error_nnxxx.get(rc//1000, InternalError))


def get_mimerapi_exception(mimerapi_handle, rc):
    """
    Return (errorclass, errorvalue) from a failed MimerAPI call.
    """
    (rc0, _, msg) = mimerapi.mimerGetError8(mimerapi_handle)
    if rc0:
        msg = "Unknown error %d" % rc
    return (get_error_class(rc), (rc, msg))


def check_for_exception(*arg):
    """
        Maps a MimerAPI error code to an exception class and look up
        an error message text.
    """
    if (arg[1] == 0):
        return 0
    elif (arg[0] >= 0):
        return 0
    elif (arg[0] < -10000):
        key = -arg[0] // 1000
        if (key >= 25):
            return (py_error_nnxxx[key],arg[1])
        else:
            r = mimerapi.mimerGetError8(arg[1])
            if (r[0] != 0):
                msg = "Unknown error %d" % arg[0]
            else:
                msg = r[2]
            return (py_error_nnxxx[key], msg)
