**********************************
Python and Mimer SQL data types
**********************************

This section discusses the relationship between Python3 data types and
Mimer SQL data types.

-----------------------------------------

Overview of Mimer SQL to Python data types:

+------------------------+--------------------+
| Mimer SQL              | Python3            |
|                        |                    |
+========================+====================+
| BOOLEAN                | Bool               |
+------------------------+--------------------+
| INTEGER                | Int                |
+------------------------+--------------------+
| INTEGER(p)             | Int                |
+------------------------+--------------------+
| BIGINT                 | Int                |
+------------------------+--------------------+
| SMALLINT               | Int                |
+------------------------+--------------------+
| DOUBLE PRECISION       | Float              |
+------------------------+--------------------+
| FLOAT                  | Float              |
+------------------------+--------------------+
| FLOAT(p)               | Decimal            |
+------------------------+--------------------+
| REAL                   | Float              |
+------------------------+--------------------+
| DECIMAL(p,s)           | decimal            |
+------------------------+--------------------+
| BINARY                 | bytes              |
+------------------------+--------------------+
| VARBINARY(n)           | bytes              |
+------------------------+--------------------+
| BLOB(n[K,M,G])         | bytes              |
+------------------------+--------------------+
| NCLOB(n)               | Str                |
+------------------------+--------------------+
| CHAR(n)                | Str                |
+------------------------+--------------------+
| VARCHAR(n)             | Str                |
+------------------------+--------------------+
| NCHAR(n)               | Str                |
+------------------------+--------------------+
| NVARCHAR(n)            | Str                |
+------------------------+--------------------+
| DATE                   | Str                |
+------------------------+--------------------+
| TIME(s)                | Str                |
+------------------------+--------------------+
| TIMESTAMP(s)           | Str                |
+------------------------+--------------------+
| UUID                   | uuid               |
+------------------------+--------------------+
| INTERVAL               | Str                |
+------------------------+--------------------+
| NULL                   | NoneType           |
+------------------------+--------------------+


BOOLEAN 
------------

In Python all objects can act as a ``BOOLEAN``. With this in mind, a parameter
marker insert can be performed with any Python object to a Mimer SQL ``BOOLEAN`` 
column and MimerPy will accept this. Consider the following example::

  >>> cur.execute("create table booltable(c1 BOOLEAN)")

  >>> cur.executemany("insert into booltable values (?)", [(None,), (1,), (0,), (3.1415,), ("potato",), ('banana',)])

All of the paramarkers are of accepted Python boolean types and in the
database these values will be stored as ``False``, ``True``,
``False``, ``True``, ``True`` and ``True``. For more information on
Python3 built-in types and truth values testing please visit `Built-in
Types`_.

.. _Built-in Types: https://docs.python.org/3/library/stdtypes.html#truth-value-testing

INTEGER, INTEGER(p), BIGINT, and SMALLINT
----------------------------------------------------

Because Python3 only uses one data type for the four corresponding
Mimer SQL integer types, it's the responsibility of the user to stay
within the limits.  If a value is too large or too small for a number
(``INTEGER``, ``BIGINT`` or ``SMALLINT``) column, a
:exc:`ProgrammingError` will be raised. The following limits apply:

+------------------------+-----------------------------------+
| Mimer SQL data type    | Values                            |
|                        |                                   |
+========================+===================================+
| INTEGER                | :math:`-2^{31} \:to\: 2^{31} - 1` |
+------------------------+-----------------------------------+
| INTEGER(p)             | **p decimal digits,**             |
|                        | :math:`1 <= p <= 45`              |
+------------------------+-----------------------------------+
| BIGINT                 | :math:`-2^64 \:to\: 2^64 - 1`     |
+------------------------+-----------------------------------+
| SMALLINT               | :math:`-2^-16 \:to\: 2^-16 - 1`   |
+------------------------+-----------------------------------+

DOUBLE PRECISION, FLOAT and REAL
------------------------------------------------------------
``DOUBLE PRECISION``, ``FLOAT`` and ``REAL`` conform to 64-bit and
32-bit IEEE floating point numbers. Mimer SQL will not accept NaN, +Inf or
-Inf. And it will convert the distinct value -0.0 to 0.0.
The approximate limits apply:

+------------------------+-----------------------------------+-----------+
| Mimer SQL data type    | Values                            | IEEE type |
+========================+===================================+===========+
| DOUBLE PRECISION       | :math:`-10^{308} \:to\: 10^{308}` | 64-bit    |
+------------------------+-----------------------------------+-----------+
| FLOAT                  | :math:`-10^{308} \:to\: 10^{308}` | 64-bit    |
+------------------------+-----------------------------------+-----------+
| REAL                   | :math:`-10^{38} \:to\: 10^{38}`   | 32-bit    |
+------------------------+-----------------------------------+-----------+


FLOAT(p) and DECIMAL(p,s)
------------------------------------------------------------
``FLOAT(p)`` describes a floating point value with p digits in the
decimal mantissa. This Mimer SQL type is not yet supported in MimerPy.

