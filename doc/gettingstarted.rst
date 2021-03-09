***************
Getting started
***************

With Mimerpy installed, before proceeding make sure that you have a
Mimer server of the corresponding version running. If you are
uncertain if you have a Mimer server running, or need help getting one
running, please visit the `Mimer documentation`_.

.. _Mimer documentation: https://developer.mimer.com/products/documentation/

Checking the Mimerpy installation
---------------------------------
While the primary use of Mimerpy is as a package used by other Python
programs, it is possible to use it a a stand-alone Python
program. This makes it easy to check if Mimerpy works as intended and
can connect to a started Mimer database server.

For example:

.. code-block:: console

    $ python -m mimerpy
    Use option -h to get help
    $ python -m mimerpy -h
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
      -v, --version         Display MimerPy and MimerAPI version numbers
    $ python -m mimerpy -v
    Mimerpy  version 1.0.29
    MimerAPI version 11.0.3D
    $ python -m mimerpy -d pesc110 -u SYSADM -p SYSADM 'select current_date from system.onerow'
    [('2021-03-09',)]

In this way you can connect to a database server and execute a SQL
statement.  If the statement returns a result, it will be displayed as
a list of tuples (in Python syntax).


Establishing a connection
------------------------------------------------
In your Python interpreter:

.. code-block:: console

    >>> import mimerpy

      # Creating a connection
    >>> con = mimerpy.connect(dsn ="mimerDB", user="mimerUser", password="password")

If no errors occurred, a connection has been established.

If you get the error *"ImportError: No module named 'mimerpy'"*, and you installed
Mimerpy with the help of pip, you can check your pip packages and make sure Mimerpy
is present in the list. On Unix you can use the command:

.. code-block:: console

  $ pip list | grep mimerpy

If nothing shows up, the installation was not completed successfully.

.. note:: Remember to run the Python version you installed Mimerpy on.

Executing statements
--------------------
After establishing a connection you are ready to create a cursor and start executing statements:

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

Bare in mind that in Python all :meth:`execute`-statements have to be committed,
or they will be rolled back after the connection is closed. See :ref:`cursorclass` for more
information.

Running your first program
---------------------------
Just like in the Python interpreter, Mimerpy can be run from a file.
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
  cur.execute("insert into test_table values ('Using Mimerpy is easy!')")

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
  Using Mimerpy is easy!

For more examples visit :ref:`Code examples`. For help with MimerSQL query syntax visit :ref:`User guide`.
