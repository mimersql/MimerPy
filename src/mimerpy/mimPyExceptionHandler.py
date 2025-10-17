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

from .mimPyExceptions import *
from .mimPyErrorCodes import (
    mimerpy_error,
    py_error_nnnnn,
    py_error_nnnnx,
    py_error_nnxxx,
    py_error_xxxxx,
)

def get_error_class(rc):
    """
    Return a suitable error class from an error number.
    """
    rc = -rc
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
    from mimerpy import mimerapi
    if -25999 <= rc <= -25000:
        return (get_error_class(rc), (rc, mimerpy_error[rc]))
    (rc0, _, msg) = mimerapi.mimerGetError8(mimerapi_handle)
    if rc0:
        msg = "Unknown error %d" % rc
    return (get_error_class(rc), (rc, msg))
