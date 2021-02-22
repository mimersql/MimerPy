************
Cursor class
************

.. _PEP 249: https://www.python.org/dev/peps/pep-0249/


.. class:: Cursor

The class cursor is used to execute MimerSQL statements and manage data result sets.

Cursors that have been created from the same connection are not isolated. This means if data is manipulated by a cursor, this is visible to all other cursors
created with that connection. Changes made by a cursor are not visible to other cursors created from *different* connections unless the connection's attribute :attr:`~autocommitmode` is set to ``True``. If auto-commit is turned on, changes made to the database are visible to all
cursors independent on their connection.

A cursor can be opened either by calling :meth:`Connection.cursor() <cursor>`, :meth:`Connection.execute() <execute>` or :meth:`Connection.executemany() <executemany>`.


Methods
------------------------

.. method:: close()

  Closes a cursor. From this point onwards the cursor is unusable and a :meth:`~ProgrammingError` is raised if any operations are attempted on the connection.

.. method:: execute(query, [,parameters])

  Prepares and executes a SQL statement.

  The input parameter *parameters* is optional, as queries can either contain data or parameter markers can be used:

  .. code-block:: console

     $ cur.execute("INSERT INTO test_table VALUES (3)")
     $ cur.execute("INSERT INTO test_table VALUES (?)", (3))

  If the same query is executed two times in a row, it is reused.

.. method:: executemany(query, seq_of_parameters)

  Prepares and executes a SQL statement against all parameters found in *seq_of_parameters*.

  .. note:: *write something about DDL and selectstatement here*

.. method:: fetchone()

  Fetches the next row of a result set. The row is returned as a tuple. If
  no more data is available, None is returned.

  If :meth:`~fetchone` is called and the previous call to :meth:`~execute` did not produce a result
  set, a :meth:`~ProgrammingError` is raised.

.. method:: fetchmany([size=cursor.arraysize])

  Fetches the next rows of a result set. The rows are returned as a list of tuples. If
  no more data is available, an empty list is returned.

  The method fetches the number of rows specified by the parameter. If unspecified, the cursor's arraysize
  is used. If the size of the fetch is larger than the number of rows available in the result set,
  the available rows are returned.

  If the size parameter is specified, the cursor's :attr:`arraysize` is changed and if :meth:`~fetchmany` is called upon
  again without a specified size, the new :attr:`arraysize` is used.

  If :meth:`~fetchmany` is called and the previous call to :meth:`~execute` did not produce a result
  set, a :meth:`~ProgrammingError` is raised.

.. method:: fetchall()

  Fetches the remaining rows of a query result. The rows are returned as a list of tuples.  If
  no more data is available, an empty list is returned.

  If :meth:`~fetchall` is called and the previous call to :meth:`~execute` did not produce a result
  set, a :meth:`~ProgrammingError` is raised.

.. method:: setinputsizes()

  The method is a requirement from the DB-API `PEP 249`_ but does not do anything.

.. method:: setoutputsize()

  The method is a requirement from the DB-API `PEP 249`_ but does not do anything.


Attributes
------------------------

.. attribute:: description

  A read-only attribute that is a sequence of 7-item sequences. Each sequence stores information regarding the latest result column:

  * name
  * type_code
  * display_size
  * internal_size
  * precision
  * scale
  * null_ok

  Only name and type_code are specified, the rest of the items are set to ``None``.

  ``name`` provides the name of the result column and ``type_code`` specifies the native Mimer MICRO API type code for the column.

.. attribute:: rowcount

  Read-only attribute that specifies the number of updated rows that the last :meth:`~execute` performed. For example if performing
  a ``INSERT``, ``UPDATE`` or ``DELETE`` statement, the attribute is changed.

  .. note:: Currently for a cursor without the :meth:`~scroll` function,  a ``SELECT`` query does not change the value of the :attr:`rowcount`.

.. attribute:: arraysize

  Read-write attribute which specifies the number of rows to be fetched each time with :meth:`~fetchmany`. By default this is set to 1 when a cursor
  is opened, thus it will fetch one row at a time from the result set until changed by calling :meth:`~fetchmany` with the desired size.


Extensions
------------------------

.. attribute:: connection

  Read-only attribute which returns a reference to the connection at which the cursor was created.

.. attribute:: messages

  List where an exception class and value is appended to as a tuple that the interface receives from the underlying database.

  The list is cleared prior to executing all standard cursor methods except :meth:`fetch*() <fetchone>`

.. method:: next()

  Returns the next row in a result set, with the same semantics as :meth:`~fetchone`. If there is no more data available in the result set, a ``StopIteration`` exception is raised.

.. method:: __iter__()

  Returns self which enables the cursors compatible with iteration.

.. attribute:: errorhandler

  SKRIVA HÄR SKRIVA HÄR SKRIVA HÄR

ScrollCursor
------------------------

.. class:: ScrollCursor

  ``ScrollCursor`` is a subclass to the :class:`~Cursor`-class where the cursor can be scrolled to new positions in the result set.
  All methods in the baseclass :class:`~Cursor` are available to a ``ScrollCursor``.

  When opening a cursor by using the method :meth:`Connection.cursor() <cursor>`, if the parameter
  *scrollable* is set to ``True``, the cursor will be scrollable and an instance of :class:`ScrollCursor`. However, if not specified, the cursor is by default not scrollable.

  .. Note:: A ``ScrollCursor`` fetches the whole result set to the client.


Methods
^^^^^^^^^^^^^^^^^^^^^^^^

.. method:: scroll(value [, mode='relative'])

  Method scrolls the cursor to a new position according to the *mode* of the scroll.

  The *mode* of the cursor is set to ``relative`` by default. This changes the cursor's position by *value* number of rows in relation to the current position of the cursor. If
  *mode* is set to ``absolute`` the cursor is moved *value* number of rows down from the absolute position.

  If the method is called upon and desired position in the result set does not exist, an ``IndexError`` is raised.

Attributes
^^^^^^^^^^^^^^^^^^^^^^^^

.. attribute:: rownumber

A read-only attribute that specifies the zero-based index of the cursor in the result set.

This is set to ``None`` until a statement resulting in a result set i performed. 

If a fetch operation is performed on the result set, the next row to fetch is the row with the :attr:`rownumber` as index.

.. attribute:: rowcount

Same as for :class:`Cursor`. However, unlike for an instance of the base class, this is also updated whenever a ``SELECT`` statement is executed.
