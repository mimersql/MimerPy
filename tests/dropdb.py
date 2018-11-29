import mimerpy
import unittest
import time
import random

from mimerpy.mimPyExceptions import *
import db_config

print("Dropping")
a = mimerpy.connect(dsn = db_config.DB_INFO['DBNAME'], user =
            db_config.DB_INFO['SYSADM'], password = db_config.DB_INFO['SYADMPSW'])
b = a.cursor()
try:
    b.execute("DROP DATABANK testbank CASCADE")
except:
    "nothing"
try:
    b.execute("DROP IDENT TEST_IDENT CASCADE")
except:
    "nothing"
b.close()
a.close()
print("Dropped")