``DECIMAL(p,s)`` describes a decimal value with p digits, of which s
digits are after the decimal point. Values of this type are mapped to
Python decimal objects.

BINARY(n) 
---------------
.. _BINARY:

In Python3 there are many ways to create a ``BINARY`` object. One way
is to using the ``b'`` tag, another way is to use the ``to_bytes``
method, or you can use the ``bytearray`` method. When specifying a
parameter for ``BINARY`` column, MimerPy expects it to be a
`bytes-like object`_.  ``n`` specifies the length to be between 1 and 15 000.

Example usage of binary:

.. code-block:: console

  >>> b.execute("create table binarytable (c1 BINARY(3))")
  >>> b.execute("insert INTO binarytable VALUES (?)", (b'A01'))

.. seealso:: `Binary data`_, for more information.

.. _bytes-like object: https://docs.python.org/3/glossary.html#term-bytes-like-object
.. _Binary data: https://docs.python.org/3/library/binary.html

VARBINARY(n) 
-------------------

Just like :ref:`BINARY <BINARY>`, but can hold object of varying length.

Example usage of varbinary:

.. code-block:: console

  >>> b.execute("create table varbinarytable (c1 VARBINARY(10))")
  >>> b.execute("insert INTO varbinarytable VALUES (?)", (b'A01'))

BLOB(n[K|M|G]) 
-------------------------
Just like :ref:`BINARY <BINARY>` but for larger objects. Like binary columns it expects the a parameter to be a `bytes-like object`_. The BINARY LARGE OBJECT or BLOB data type stores binary string values of varying length up to the maximum specified as the large object length (n[K|M|G]).

The large object length is n, optionally multiplied by K|M|G.

Data stored in BLOB’s may only be stored in the database and retrieved again, it cannot be used in arithmetical operations.

If you specify <n>K, the length is <n> multiplied by 1 024.

If you specify <n>M, the length is <n> multiplied by 1 048 576.

If you specify <n>G, the length is <n> multiplied by 1 073 741 824.

If you do not specify large object length, Mimer SQL assumes that the length of the data type is 1M.

Example usage of ``BLOB``:

  >>> cur.execute("create table blob_table (c1 BLOB(1024), c2 BLOB(1024K), c3 BLOB(1024M), c4 BLOB(1024G)")
  >>> with open("examplepicture.jpg", 'rb') as input_file:
  ...      ablob = input_file.read()
  ...      cur.execute("insert INTO blob_table c1 VALUES (?)", (ablob))

CLOB(n[K|M|G])
--------------------
.. _CLOB:

The CHARACTER LARGE OBJECT (CLOB) data type stores character string values of varying length up to the maximum specified as the large object length (n[K|M|G]). It can store all Latin-1 symbols

The large object length is n, optionally multiplied by K|M|G.

You can specify the maximum length of the CLOB data type as the length of the column when you create the table.

Example usage of ``CLOB``::

  >>> cur.execute("create table clob_table (c1 CLOB) in databank")
  >>> with open("longbook.txt", 'r') as input_file:
  ...      aclob = input_file.read()
  ...      cur.execute("insert INTO clob_table VALUES (?)", (aclob))

NCLOB(n) 
--------------
Just like :ref:`CLOB <CLOB>`, but can hold all Unicode code-points.

Example usage of ``NCLOB``::

 >>> cur.execute("create table nclob_table (c1 NCLOB)")
 >>> with open("chineseBook.txt", 'r') as input_file:
 ...      anclob = input_file.read()
 ...      cur.execute("insert INTO nclob_table VALUES (?)", (anclob))

CHAR(n) 
-------------
The CHARACTER (CHAR) data type stores string values of fixed length in a column.

``n`` specifies the length of the CHAR data type as the length of the column when you create a table. ``n`` specifies the length to be any value between 1 and 15 000.

When Mimer SQL stores values in a column defined as CHAR, it right-pads the values with spaces to conform with the specified column length.

.. Note:: If you define a data type as CHARACTER or CHAR, that is, without specifying a length, the length of the data type is 1.

Example usage of ``CHAR(n)``::

 >>> cursor.execute("create table char_table(c1 nchar(5), c2 nchar(10))")
 >>> cursor.execute("insert into char_table values (:a,:b)", "char table"))

VARCHAR(n) 
-----------------
The CHARACTER VARYING, abbreviated CHAR VARYING or VARCHAR, data type stores strings of varying length.

``n`` specifies the maximum length of the VARCHAR data type as the length of the column when you create a table. ``n`` specifies the length to be between 1 and 15 000.

Example usage of ``VARCHAR(n)``::
 
 >>> cursor.execute("create table varchar_table (c1 NVARCHAR(128), c1 NVARCHAR(256)")
 >>> cursor.execute("insert into varchar_table values (:a, :b)", ("Hey", "my string")))

