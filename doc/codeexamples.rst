***************
Code examples
***************

.. _more-examples:

The following section shows a few short and useful examples how to use :mod:`mimerpy` efficiently with the correct syntax.

The aim of these examples are to illustrate some useful methods and clarify the correct usage of the module's content.

Inserting a ``BLOB``
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

The ``with`` statement is a useful tool as it allows the user to open a connection or cursor without having to explicitly close it and changes done within the with's scope are automatically comitted.

The following example uses ``with`` for a :class:`Connection`::

  >>> import mimerpy

      # Opening a connection and executing statements with it. Changes are automatically committed
  >>> with mimerpy.connect(dsn = "dbname", user = "username", password = "password") as conn:
      ...   conn.execute("CREATE TABLE with_table_connection(c1 INTEGER, c2 VARCHAR(32))")
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
        ...   cur.execute("CREATE TABLE with_table_cursor(c1 INTEGER, c2 VARCHAR(32))")
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

.. seealso:: :ref:`connectionclass` or :ref:`cursorclass` documentation.

Iterating a result set
-----------------------


The same table that was used in the :ref:`Using with <Using_with>` example is used to illustrate possibility of iterating a result set::

  >>> import mimerpy

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  >>> cur = conn.cursor()
  >>> cur.execute("SELECT * from with_table_cursor")

      # Iterating the result set
  >>> for value in cur:
  ...     print(value)
  ...
  # The output
  (1, 'This is an example')
  (2, 'on how to use')
  (3, 'the with functionality.')

  >>> cur.close()
  >>> conn.close()

.. seealso:: :ref:`cursorclass` documentation.

Scrolling
------------------------

This example shows how a :class:`ScrollCursor` and its attribute :attr:`rownumber`:
can be used and::

  >>> import mimerpy

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  >>> cur = conn.cursor(scrollable = 'True')

      # Creating and inserting value to table
  >>> cur.execute("CREATE TABLE scroll_example(c1 INTEGER, c2 VARCHAR(32))")
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
performing several executes.However, this can be done by using the method
:meth:`executemany` once. See the following example::

  >>> import mimerpy

  >>> conn = mimerpy.connect(dsn = "dbname", user = "username", password = "password")

  >>> cur = conn.cursor()

      # Creating a table with a BLOB column
  >>> cur.execute("CREATE TABLE executemany_table (c1 INTEGER, c2 VARCHAR(32))")

      # Inserting two rows into the table
  >>> cur.executemany("INSERT INTO executemany_table VALUES (?,?)", (((1, "This is an example"), (2, "on how to use executemany."))))

      # Committing and closing the cursor and connection
  >>> conn.commit()
  >>> cur.close()
  >>> conn.close()

.. seealso:: :ref:`cursorclass` documentation.

Transaction loop
------------------------

You often want to guarantee the completion of a transaction by retrying
it if it fails. See the following example::

    import mimerpy
    from mimerpy.mimPyExceptions import DatabaseError, TransactionAbortError

    def important_transaction(con, retries = 10):
        if retries <= 0: 
            return 0
        try: 
            cursor = con.cursor()
            cursor.execute("CREATE TABLE poff (c1 INTEGER, c2 FLOAT) in pybank")
            cursor.execute("INSERT into poff values (:a, :b)", (5, 5.5))
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

.. Messages
.. --------------
