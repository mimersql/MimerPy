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

from platform import system
from sys import version_info
plat = system()
if plat == 'Windows' and version_info[0] == 3 and version_info[1] >= 8:
    from os import add_dll_directory
    from winreg import HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY, ConnectRegistry, OpenKeyEx, QueryValueEx, CloseKey, EnumKey, OpenKeyEx
    root = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    mimer_key = OpenKeyEx(root, r"SOFTWARE\Mimer\Mimer SQL", 0,  KEY_READ | KEY_WOW64_64KEY)
    index = 0
    while True:
        try:
            key = EnumKey(mimer_key,index)
            if key != "License" and key != "SQLHosts":
                version = key
                break
            index = index + 1
        except OSError:
            break
    inner_key = OpenKeyEx(mimer_key, version)
    path = QueryValueEx(inner_key, 'PathName')[0]
    CloseKey(inner_key)
    CloseKey(root)
    add_dll_directory(path)
from pkg_resources import get_distribution, DistributionNotFound
from mimerpy.connectionPy import Connection
from mimerpy.cursorPy import _define_funcs
from mimerpy.mimPyExceptions import *
from mimerpy.mimPyExceptionHandler import mimerpy_error
import re
import mimerapi
import mimerpy
import functools
import logging

#
#  Set version number from tag in git
#
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    pass



def connect(dsn='', user='', password='',
            autocommit=False, errorhandler=None):
    """
    Create a database connection.

    dsn         Data source name.
                If empty, the environment variable MIMER_DATABASE is consulted.
                If that variable is unavailable, the default database as
                specified in /etc/sqlhosts (UNIX) or in the Mimer Administrator
                (Windows) is used.

    user        Name of the ident to use.
                If empty, the database server will perform an OS_USER login
                using the OS-level username. This does not work if the database
                server is remote.

    password    Password to chosen ident.
                Leave this empty if performing an OS_USER login.

    autocommit  Autocommit mode.
                The default behaviour according to PEP-0249 is False, meaning
                that all transactions have to be explicitly committed.
                If autocommit is enabled, each statement is committed
                automatically when executed.

    errorhandler A handler for errors according to the Optional Error Handling
                Extension described in PEP-0249.
    """
    return Connection(dsn, user, password, autocommit, errorhandler)

apilevel = '2.0'
threadsafety = '1'
paramstyle = 'qmark'
_v = re.findall(r'^\d+\.\d+\.\d+$', __version__)
version = _v[0] if len(_v) else ''
version_info = tuple([int(x) for x in version.split(".")]) if len(version) else ()
mimerapi.__version__ = mimerapi.mimerAPIVersion().rstrip()

def _tracefunc(func, prefix, logger):
    @functools.wraps(func)
    def tracer(*args, **kwargs):
        r_args = [repr(a) for a in args]
        r_kwargs = ["%s=%s" % (k, repr(v)) for k, v in kwargs.items()]
        signature = ", ".join(r_args + r_kwargs)
        logger.info("%sCall %s(%s)"
                    % (prefix, func.__name__, signature))
        try:
            value = func(*args, **kwargs)
            logger.info("%sRet: %s" % (prefix, repr(value)))
            return value
        except Exception as e:
            logger.info("EXCEPTION: %s" % repr(e))
            raise e
    return tracer

def _alterfuncs(d, prefix, logger):
    for fn in dir(d):
        f = d.__getattribute__(fn)
        if fn[0] != '_' and fn[0] >= 'a' and callable(f):
            setattr(d, fn, _tracefunc(f, prefix, logger))

def _apitrace(prefix=''):
    logger = logging.getLogger("MimerAPI")
    logger.setLevel(logging.INFO)
    _alterfuncs(mimerapi, prefix, logger)
    _define_funcs()

def _altermeths(d, prefix, logger):
    for fn in dir(d):
        if fn[0] != '_' and fn[0] >= 'a':
            try:
                f = d.__getattribute__(d, fn)
                if callable(f):
                    setattr(d, fn, _tracefunc(f, prefix, logger))
            except AttributeError:
                pass

def _pytrace(prefix=''):
    logger = logging.getLogger("MimerPy")
    logger.setLevel(logging.INFO)
    _alterfuncs(mimerpy, prefix, logger)
    _altermeths(mimerpy.connectionPy.Connection, prefix, logger)
    _altermeths(mimerpy.cursorPy.Cursor, prefix, logger)
    _altermeths(mimerpy.cursorPy.ScrollCursor, prefix, logger)

def _trace(things=255, prefix='', setLogLevel=True):
    if setLogLevel:
        logging.basicConfig(level=logging.INFO)
    if things & 1:
        _pytrace(prefix)
    if things & 2:
        _apitrace(prefix)
