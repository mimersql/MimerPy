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
import cursor
import math

py_error = {10:DataError, 11:OperationalError, 12:ProgrammingError, 14:ProgrammingError,
 16:OperationalError, 18:DatabaseError, 19:InternalError, 21:IntegrityError,
 23:InternalError, 24:ProgrammingError, 25:ProgrammingError, 26:InterfaceError,
 27:DataError, 28: NotSupportedError}

def check_for_exception(*arg):
    """
        Maps Mimer Micro C API error codes to corresponding
        Python exception.

    """
    if(arg[0] == 90):
        return (py_error[18],"Login failure")
    elif(arg[1] == 0):
        return 0
    elif(arg[0] >= 0):
        return 0
    elif(arg[0] < -10000):
        key = math.floor(abs(arg[0]/1000))
        if(key >= 25):
            return (py_error[key],arg[1])
        else:
            return (py_error[key],(cursor.mimerGetError8(arg[1])[2]))
