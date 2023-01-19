***************
Getting started
***************

With MimerPy installed, before proceeding make sure that you have a
Mimer SQL database server using version 11, or later. If you are
uncertain if you have a Mimer SQL server running, or need help getting one
running, please visit the `Mimer documentation`_.

.. _Mimer documentation: https://developer.mimer.com/products/documentation/

.. note:: MimerPy requires Python 3.5 or later. On Windows the command to run python3 varies between `python` and  `python3` depending on what versions you have installed. On Linux the command normally is `python3`. In this guide we use `python3` as command, but you might have to adjust for your environment.

Checking the MimerPy installation
---------------------------------
While the primary use of MimerPy is as a package used by other Python
programs, it is possible to use it a a stand-alone Python
program. This makes it easy to check if MimerPy works as intended and
can connect to a started Mimer SQL database server.

For example:

.. code-block:: console

    $ python3 -m mimerpy
    Use option -h to get help
    $ python3 -m mimerpy -h
    usage: mimerpy [-h] [-d DATABASE] [-u USER] [-p PASSWORD] [-v] [sql]

    A simple command line program for the MimerPy library. It can display the
    version number of the MimerPy library (-v switch) or connect to a Mimer
    database server and execute a singe SQL statement (provide database, user, and
    password arguments and a SQL statement).

    positional arguments:
      sql                   A SQL command to execute

    optional arguments:
      -h, --help            show this help message and exit
      -d DATABASE, --database DATABASE
                            Database to connect to
      -u USER, --user USER  User name to use in connection
      -p PASSWORD, --password PASSWORD
                            Password for the user
      -v, --version         Display MimerPy and Mimer API version numbers
    $ python3 -m mimerpy -v
    Mimerpy   version 1.1.0
    Mimer API version 11.0.5B
    $ python3 -m mimerpy -d pesc110 -u SYSADM -p SYSADM 'select current_date from system.onerow'
    ('2021-03-09',)

The last command shows that you can connect to a database by
specifying a database name, a user name, a password, and then an SQL
statement. If the statement returns a result, it will be displayed as
a list of tuples_ (in Python syntax).

If you have defined a default database and an OS_USER, you can omit
the database connection details and use the following command:

.. code-block:: console

    $ python3 -m mimerpy 'select current_date from system.onerow'
    ('2021-03-09',)


.. _list: https://docs.python.org/3/tutorial/introduction.html#lists
.. _tuples: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences

Establishing a connection
------------------------------------------------
In your Python interpreter:

.. code-block:: console

    >>> import mimerpy

      # Creating a connection
    >>> con = mimerpy.connect(dsn="mimerDB", user="mimerUser", password="password")

If no errors occurred, a connection has been established.

.. seealso:: Information on :ref:`Connection parameters`.

Executing statements
--------------------
After establishing a connection you are ready to create a cursor and
start executing statements:

.. code-block:: console

  >>> import mimerpy

    # Creating a connection
  >>> con = mimerpy.connect(dsn ="mimerDB", user="mimerUser", password="password")

    # Creating a cursor
  >>> cur = con.cursor()

    # Executes a query
  >>> cur.execute("create databank testbank")

    # Committing the changes
  >>> con.commit()

Remember that in Python all :meth:`execute`-statements have to be
committed (unless autocommitmode=true), or they will be rolled back after the connection is
closed. See :ref:`cursorclass` for more information.

Running your first program
---------------------------
Just like in the Python interpreter, MimerPy can be run from a file.
In this example the following file is used: :download:`dbtest.py <dbtest.py>`::

  import mimerpy

  # Creating a connection
  con = mimerpy.connect(dsn ="testDB11", user="SYSADM", password="SYSADM")

  # Creating a cursor
  cur = con.cursor()

  # Creating a databank
  cur.execute("create databank bankoftest")

  # Creating a table
  cur.execute("create table test_table(c1 NVARCHAR(128)) in bankoftest")

  # Inserting a string
  cur.execute("insert into test_table values ('Using MimerPy is easy!')")

  # Selecting the inserted string
  cur.execute("select * from test_table")

  # Fetching the data from the result set
  fetchValue = cur.fetchall()

  # Closing the cursor
  cur.close()

  # Committing the changes
  con.commit()

  # Closing the connection
  con.close()

  # Printing the result from fetchall()
  print(fetchValue[0])

If we run dbtest.py we get:

.. code-block:: console

  $ python3 dbtest.py
  Using MimerPy is easy!

For more examples visit :ref:`Code examples`. For help with Mimer SQL
query syntax visit :ref:`User guide`.