NCHAR(n) 
----------------
The NATIONAL CHARACTER (NCHAR) data type stores string values of fixed length in a column. ``n`` specifies the specify length of the NATIONAL CHARACTER data type as the length of the column when you create a table. ``n`` can be any value between 1 and 5 000.

When Mimer SQL stores values in a column defined as NATIONAL CHARACTER, it right-pads the values with spaces to conform with the specified column length.

Example usage of ``NVARCHAR``::

 >>> cursor.execute("create table nchar_table(c1 nchar(5), c2 nchar(12))")
 >>> cursor.execute("insert into nchar_table values (:a,:b)", "nchar table"))

NVARCHAR(n) 
----------------
The NATIONAL CHARACTER VARYING, abbreviated NVARCHAR, NATIONAL CHAR VARYING or NCHAR VARYING, data type stores strings of varying length.

``n`` specifies the maximum length of the NATIONAL CHARACTER VARYING data type as the length of the column when you create a table. You can specify the length to be between 1 and 5 000.

Example usage of ``NVARCHAR(n)``::

 >>> cursor.execute("create table nvarchar_table (c1 NVARCHAR(128), c1 NVARCHAR(256)")
 >>> cursor.execute("insert into nvarchar_table values (:a, :b)", ("Hey", "my string"))

DATE 
----------
DATE describes a date using the fields YEAR, MONTH and DAY in the format YYYY-MM-DD. It represents an absolute position on the timeline.

Example usage of ``DATE``::

 >>> cursor.execute("create table datetable (c1 DATE)")
 >>> data = "2020-09-24"
 >>> cursor.execute("insert INTO datetable VALUES (?)", (data))

TIME(s) 
---------------
TIME(s) describes a time in an unspecified day, with seconds precision s, using the fields HOUR, MINUTE and SECOND in the format HH:MM:SS[.sF] where F is the fractional part of the SECOND value. It represents an absolute time of day.

Example usage of ``TIME``::

 >>> cursor.execute("create table timetable (c1 TIME(0))")
 >>> time = "16:04:55"
 >>> cursor.execute("insert INTO timetable VALUES (?)", (time))

TIMESTAMP(s) 
---------------------
TIMESTAMP(s) describes both a date and time, with seconds precision s, using the fields YEAR, MONTH, DAY, HOUR, MINUTE and SECOND in the format YYYY-MM-DD HH:MM:SS[.sF]. F is the fractional part of the SECOND value. It represents an absolute position on the timeline.

Example usage of ``TIMESTAMP``::

 >>> cursor.execute("create table timestamp_table(c1 TIMESTAMP(2))")
 >>> cursor.execute("insert into timestamp_table values (:a)", ('2020-09-17 11:21:51.12'))

Universally Unique Identifier (UUID)
------------------------------------------
Universally Unique Identifier is currently not implemented. 

INTERVAL 
------------
An INTERVAL is a period of time, such as: 3 years, 90 days or 5 minutes and 45 seconds. The table below show all available interval types.

+-------------------------------+---------------+
| Mimer SQL Data type           | Range         |
|                               |               |
+===============================+===============+
| INTERVAL YEAR(p)              | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL YEAR(p) to MONTH     | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL MONTH(p)             | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL DAY(p)               | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL DAY(p) to HOUR       | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL DAY(p) to MINUTE     | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL DAY(p) to SECOND     | 1 <= p <= 7   |
+-------------------------------+---------------+
| INTERVAL HOUR(p)              | 1 <= p <= 8   |
+-------------------------------+---------------+
| INTERVAL HOUR(p) to MINUTE    | 1 <= p <= 8   |
+-------------------------------+---------------+
| INTERVAL HOUR(p) to SECOND    | 1 <= p <= 8   |
+-------------------------------+---------------+
| INTERVAL MINUTE(p)            | 1 <= p <= 10  |
+-------------------------------+---------------+
| INTERVAL MINUTE(p) to SECOND  | 1 <= p <= 10  |
+-------------------------------+---------------+
| INTERVAL SECOND(p)            | 1 <= p <= 12  |
+-------------------------------+---------------+
| INTERVAL SECOND(p,s)          | 0 <= s <= 9   |
+-------------------------------+---------------+

Consider the following example::

  >>> cursor.execute("create table intervaltable (c1 YEAR(5), c2 INTERVAL YEAR(5) TO MONTH)")
  >>> cursor.execute("insert into intervaltable values (?)", ("2021", "2021-05"))

NULL 
------------
The Python data type ``None`` is mapped to ``NULL`` in
MimerPy. Mimer SQL ``NULL`` values will be returned as ``None`` in
Python. Consider the following example::

  >>> cursor.execute("create table booltable(c1 INTEGER)")
  >>> cursor.execute("insert into booltable values (NULL)")
  >>> cursor.execute("insert into booltable values (?)", (None))

In the database both values will be stored as ``NULL``. When selected,
they are both shown as ``None`` in Python.
