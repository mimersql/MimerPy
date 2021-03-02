..
    PLACEHOLDER FILE, THE TEXT FOR THE documentation FOR THIS FILE IS IN mimerpy.rst
******************************
Connection class
******************************

.. _PEP 249: https://www.python.org/dev/peps/pep-0249/

.. class:: Connection

   The class Connection is used to establish a connection with a Mimer database.

Methods
------------------------
.. method:: connect(dsn = None, user = None, password = None, 'autocommit' = None, 'errorhandler' = None)

  Constructor for creating a connection to the database using the class Connection. Returns a :class:`Connection object` To establish a default connection with a Mimer database
  the following parameters are required:

  * *dsn* -- Data source name as a string
  * *user* -- Username as a string
  * *password* -- Password as a string

  This will create the default connection according the `PEP 249`_ specification.

  The connection's auto-commit feature is initially turned off and the default errorhandler is used. However, the following parameters can be set when creating a new connection:

  * *autocommit* -- If '*autocommit*' = ``None`` or unspecified, auto-commit mode is turned off (as by default). If '*autocommit*' = ``True``
    queries will be auto committed.
  * *errorhandler* -- If '*errorhandler*' = ``None`` or unspecified, the default errorhandler is used. However, the user can choose to
    use their own errorhandler of choice by setting this parameter.

.. method:: close()

  Method is used for closing a connection. When using :meth:`~close` all cursors that are using the connection are also closed.

  If the auto-commit feature is turned off and a connection is closed before committing any changes, an implicit rollback is executed. Thus, before evoking :meth:`~close`,
  :meth:`commit` should be used to prevent any changes being lost. However, if auto-commit  is turned on, an implicit rollback is not performed.

  When a connection has been closed using :meth:`~close`, it is unusable and a :meth:`~ProgrammingError` is raised if any operations are attempted on the connection.

.. method:: commit()

  Commits the pending transaction to the database.

  .. note:: If :meth:`~commit` is not performed on a connection, all pending transactions are implicitly rollbacked and all data manipulation performed during the transaction is lost.

  To use the auto-commit feature on the connection, see :meth:`~autocommit`.

.. method:: rollback()

  Causes the database to roll back to the start of any pending transaction. If a connection is closed without committing any changes made during the transaction, a rollback is implicitly performed.

.. method:: cursor('scrollable'  = False)

  Returns a new :class:`~Cursor` object using the connection.

  If *scrollable* is unspecified, the default cursor class will be returned. If *scrollable* = ``True``
  a scrollable cursor will be returned, see :class:`Cursor <ScrollCursor>`.

.. method:: execute(query, [,parameters])

  This method is not included in the standard implementation. It returns a :class:`~Cursor` object and executes the query.

.. method:: executemany(query, seq_of_parameters)

  This method is not included in the standard implementation. It returns a :class:`~Cursor` object and executes the query against all the parameter sequences.

Attributes
------------------------
.. attribute:: autocommitmode

  Attribute determines if the connection will auto-commmit any changes or if :meth:`~commit` has to be performed explicitly.
  This is set to False by default unless otherwise stated when opening the connection or using :meth:`~autocommit` to change this attribute.

Extensions
------------------------

.. method:: autocommit(bool)

This method is used to turn on or off the auto-commit feature on the connection. This means that by using this method, from this point onward changes are autocommitted.

Turns on auto-commit feature if boolean value ``True`` and turns it off if ``False``.

.. Warning:: If :meth:`~autocommit` is called, all changes that have not yet been committed during the current transaction are rolled back and the auto-commit feature is later turned on. To prevent this, either set '*autocommit*' = ``True`` when opening a connection or use method :meth:`~commit` before
            using :meth:`~autocommit`.

.. attribute:: messages

Attribute where if raised, exception class and exception value are appended to. If connection has at least one cursor, then the error will be appended to the
cursor's messages attribute, otherwise the error is appended to the connection's messages attribute.

.. attribute:: errorhandler

  The attribute states what errorhandler is used. This is set to the default unless otherwise stated when opening the connection. For further information, see
  :doc:`exceptions`.
