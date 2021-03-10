**************************
Python and Mimer datatypes
**************************

This section discusses the relationship between Python3 data types and
MimerSQL data types.

-----------------------------------------

Overview of MimerSQL to Python data types:

+------------------------+--------------------+
| MimerSQL               | Python3            |
|                        |                    |
+========================+====================+
| BOOLEAN                | Bool               |
+------------------------+--------------------+
| INTEGER                | Int                |
+------------------------+--------------------+
| BIGINT                 | Int                |
+------------------------+--------------------+
| SMALLINT               | Int                |
+------------------------+--------------------+
| DOUBLE                 | Float              |
+------------------------+--------------------+
| FLOAT                  | Float              |
+------------------------+--------------------+
| REAL                   | Float              |
+------------------------+--------------------+
| BINARY                 | bytes              |
+------------------------+--------------------+
| BLOB                   | bytes              |
+------------------------+--------------------+
| NCLOB                  | Str                |
+------------------------+--------------------+
| NVARCHAR               | Str                |
+------------------------+--------------------+
| NULL                   | NoneType           |
+------------------------+--------------------+


``BOOLEAN``
^^^^^^^^^^^^

In Python all objects can act as a ``BOOLEAN``. With this in mind, a parameter
marker insert can be performed with any Python object to a Mimer ``BOOLEAN``
column and Mimerpy will accept this. Consider the following example::

  >>> cur.execute("create table booltable(c1 BOOLEAN)")

  >>> cur.executemany("insert into booltable values (?)", [(None,), (1,), (0,), (3.1415,), ("potato",), ('banana',)])

All of the paramarkers are of accepted Python boolean types and in the
database these values will be stored as ``False``, ``True``,
``False``, ``True``, ``True`` and ``True``. For more information on
Python3 built-in types and truth values testing please visit `Built-in
Types`_.

.. _Built-in Types: https://docs.python.org/3/library/stdtypes.html#truth-value-testing

``INTEGER``, ``BIGINT & SMALLINT``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because Python3 only uses one data type for the three corresponding
MimerSQL integer types, it's the responsibility of the user to stay
within the limits.  If a value is too large or too small for a number
(``INTEGER``, ``BIGINT`` or ``SMALLINT``) column, a
:exc:`ProgrammingError` will be raised. The following limits apply:

+------------------------+----------------------+
| MimerSQL data type     | Range of values      |
|                        |                      |
+========================+======================+
| INTEGER                | -2^31 to 2^31 - 1    |
+------------------------+----------------------+
| BIGINT                 | -2^64 to 2^64 - 1    |
+------------------------+----------------------+
| SMALLINT               | -2^16 to 2^16 - 1    |
+------------------------+----------------------+

``DOUBLE PRECISION, FLOAT & REAL``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``DOUBLE PRECISION``, ``FLOAT`` and ``REAL`` conform to 64-bit and
32-bit IEEE floating point numbers. Mimer will not accept NaN, +Inf or
-Inf. And it will convert the distinct value -0.0 to 0.0.

+------------------------+----------------------+-----------+
| MimerSQL data type     | Range of values      | IEEE type |
|                        |                      |           |
+========================+======================+===========+
| DOUBLE PRECISION       | -10^308 to 10^308    | 64-bit    |
+------------------------+----------------------+-----------+
| FLOAT                  | -10^308 to 10^308    | 64-bit    |
+------------------------+----------------------+-----------+
| REAL                   | -10^38 to 10^38      | 32-bit    |
+------------------------+----------------------+-----------+

``BINARY``
^^^^^^^^^^^^
.. _BINARY:

In Python3 there are many ways to create a ``BINARY`` object. One way
is to using the ``b'`` tag, another way is to use the ``to_bytes``
method, or you can use the ``bytearray`` method. When specifying a
parameter for ``BINARY`` column, Mimerpy expects it to be a
`bytes-like object`_.

Example usage of binary:

.. code-block:: console

  >>> b.execute("create table binarytable (c1 BINARY(3))")
  >>> b.execute("insert INTO binarytable VALUES (?)", (b'A01'))

.. seealso:: `Binary data`_, for more information.

.. _bytes-like object: https://docs.python.org/3/glossary.html#term-bytes-like-object
.. _Binary data: https://docs.python.org/3/library/binary.html

``BLOB`` 
^^^^^^^^^^^^^^^^^^^^^^^^^

Just like :ref:`BINARY <BINARY>` but for larger objects. Like binary
columns it expects the a parameter to be a `bytes-like object`_.

Example usage of ``BLOB``::

  >>> cur.execute("create table blob_table (c1 BLOB)")
  >>> with open("examplepicture.jpg", 'rb') as input_file:
  ...      ablob = input_file.read()
  ...      cur.execute("insert INTO blob_table VALUES (?)", (ablob))

``CLOB``
^^^^^^^^^^
.. _CLOB:

The ``CLOB`` column is used for storing large string objects. It can
store all Latin-1 characters.

Example usage of ``CLOB``::

  >>> cur.execute("create table clob_table (c1 CLOB) in databank")
  >>> with open("longbook.txt", 'r') as input_file:
  ...      aclob = input_file.read()
  ...      cur.execute("insert INTO clob_table VALUES (?)", (aclob))

``NCLOB``
^^^^^^^^^^
Just like :ref:`CLOB <CLOB>`, but can hold all Unicode code-points.

Example usage of ``NCLOB``::

 >>> cur.execute("create table nclob_table (c1 NCLOB)")
 >>> with open("chineseBook.txt", 'r') as input_file:
 ...      anclob = input_file.read()
 ...      cur.execute("insert INTO nclob_table VALUES (?)", (anclob))

``NULL``
^^^^^^^^^^^^
The Python data type ``None`` is mapped to ``NULL`` in
Mimerpy. MimerSQL ``NULL`` values will be returned as ``None`` in
Python. Consider the following example::

  >>> cur.execute("create table booltable(c1 INTEGER)")
  >>> cur.execute("insert into booltable values (NULL)")
  >>> cur.execute("insert into booltable values (?)", (None))

In the database both values will be stored as ``NULL``. When selected,
they are both shown as ``None`` in Python.
