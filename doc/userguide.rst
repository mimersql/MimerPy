
User guide
***************

.. _mimer-syntax:

This chapter of the documentation covers the relationship between
MimerPy, Mimer SQL and the Mimer SQL C API.

Connection parameters
---------------------
You can use a dictionary to store connection parameters. And you can
omit connection parameters to use default values.

Use a dictionary for connection parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Python allows you to record a set of named parameters as a
dictionary_, and use it when calling functions. This allows you to
specify the connection parameters centrally and reuse it everywhere a
connection needs to be created, like this:

.. _dictionary: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
.. code-block:: console

    >>> import mimerpy
    >>> data_source = {'dsn':'mimerDB', 'user':'mimerUser', 'password':'password'}

      # Creating a connection
    >>> con = mimerpy.connect(**data_source)

Default value for Mimer SQL database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the parameter dsn is set to an empty string ("") or None in the
:meth:`connect` method, the default database name will be used.
You can specify the default in two ways:

* Specify a default database in the sqlhosts file (UNIX) or in the
  database administrator (Windows).
* Set the environment variable MIMER_DATABASE to the default database name.

Default value for user name and password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can create a Mimer SQL IDENT with the same name as the user in your
host operating system, and add an OS_USER to that ident. This allows
the user to log in to Mimer SQL without specifying a password. This only
works on local databases and not on databases accessed over TCP/IP.

For example (on UNIX):

.. code-block:: console

    $ whoami
    smith
    $ bsql
    Username: SYSADM
    Password:
    SQL>create ident smith as user;
    SQL>alter ident smith add os_user 'smith';
    SQL>exit;
    $ python3
    >>> import mimerpy
    >>> con=mimerpy.connect()


Query structure
------------------------
There are two ways to structure a query in MimerPy, with or without
parameter markers.

Without parameter markers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Executing a query without parameter markers is done with the Mimer SQL
syntax.  If you are looking for help with basic elements of the SQL
language and Mimer SQL please visit `Mimer SQL documentation`_.  Consider
the following example::

  >>> con = mimerpy.connect(dsn ="mimerDB", user="mimerUser", password="password")
  >>> cur = con.execute("create table testtable(c1 NVARCHAR(128), c2 BINARY(3))")
  >>> cur.execute("INSERT INTO ptable VALUES ('bar', x'ABCD01')")

There are some drawbacks using constant literals in SQL expressions:

* The SQL database server will compile each new SQL statement into an
  intermediate executable representation. The database server maintains a cache
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
Mimer SQL uses the ``qmark`` parameter style. This means parameter markers are of
question mark style, e.g...WHERE name=?. Dictionaries can also be used as parameter markers. 
The key(s) in the dictionary have to match up with the corresponding column you want to manipulate.  

When executing to a single column, the rules can be bent a bit::

      # Creating a table
  >>> cur.execute("create table ptable(c1 NVARCHAR(128))")

      # Executing a statement using parametermarkers
  >>> cur.execute("INSERT INTO ptable VALUES (?)", "bar")      # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?)", ("bar"))    # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?)", ("bar",))   # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?)", ["bar"])    # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (:a)", {'a':bar}) # Correct

When executing to multiple columns, the rules are more strict::

      # Creating a table
  >>> cur.execute("create table ptable(c1 NVARCHAR(128), c2 INTEGER, c3 FLOAT)")

      # Executing a statement using parametermarkers
  >>> cur.execute("INSERT INTO ptable VALUES (?,?,?)", ("bar",314,41.23))                 # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?,?,?)", ["bar",314,41.23])                 # Correct
  >>> cur.execute("INSERT INTO ptable VALUES (?,?,?)", "bar",314,41.23)                   # Incorrect
  >>> cur.execute("INSERT INTO ptable VALUES (:a,:b,:c)", {'a':"bar",'b':314,'c':41.23})  # Correct

The same rules apply when using :meth:`~executemany`. For an example,
see :ref:`Executemany`.


.. Common mistakes
.. ------------------------


.. If you are looking for a more formal guide please visit the `Mimer documentation`_

.. _PEP 249: https://peps.python.org/pep-0249/
.. _Mimer SQL documentation: https://developer.mimer.com/products/documentation/


Transaction control
------------------------

Every time an :meth:`execute` is called from a connection or a cursor,
a transaction, if not already open, starts.  The transaction is
supposed to be open until a :meth:`rollback` or a :meth:`commit` is
performed. Unfortunately this is not always true.  If a Data Definition
Language(DDL) statement is executed the transaction will implicitly end. 
Because of this there are some limitations and a few things to keep in mind while
using the current version MimerPy.

* DDL and Data Manipulation Language (DML) statements should (can) not be mixed in the same transaction.
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

Mimer SQL DML and DDL cheat sheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
