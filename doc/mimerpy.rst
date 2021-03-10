**************************
The :mod:`mimerpy` module
**************************

The module
****************

.. _PEP 249: https://www.python.org/dev/peps/pep-0249/

The :mod:`mimerpy` module enables the creation of connections to Mimer
databases and the opening of cursors to execute MimerSQL statements.

Constructor
------------

.. method:: connect(dsn = None, user = None, password = None, 'autocommit' = False, 'errorhandler' = None) 

  Constructor for creating a connection to the specified database
  using the :class:`Connection` class. Returns a :class:`Connection`
  object. To establish a default connection with a Mimer database the
  following parameters are required:

  * *dsn* -- Data source name as a string
  * *user* -- Username as a string
  * *password* -- Password as a string

  This will create the default connection according the `PEP 249`_
  specification.

  The connection's auto-commit feature is initially turned off and the default
  errorhandler is used. The following parameters can be set when creating
  a new connection:

  * *autocommit* -- If '*autocommit*' = ``False`` or unspecified,
    auto-commit mode is turned off (as by default). If '*autocommit*'
    = ``True`` queries will be automatically committed.

  * *errorhandler* -- If '*errorhandler*' = ``None`` or unspecified,
    the default errorhandler is used. The user can choose to use their
    own errorhandler of choice by setting this parameter.

Globals
----------

.. data:: __version__

  String that describes the version number of the :mod:`mimerpy` module.

.. data:: apilevel

  String that refers to the supported DB API level, which for :mod:`mimerpy`
  is ``2.0``.

.. data:: threadsafety

  Integer that states the thread safety of the interface.

  For :mod:`mimerpy` the thread safety is ``1`` this means that threads may share the module,
  but not connections, according with the `PEP 249 threadsafety`_ specification.

.. data:: paramstyle

  String that states what parameter marker format that is used. This
  has the value ``qmark``.

.. seealso:: Information on :ref:`Query structure`.


.. _connectionclass:

Connection
****************

.. _PEP 249 threadsafety: https://www.python.org/dev/peps/pep-0249/#threadsafety

.. Class:: Connection

  The class Connection is used to establish a connection with a Mimer database.

Connection Methods 
--------------------------------------

.. method:: close() 

  Method is used for closing a connection. The :meth:`~close`-method
  also closes all cursors opened with the connection.

  If the auto-commit feature is turned off and a connection is closed
  before committing any changes, an implicit roll back is
  executed. Thus, before evoking :meth:`~close`, :meth:`commit` should
  be used to prevent any changes being lost.  However, if auto-commit
  is turned on, changes are automatically committed.

  When a connection has been closed using :meth:`~close`, it is
  unusable and a :exc:`~ProgrammingError` is raised if any operations
  are attempted on the connection.

.. method:: commit() 

  Commits the pending transaction to the database.

  .. note:: If :meth:`~commit` is not performed on a connection, all
    pending transactions are implicitly rolled back and all data manipulation
    performed during the transaction is lost.

  For information on the auto-commit feature on the connection, see
  :meth:`~autocommit`.

.. method:: rollback() 

  Causes the database to roll back to the start of the transaction.
  If a connection is closed without committing changes made during
  the transaction, a :meth:`rollback` is implicitly performed.

.. method:: cursor('scrollable'  = False) 

  Returns a new :class:`~Cursor` object using the connection.

  If *scrollable* is unspecified, the default cursor class will be
  returned. If *scrollable* = ``True`` a :class:`ScrollCursor` will be
  returned.

.. method:: execute(query, [,parameters]) 

  This method is not included in the `PEP 249`_. It returns a
  :class:`~Cursor` object and executes the query.

.. method:: executemany(query, seq_of_parameters) 

  This method is not included in the `PEP 249`_. It returns a
  :class:`~Cursor` object and executes the query against all the
  parameter sequences.

Connection Attributes 
----------------------------------------
.. attribute:: autocommitmode 

  Attribute determines if the connection will auto-commmit any changes
  or if :meth:`~commit` has to be performed explicitly.  This is set
  to ``False`` by default unless otherwise stated when opening the
  connection or by using the :meth:`~autocommit` method to change this
  attribute.

