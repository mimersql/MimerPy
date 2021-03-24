
User guide
***************

.. _mimer-syntax:

This chapter of the documentation covers the relationship between
MimerPy, Mimer SQL and the Mimer SQL C API.

Query structure
------------------------
There are two ways to structure a query in MimerPy, with or without
parameter markers.

Without parameter markers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Executing a query without parameter markers is done with the Mimer SQL
syntax.  If you are looking for help with basic elements of the SQL
language and Mimer SQL please visit `Mimer documentation`_.  Consider
the following example::

  >>> con = mimerpy.connect(dsn ="mimerDB", user="mimerUser", password="password")
  >>> cur = con.execute("create table testtable(c1 NVARCHAR(128), c2 BINARY(3))")
  >>> cur.execute("INSERT INTO ptable VALUES ('bar', x'ABCD01')")

There are some drawbacks using constant literals in SQL expressions:

* The SQL server will compile each new SQL statement into an
  intermediate executable representation. The server maintains a cache
  of statements it has already compiled. If it finds the exact same
  SQL string, it can reuse an old compiled statement. Use parameter
  markers to keep the statements identical and reusable.
* Creating SQL strings with data constants can create a security risk known
  as `SQL Injection`_. Use parameter markers to avoid this risk.

.. _SQL Injection: https://en.wikipedia.org/wiki/SQL_injection

With parameter markers
^^^^^^^^^^^^^^^^^^^^^^^^

Executing queries with parameter markers should be done following a few rules.
According to the `PEP 249`_ parameter markers should be a list of tuples.
Mimer uses the ``qmark`` parameter style. This means parameter markers are of
question mark style, e.g...WHERE name=?

When executing to a single column, the rules can be bent a bit::

      # Creating a table
  >>> cur.execute("create table ptable(c1 NVARCHAR(128))")

      # Executing a statement using parametermarkers
  >>> cur.execute("INSERT INTO ptable VALUES (?)", "bar")    # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?)", ("bar"))  # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?)", ("bar",)) # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?)", ["bar"])  # Correct

When executing to multiple columns, the rules are more strict::

      # Creating a table
  >>> cur.execute("create table ptable(c1 NVARCHAR(128), c2 INTEGER, c3 FLOAT) in testbank")

      # Executing a statement using parametermarkers
  >>> cur.execute("INSERT INTO ptable VALUES (?,?,?)", ("bar",314,41.23)) # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?,?,?)", ["bar",314,41.23]) # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?,?,?)", "bar",314,41.23)   # Incorrect

The same rules apply when using :meth:`~executemany`. For an example,
see :ref:`Executemany`.


.. Common mistakes
.. ------------------------


.. If you are looking for a more formal guide please visit the `Mimer documentation`_

.. _PEP 249: https://www.python.org/dev/peps/pep-0249/
.. _mimer documentation: https://developer.mimer.com/documentation/


Transaction control
------------------------

Every time an :meth:`execute` is called from a connection or a cursor,
a transaction, if not already open, starts.  The transaction is
supposed to be open until a :meth:`rollback` or a :meth:`commit` is
performed. Unfortunately this is not always true.  If a DDL statement
is executed the transaction will implicitly end.  Because of this
there are some limitations and a few things to keep in mind while
using the current version MimerPy.

* DLL and DML statements should (can) not be mixed in the same transaction.
* DDL statement are always committed.

In most sequences of DDL and DML mixing, MimerPy will raise a
:exc:`ProgrammingError`. However not always.  MimerPy is coded to
handle mixing of DDL and DML statements, but the current version of
the Mimer SQL C API can not handle it.  Because of this, unpredictable
behavior sometimes occur when mixing DDL and DML executes.

The MimerPy user has the responsibility to write code with transaction
control in mind.  Our recommendation is to always commit before and
after a executing a DDL statement.  Consider the following example::

  >>> cur = conn.cursor()
  >>> cur.execute("create table mytable(c1 NVARCHAR(128))")
  >>> cur.execute("insert into mytable values ('foo')")
  >>> cur.execute("select * from mytable")
  >>> conn.commit()

In the current version of the Mimer SQL C API (``11.0``) the example
above will not raise an error. However, because DDL statements are
always committed, this example gives a false impression. Consider the
following example::

  >>> cur = conn.cursor()
  >>> cur.execute("create table mytable(c1 NVARCHAR(128))")
  >>> cur.commit()
  >>> cur.execute("insert into mytable values ('bar')")
  >>> cur.execute("select * from mytable")
  >>> conn.commit()

This is what is done in the first example implicitly.

.. note:: If you wish to bypass this problem, :meth:`autocommit` can
          be used and none of this applies.

Mimer SQL DML & DDL cheat sheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
+----------+----------+
| DML      | DDL      |
|          |          |
+==========+==========+
| SELECT   | CREATE   |
+----------+----------+
| INSERT   | ALTER    |
+----------+----------+
| UPDATE   | DROP     |
+----------+----------+
| DELETE   |          |
+----------+----------+
