***************
Code examples
***************

.. _more-examples:

The following section shows a few short and useful examples how to use :mod:`mimerpy` efficiently.

The aim of these examples are to illustrate some useful methods and clarify the correct usage of the module's content.

Inserting a BLOB
------------------------

The following example inserts the picture *mimer.jpg* as a ``BLOB`` into a table::

  >>> import mimerpy

  # Establishing a connection
  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  # Opening a cursor
  >>> cur = conn.cursor()

  # Creating a table with a BLOB column
  >>> cur.execute("CREATE TABLE blob_table (blobcolumn BLOB)")

  # Reading from the .jpg file in binary mode
  >>> with open("mimer.jpg", 'rb') as input_file:
  ...      insert_blob = input_file.read()
  ...      cur.execute("INSERT INTO blob_table VALUES (?)", (insert_blob))
  ...
  # Committing and closing the cursor and connection
  >>> conn.commit()
  >>> cur.close()
  >>> conn.close()

.. seealso:: see :ref:`BINARY <BINARY>` documentation.

Using `with`
---------------------------
.. _Using_with:

The Python ``with`` statement is a useful tool as it allows the user to open a connection or cursor without having to explicitly close it. Changes done within the with's scope are automatically comitted.

The following example uses ``with`` for a :class:`Connection`::

  >>> import mimerpy

      # Opening a connection and executing statements with it. Changes are automatically committed
  >>> with mimerpy.connect(dsn = "dbname", user = "username", password = "password") as conn:
      ...   conn.execute("INSERT INTO with_table_connection VALUES (?,?)", (1, "This is an example"))
      ...   conn.execute("INSERT INTO with_table_connection VALUES (?,?)", (2, "on how to use"))
      ...   conn.execute("INSERT INTO with_table_connection VALUES (?,?)", (3, "the with functionality."))
      ...
      # The connection has now been closed