Connection Extensions 
------------------------------------------

.. method:: autocommit(bool) 

  This method is used to turn on or off the auto-commit feature on the
  connection.  By using this method, from this point onward changes
  are automatically committed.

  Turns on auto-commit feature if boolean value ``True`` and turns it
  off if ``False``.

.. Warning:: If :meth:`~autocommit` is called, all changes that have
            not yet been committed during the current transaction are
            rolled back and the auto-commit feature is later turned
            on. To prevent this, either set '*autocommit*' = ``True``
            when opening a connection or use method :meth:`~commit`
            before using :meth:`~autocommit`.

.. attribute:: messages 

  Attribute where if raised, exception class and exception value are
  appended to. If connection has at least one cursor, then the error
  will be appended to the cursor's messages attribute, otherwise the
  error is appended to the connection's messages attribute.  The aim
  of this attribute is to eliminate the need for a :exc:`Warning`
  exception which often causes problems.

.. attribute:: errorhandler 

  The attribute states what errorhandler is used. This is set to the
  default unless otherwise stated when opening the connection. For
  further information, see :doc:`exceptions`.

.. method:: __enter__()

  Returns self which enables the connections's compatibility with the
  Python ``with`` statement.

.. seealso:: :ref:`Using with <Using_with>` for an example how this is used.

.. _cursorclass:

Cursor
****************

.. class:: Cursor 

  The class cursor is used to execute MimerSQL statements and manage
  data result sets.

  Cursors that have been created from the same connection are not
  isolated. This means if data is manipulated by a cursor, this is
  visible to all other cursors created with that connection. Changes
  made by a cursor are not visible to other cursors created from
  *different* connections until the changes are committed or unless
  the connection's attribute :attr:`~autocommitmode` is set to
  ``True``. If auto-commit is turned on, changes made to the database
  are visible to all cursors independent on their connection.

  A cursor can be opened either by calling :meth:`Connection.cursor()
  <cursor>`, :meth:`Connection.execute() <execute>` or
  :meth:`Connection.executemany() <executemany>`.


Cursor Methods
----------------

.. method:: close() 

  Closes a cursor. From this point onwards the cursor is unusable and
  a :exc:`~ProgrammingError` is raised if any operations are attempted
  on the connection.

.. method:: execute(query, [,parameters]) 

  Prepares and executes a SQL statement.

  The input parameter *parameters* is optional, as queries can either
  contain data or parameter markers can be used, see :ref:`User guide`
  for more information.

.. method:: executemany(query, seq_of_parameters) 

  Prepares and executes a SQL statement against all parameters in
  *seq_of_parameters*.

.. seealso:: :ref:`User guide`, for the correct syntax of these methods.

.. method:: fetchone() 

  Fetches the next row of a result set. The row is returned as a tuple. If
  no more data is available, ``None`` is returned.

  If :meth:`~fetchone` is called and the previous call to
  :meth:`~execute` did not produce a result set, a
  :exc:`~ProgrammingError` is raised.

.. method:: fetchmany([size=cursor.arraysize]) 

  Fetches the next rows of a result set. The rows are returned as a
  list of tuples. If no more data is available, an empty list is
  returned.

  The method fetches the number of rows specified by the parameter. If
  unspecified, the cursor's :attr:`arraysize` is used. If the size of
  the fetch is larger than the number of rows available in the result
  set, the remaining rows are returned.

  If the size parameter is specified, the cursor's :attr:`arraysize`
  is changed and if :meth:`~fetchmany` is called upon again without a
  specified size, the new :attr:`arraysize` is used.

  If :meth:`~fetchmany` is called and the previous call to
  :meth:`~execute` did not produce a result set, a
  :exc:`~ProgrammingError` is raised.

.. method:: fetchall() 

  Fetches the remaining rows of a result set. The rows are returned as
  a list of tuples.  If no more data is available, an empty list is
  returned.

  If :meth:`~fetchall` is called and the previous call to
  :meth:`~execute` did not produce a result set, a
  :exc:`~ProgrammingError` is raised.

