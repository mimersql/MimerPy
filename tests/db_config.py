# The database to run the tests on. Having it empty means that the
# environment variable MIMER_DATABASE controls the database to connect to.
DBNAME = ''

# The test connects to SYSADM_USR and creates a subident that is used for all
# the tests. After testing, the subident is dropped and everything goes away.
SYSADM_USR = 'SYSADM'
SYSADM_PWD = 'SYSADM'


DB_INFO = {
    'DBNAME': '',
    'SYSADM': 'SYSADM',
    'SYADMPSW': 'SYSADM',
}

DB_IDENT = {
    'NAME': 'TEST_IDENT',
    'PSW': 'mimerPass',
}

#################################################################
## Stuff below defines routines for all tests.
## Do not change for configuration purposes
#################################################################

import mimerpy

# Connection arguments for SYSADM
SYSUSR = dict(dsn      = DBNAME,
              user     = SYSADM_USR,
              password = SYSADM_PWD)

# Connection arguments for test user
TSTUSR = dict(dsn      = DBNAME,
              user     = 'MIMERPY',
              password = 'PySecret')


def setup():
    syscon = mimerpy.connect(**SYSUSR)
    with syscon.cursor() as c:
        c.execute("CREATE IDENT MIMERPY AS USER USING 'PySecret'")
        c.execute("GRANT DATABANK TO MIMERPY")
    syscon.commit()
    tstcon = mimerpy.connect(**TSTUSR)
    with tstcon.cursor() as c:
        c.execute("CREATE DATABANK PYBANK")
    tstcon.commit()
    return (syscon, tstcon)
