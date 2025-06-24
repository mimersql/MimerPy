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

# The database to run the tests on. Having it empty means that the
# environment variable MIMER_DATABASE controls the database to connect to.
DBNAME = ''

# The test connects to SYSADM_USR and creates a subident that is used for all
# the tests. After testing, the subident is dropped and everything goes away.
SYSADM_USR = 'SYSADM'
SYSADM_PWD = 'SYSADM'


#################################################################
## Stuff below defines routines for all tests.
## Do not change for configuration purposes
#################################################################

import mimerpy
import os
import getpass
from platform import system

# Connection arguments for SYSADM
SYSUSR = dict(dsn      = DBNAME,
              user     = SYSADM_USR,
              password = SYSADM_PWD)

# Connection arguments for test user
TSTUSR = dict(dsn      = DBNAME,
              user     = 'MIMERPY',
              password = 'PySecret')

OSUSER = getpass.getuser()
QUALIFIED_OSUSER = getpass.getuser()
plat = system()
if plat == 'Windows':
    QUALIFIED_OSUSER = os.getenv("USERDOMAIN") + "\\" + OSUSER 

KEEP_MIMERPY_IDENT = os.environ.get('MIMER_KEEP_MIMERPY_IDENT', 'false') == 'true'
MIMERPY_STABLE = os.environ.get('MIMERPY_STABLE', 'True')
MIMERPY_TRACE = os.environ.get('MIMERPY_TRACE')

def setup():
    if MIMERPY_TRACE:
        mimerpy._trace()
    syscon = mimerpy.connect(**SYSUSR)
    with syscon.cursor() as c:
        try:
            c.execute("DROP IDENT MIMERPY CASCADE")
        except mimerpy.DatabaseError as de:
            if de.message[0] != -12517:
                pass
            else:
                pass

        c.execute("CREATE IDENT MIMERPY AS USER USING 'PySecret'")
        c.execute("GRANT DATABANK,IDENT TO MIMERPY")
    syscon.commit()
    tstcon = mimerpy.connect(**TSTUSR)
    with tstcon.cursor() as c:
        c.execute("CREATE DATABANK PYBANK")
        c.execute(F"CREATE IDENT \"{OSUSER}\" AS USER")
        c.execute(F"ALTER IDENT \"{OSUSER}\" ADD OS_USER '{QUALIFIED_OSUSER}' ")
    tstcon.commit()
    return (syscon, tstcon)

def teardown(tstcon, syscon):
        tstcon.close()
        if not KEEP_MIMERPY_IDENT:
            with syscon.cursor() as c:
                c.execute("DROP IDENT MIMERPY CASCADE")
            syscon.commit()
        syscon.close()