.. method:: setinputsizes() 

  The method does not do anything but is a requirement from the DB-API
  `PEP 249`_.

.. method:: setoutputsize() 

  The method does not do anything but is a requirement from the DB-API
  `PEP 249`_.


Cursor Attributes 
--------------------------------------

.. attribute:: description 

  A read-only attribute that is a sequence of 7-item sequences. Each
  sequence stores information regarding the latest result column:

  * name
  * type_code
  * display_size
  * internal_size
  * precision
  * scale
  * null_ok

  Only name and type_code are specified, the rest of the items are set
  to ``None``.

  ``name`` provides the name of the result column and ``type_code``
  specifies the native Mimer SQL C API type code for the column.

.. attribute:: rowcount 

  Read-only attribute that specifies the number of updated rows that
  the last :meth:`~execute` performed. For example performing an
  ``INSERT``, ``UPDATE`` or ``DELETE`` statement, the attribute is
  changed.

.. attribute:: arraysize 

  Read-write attribute which specifies the number of rows to be
  fetched with :meth:`~fetchmany`. By default this is set to ``1``
  when a cursor is opened, thus it will fetch one row at a time from
  the result set until it is changed by calling :meth:`~fetchmany`
  with a different size.


Cursor Extensions 
--------------------------------------

.. attribute:: connection

  Read-only attribute which returns a reference to the connection at
  which the cursor was created.

.. attribute:: messages 

  List where an exception class and value is appended to as a tuple
  that the interface receives from the underlying database.  The aim
  of this attribute is to eliminate the need for a Warning exception
  which often causes problems.

  The list is cleared prior to executing all standard cursor methods
  except :meth:`fetch*() <fetchone>`.

.. method:: next() 

  Returns the next row in a result set, with the same semantics as
  :meth:`~fetchone`. If there is no more data available in the result
  set, a ``StopIteration`` exception is raised.

.. method:: __iter__() 

  Returns self which enables the cursor's compatibility with iteration.

.. seealso:: :ref:`Iterating a result set`, for an example how this
             can be used.

.. attribute:: errorhandler 

  The attribute states what errorhandler is used. This is set to the
  default unless otherwise stated when opening the connection. For
  further information, see :doc:`exceptions`.

.. method:: __enter__()

  Returns self which enables the cursor's compatibility with the Python ``with`` statement.

.. seealso:: :ref:`Using with <Using_with>`, for an example how this
             can be used.

.. _scrollcursorclass:

ScrollCursor 
------------------

.. class:: ScrollCursor 

  ``ScrollCursor`` is a subclass to the :class:`~Cursor`-class where
  the cursor can be scrolled to new positions in the result set.  All
  methods in the baseclass :class:`~Cursor` can also be used by a
  ``ScrollCursor``.

  When opening a cursor by using the method :meth:`Connection.cursor()
  <cursor>`, if the parameter *scrollable* is set to ``True``, the
  cursor will be scrollable and an instance of ``ScrollCursor``.  If
  not specified, the cursor is by default not scrollable.

  .. Note:: A ``ScrollCursor`` fetches the whole result set to the client.


ScrollCursor Methods 
^^^^^^^^^^^^^^^^^^^^^^^^^

.. method:: scroll(value [, mode='relative']) 

  Method scrolls the cursor to a new position according to the *mode*
  of the scroll.

  The *mode* of the cursor is set to ``relative`` by default. This
  changes the cursor's position by *value* number of rows in relation
  to the current position of the cursor. If *mode* is set to
  ``absolute`` the cursor is moved *value* number of rows down from
  the absolute position.

  If the method is called upon and desired position in the result set
  does not exist, an :exc:`IndexError` is raised.

ScrollCursor Attributes
^^^^^^^^^^^^^^^^^^^^^^^^

.. attribute:: rownumber

  A read-only attribute that specifies the zero-based index of the
  cursor in the result set.

  This is set to ``None`` until a statement resulting in a result set
  i performed.

  If a fetch operation is performed on the result set, the next row to
  fetch is the row with the :attr:`rownumber` as index.

.. attribute:: rowcount

  Same as for :class:`Cursor`, but is also updated whenever a
  ``SELECT`` statement is executed.
