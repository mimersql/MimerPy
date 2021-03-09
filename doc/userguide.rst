***************
User guide
***************

.. _mimer-syntax:

This chapter of the documentation covers the relationship between Mimerpy, MimerSQL and the Mimer Micro C API.

Query structure
------------------------
There are two ways to structure a query in Mimerpy, with or without parameter markers.

Without parameter markers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Executing a query without parameter markers is done with the MimerSQL syntax.
If you are looking for help with basic elements of the SQL language and MimerSQL please visit `Mimer documentation`_.
Consider the following example::

  >>> con = mimerpy.connect(dsn ="mimerDB", user="mimerUser", password="password")
  >>> cur = con.execute("create table testtable(c1 NVARCHAR(128), c2 BINARY(3))")
  >>> cur.execute("INSERT INTO ptable VALUES ('bar', x'ABCD01')")

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

The same rules apply when using :meth:`~executemany`. For an example, see :ref:`Executemany`.


.. Common mistakes
.. ------------------------


.. If you are looking for a more formal guide please visit the `official mimer documentation`_

.. _PEP 249: https://www.python.org/dev/peps/pep-0249/
.. _mimer documentation: http://developer.mimer.com/documentation/html_101/Mimer_SQL_Engine_DocSet/index.htm
.. _official mimer documentation: http://developer.mimer.com/documentation/html_101/Mimer_SQL_Engine_DocSet/index.htm


Transaction control
------------------------

Every time an :meth:`execute` is called from a connection or a cursor, a transaction, if not already open, starts.
The transaction is supposed to be open until a :meth:`rollback` or a :meth:`commit` is performed. Unfortunately this is not always true.
If a DDL statement is executed the transaction will implicitly end.
Because of this there are some limitations and a few things to keep in mind while using the current version Mimerpy.

* DLL and DML statements should (can) not be mixed in the same transaction.
* DDL statement are always committed.

In most sequences of DDL and DML mixing, Mimerpy will raise a :exc:`ProgrammingError`. However not always.
Mimerpy is coded to handle mixing of DDL and DML statements, but the current version of the Mimer Micro C API can not handle it.
Because of this, unpredictable behavior sometimes occur when mixing DDL and DML executes.

The Mimerpy user has the responsibility to write code with transaction control in mind.
Our recommendation is to always commit before and after a executing a DDL statement.
Consider the following example::

  >>> cur = conn.cursor()
  >>> cur.execute("create table mytable(c1 NVARCHAR(128))")
  >>> cur.execute("insert into mytable values ('foo')")
  >>> cur.execute("select * from mytable")
  >>> conn.commit()

In the current version of the Mimer Micro C API (``11.0``) the example above will not raise an error. However, because DDL
statements always are committed, this example gives bad abstraction. Consider the following example::

  >>> cur = conn.cursor()
  >>> cur.execute("create table mytable(c1 NVARCHAR(128))")
  >>> cur.commit()
  >>> cur.execute("insert into mytable values ('bar')")
  >>> cur.execute("select * from mytable")
  >>> conn.commit()

This is what is done in the first example implicitly.

.. note:: If you wish to bypass this problem, :meth:`autocommit` can be used and none
          of this applies.

MimerSQL DML & DDL cheat sheet
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