When leaving the ``with``'s scope, the connection is closed and the inserted data is automatically committed.
We can open a new connection and check that the information was committed successfully::

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")
  >>> cur = conn.cursor()
  >>> cur.execute("SELECT * from with_table_cursor")
  >>> cur.fetchall()
  # The output
  [(1, "This is an example", (2, "on how to use"), (3, "the with functionality")]

  >>> cur.close()
  >>> conn.close()


The following example uses ``with`` for a :class:`Cursor`::

    >>> import mimerpy

    >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

        # Opening a cursor and executing statements with it. Changes are automatically committed
    >>> with conn.cursor() as cur:
        ...   cur.execute("INSERT INTO with_table_cursor VALUES (?,?)", (1, "This is an example"))
        ...   cur.execute("INSERT INTO with_table_cursor VALUES (?,?)", (2, "on how to use"))
        ...   cur.execute("INSERT INTO with_table_cursor VALUES (?,?)", (3, "the with functionality."))
        ...
        # The cursor has been closed, now closing the connection
    >>> conn.close()

When leaving the ``with``'s scope, the cursor is closed and the inserted data is automatically committed.
We can open a new connection and check that the information was committed successfully::

    >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")
    >>> cur = conn.cursor()
    >>> cur.execute("SELECT * from with_table_cursor")
    >>> cur.fetchall()
    # The output
    [(1, "This is an example"), (2, "on how to use"), (3, "the with functionality")]

    >>> cur.close()
    >>> conn.close()

The following example uses ``with`` for a :class:`PooledConnection`
The actual :class:`MimerPool` connection pool also support the ``with`` statement.

  >>> import mimerpy
  >>> pool = MimerPool(dsn="targetdb", user = "SYSADM", password = "SYSADM", maxconnections=10, initialconnections=1)
  >>> with pool.get_connection() as con:
  ...     print_pool_status("del_rows, in with")
  ...     con.execute("delete from my_tab")
  ...     con.commit() 

.. seealso:: :ref:`connectionclass` or :ref:`cursorclass` documentation.

Iterating a result set
-----------------------


The same table that was used in the :ref:`Using with <Using_with>` example is used to illustrate possibility of iterating a result set::

  >>> import mimerpy

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  >>> cur = conn.cursor()
  >>> cur.execute("SELECT * from with_table_cursor")

      # Iterating the result set
  >>> for ix, str in cur:
  ...     print(ix, str)
  ...
  1 This is an example
  2 on how to use
  3 the with functionality.

  >>> cur.close()
  >>> conn.close()

.. seealso:: :ref:`cursorclass` documentation.

Scrolling
------------------------

This example shows how a :class:`ScrollCursor` and its attribute :attr:`rownumber`
can be used and::

  >>> import mimerpy

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  >>> cur = conn.cursor(scrollable = 'True')

      # Creating and inserting value to table
  >>> cur.execute("INSERT INTO scroll_example VALUES (?,?)", (1, "This is an example"))
  >>> cur.execute("INSERT INTO scroll_example VALUES (?,?)", (2, "on how to use"))
  >>> cur.execute("INSERT INTO scroll_example VALUES (?,?)", (3, "a ScrollCursor."))
  >>> cur.execute("INSERT INTO scroll_example VALUES (?,?)", (4, "This is very"))
  >>> cur.execute("INSERT INTO scroll_example VALUES (?,?)", (5, "useful and easy."))
  >>> cur.execute("INSERT INTO scroll_example VALUES (?,?)", (6, "Try it out!"))

      # Selecting the whole table
  >>> cur.execute("SELECT * from scroll_example")

      # Scrolling the result set
  >>> cur.scroll(5, mode='relative')
  >>> print(cur.fetchone())
  # The output
  (6, 'Try it out!')

      # Scrolling the result set
  >>> cur.scroll(0, mode='absolute')
  >>> print(cur.fetchone())
  # The output
  (1, 'This is an example')

      # We can also check the attribute rownumber
  >>>  print("The current rownumber: ", cur.rownumber)
  # The output
  The current rownumber:  1

      # Scrolling the result set
  >>> cur.scroll(3, mode='relative')
  >>> print(cur.fetchone())
  # The output
  (5, 'useful and easy')

      # The new rownumber
  >>>  print("The new rownumber: ", cur.rownumber)
  # The output
  The new rownumber:  5

      # Scrolling outside of the result set
  >>> try:
  ...     cur.scroll(10, mode='absolute')
  ... except IndexError as e:
          print("Oops IndexError!")
  ...
  # The output
  Oops IndexError!

  >>> cur.scroll(0, mode='absolute')
  >>> print(cur.fetchmany(3))
  # The output
  [(1, 'This is an example'), (2, 'on how to use'), (3, 'a ScrollCursor.')]

  >>> print(cur.fetchall())
  # The output
  [(4, 'This is very'), (5, 'useful and easy.'), (6, 'Try it out!')]

  >>> cur.close()
  >>> conn.close()

.. seealso:: :ref:`scrollcursorclass` documentation.


Executemany
------------------------

In the above examples values have been inserted into tables by subsequently
performing several executes. However, this can be done by using the method
:meth:`executemany` once. See the following example::

  >>> import mimerpy

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  >>> cur = conn.cursor()

      # Inserting two rows into the table
  >>> cur.executemany("INSERT INTO executemany_table VALUES (?,?)", (((1, "This is an example"), (2, "on how to use executemany."))))

      # Committing and closing the cursor and connection
  >>> conn.commit()
  >>> cur.close()
  >>> conn.close()

.. seealso:: :ref:`cursorclass` documentation.

Error handling
------------------------
This example shows how to handle error situations using the database execptions::
    
    import mimerpy
    from mimerpy.mimPyExceptions import DataError, DatabaseError, IntegrityError

    def insert_row(con):
        try: 
            cursor = con.cursor()
            cursor.execute("INSERT into mytable values (:a, :b)", (5, 5.5))
        except IntegrityError as e:
            print("Integrity error :", e)
            return 0
        except DataError as e:  
            print("Data error:", e.message)
            return 0
        except DatabaseError as e:
            print("Unhandled database error:", e.message)
            print("Mimer error code: ", e.errno )
            return 0
        return 1

    if __name__ == "__main__":
        con = mimerpy.connect(dsn="pymeme", user = "SYSADM", password = "SYSADM")
        result = insert_row(con)
        if result == 1: 
            print("Succsess!")
        else:
            print("Failure!")


Transaction loop
------------------------
It is often useful to redo a transaction if it fails. There is never a
guarantee that a transaction completes. However, a program can be written so it
retries if it fails. The following example is one way of retrying a
failed transaction::

    import mimerpy
    from mimerpy.mimPyExceptions import DatabaseError, TransactionAbortError

    def important_transaction(con):
        try: 
            cursor = con.cursor()
            cursor.execute("INSERT into mytable values (:a, :b)", (5, 5.5))
            con.commit()
        except TransactionAbortError as e:
            con.rollback()
            return 0
        except DatabaseError as e:
            con.rollback()
            print("Unexpected non-database error:", e)
            return -1
        return 1

    if __name__ == "__main__":
        con = mimerpy.connect(dsn="pymeme", user = "SYSADM", password = "SYSADM")
        laps = 0
        while laps <= 10:
            result = important_transaction(con)
            if result == 1:
                break
            laps = laps + 1

        if result == 1: 
            print("Succsess!")
        else:
            print("Failure!")

.. seealso:: :ref:`TransactionAbortError <TransactionAbortError>` documentation.

Alternative Transaction loop
-------------------------------
The following example is alternative way of retrying a transaction if it fails using recursion:::

    import mimerpy
    from mimerpy.mimPyExceptions import DatabaseError, TransactionAbortError

    def important_transaction(con, retries = 10):
        if retries <= 0: 
            return 0
        try: 
            cursor = con.cursor()
            cursor.execute("INSERT into mytable values (:a, :b)", (5, 5.5))
            con.commit()
        except TransactionAbortError as e:
            con.rollback()
            return important_transaction(con, retries - 1)
        except DatabaseError as e:
            con.rollback()
            print("Unexpected non-database error:", e)
            return 0
        return 1

    if __name__ == "__main__":
        con = mimerpy.connect(dsn="pymeme", user = "SYSADM", password = "SYSADM")
        result = important_transaction(con)
        if result == 1: 
            print("Succsess!")
        else:
            print("Failure!")

Using the connection pool
-------------------------------
The following example illustrates how to use the MimerPy connection pool::

    import mimerpy
    from mimerpy.pool import(MimerPool, MimerPoolError, MimerPoolExhausted)

    pool = None

    """ Create the following table:
        create table my_tab(id integer)
    """
    def insert_row(num):
        con = pool.get_connection()
        con.execute("INSERT into my_tab values (:a)", (num))
        con.commit()
        con.close()

    def sel_row():
        con = pool.get_connection()
        cursor = con.cursor()
        cursor.execute("select * from my_tab")
        for value in cursor:
            print(value)
        cursor.close()    
        con.close()

    if __name__ == "__main__":
        pool = MimerPool(dsn="targetdb", user = "SYSADM", password = "SYSADM", maxconnections=10)
        ins_values = (1,2,3,4,5)
        print("Inserting rows")
        for val in ins_values:
            insert_row(val)
        print("Selecting row")
        sel_row()
        print("Done")
        pool.close()

.. Messages
.. --------------
