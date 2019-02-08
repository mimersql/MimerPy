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

from pkg_resources import get_distribution, DistributionNotFound
from mimerpy.connectionPy import Connection
import re
import mimerapi
import functools

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

def _tracefunc(func, prefix=''):
    @functools.wraps(func)
    def tracer(*args, **kwargs):
        r_args = [repr(a) for a in args]
        r_kwargs = ["%s=%s" % (k, repr(v)) for k, v in kwargs.items()]
        signature = ", ".join(r_args + r_kwargs)
        print("%sCall %s(%s)"
              % (prefix, func.__name__, signature))
        try:
            value = func(*args, **kwargs)
            print("%sRet: %s" % (prefix, repr(value)))
            return value
        except Exception as e:
            print("EXCEPTION: %s" % repr(e))
            raise e
    return tracer

def _apitrace(prefix=''):
    for fn in dir(mimerapi):
        f = mimerapi.__getattribute__(fn)
        if callable(f):
            setattr(mimerapi, fn, _tracefunc(f, prefix))
