**********
Exceptions
**********

.. _ref-exceptions:
.. _Mimer SQL Documentation: https://developer.mimer.com/products/documentation/
.. _Documentation page: https://developer.mimer.com/products/documentation/
.. _Exception: https://docs.python.org/3/library/exceptions.html#Exception
.. _PEP 249: https://peps.python.org/pep-0249/

The following section describes the implementation of the exception hierarchy
stated in the DB-API `PEP 249`_.

Database Exceptions
------------------------

The database exceptions are defined in :mod:`mimerpy.mimPyExceptions`.

.. seealso:: :ref:`Error handling`, for an example how this can be used.

Exception inheritance layout:

::

  Exception
  ├── Warning
  └── Error
      ├── InterfaceError
      └── DatabaseError
          ├── DataError
          ├── OperationalError
          │   └── TransactionAbortError
          ├── IntegrityError
          ├── InternalError
          ├── ProgrammingError
          └── NotSupportedError

.. exception:: Exception

  Base class for the exceptions in the hierarchy above. 
  The built-in Python `Exception`_.

.. exception:: Warning

  Exception raised for important warnings like data truncations while
  inserting, etc.  It is a subclass of :exc:`Exception`.

.. exception:: Error

  Exception that is the base class of all other error exceptions. Can be used
  to catch all errors with one single except statement.
  It is a subclass of :exc:`Exception`.

.. exception:: InterfaceError

  Exception raised for errors that are related to the database
  interface rather than the database itself. For example if a
  parameter is specified in the wrong format. It is a subclass of
  :exc:`Error`.

.. exception:: DatabaseError

  Exception raised for errors that are related to the database.
  It is a subclass of :exc:`Error`.

.. exception:: DataError

  Exception raised for errors that are due to problems with the processed data
  like division by zero, numeric value out of range, etc. It is a subclass of
  :exc:`DatabaseError`.

.. exception:: OperationalError

  Exception raised for errors that are related to the database's operation and
  not necessarily under the control of the programmer, e.g. an unexpected
  disconnect occurs, the data source name is not found, a transaction could not
  be processed, a memory allocation error occurred during processing, etc.
  It is a subclass of :exc:`DatabaseError`.

.. _TransactionAbortError:

.. exception:: TransactionAbortError

  Exception raised when the database cannot commit a transaction. The
  transaction is rolled back. It is a subclass of
  :exc:`OperationalError`. See :ref:`Transaction control` for more
  information.

.. exception:: IntegrityError

  Exception raised when the relational integrity of the database is affected,
  e.g. a foreign key check fails. It is a subclass of :exc:`DatabaseError`.

.. exception:: InternalError

  Exception raised when the database encounters an internal error,
  e.g. the cursor is not valid anymore, the transaction is out of
  sync, etc. It is a subclass of :exc:`DatabaseError`.

.. exception:: ProgrammingError

  Exception raised for programming errors, e.g. table not found or
  already exists, syntax error in the SQL statement, wrong number of
  parameters specified, etc.  It is a subclass of
  :exc:`DatabaseError`.

.. exception:: NotSupportedError

  Exception raised in case a method or database API was used which is
  not supported by the database.  It is a subclass of
  :exc:`DatabaseError`.

MimerPool Exceptions
------------------------

This section describes the exceptions for the MimerPy connection pool.

Exception inheritance layout:

::

  Exception
  └── MimerPoolError
      └── MimerPoolExhausted

.. exception:: Exception
  :noindex:

Base class for the exceptions in the hierarchy above. This is the built-in Python `Exception`_.

.. exception:: MimerPoolError

Exception rasied for general MimerPy connection pool errors.

.. exception:: MimerPoolExhausted

Exception raised when the connection pool is exhausted and no new :class:`PooledConnection` can be returned.

Messages
------------------------
This is a Python list object to which the interface appends tuples
(exception class, exception value) for all messages which the
interfaces receives from the underlying database for this cursor.

The list is cleared by all standard cursor methods calls (prior to
executing the call) except for the :meth:`fetch*() <fetchone>`.

All error and warning messages generated by the database are placed
into this list, so checking the list allows the user to verify correct
operation of the method calls.

.. seealso:: For further information regarding exception error codes, 
             see the Programmer’s Manual part of the Mimer SQL Documentation Set, located in the Mimer SQL Developer site `Documentation page`_.

.. Warnings
.. ------------------------
.. Currently not supported.

Errorhandler
------------------------
The standard error handler adds the error information to the
appropriate :attr:`messages` and raises the exception defined by the
given errorclass and errorvalue parameters.

If no errorhandler is set (the attribute is ``None``), the standard
error handling scheme as outlined above, is applied.
