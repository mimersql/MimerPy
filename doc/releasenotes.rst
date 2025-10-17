***************
Release Notes
***************

.. _sec-release-notes:

MimerPy Version 1.1
-------------------
MimerPy version 1.1 is the first public version.

Known problems:

* DDL and DML statments can not be mixed in one transaction.
  DDL statements are always committed

* DDL statements in a transaction can not be rolled back.

* The methods :meth:`setinputsizes` and :meth:`setoutputsize` are not
  implemented for cursors.

* Accessing values with the type builtin.uuid in Mimer SQL requires a
  MimerAPI of version 11.0.5B or later.

* Accessing values with the type FLOAT(p) in Mimer SQL requires a
  MimerAPI of version 11.0.5B or later.

* Accessing integer values larger than 2**63 with the type INTEGER(p)
  in Mimer SQL requires a MimerAPI of version 11.0.5B or later.

* Using method :meth:`callproc` to call a Stored Procedure is not yet
  supported.


MimerPy Version 1.3.0
---------------------
MimerPy version 1.3.0 is a major release that uses `ctypes` and dynamic bindings
to the Mimer SQL C API.

Major changes:

* MimerPy is now implemented using `ctypes` to access the Mimer SQL C API.
  This removes the need for a C compiler on all platforms.
* MimerPy now requires Python 3.6 or later.

MimerPy Version 1.3.1
---------------------
MimerPy version 1.3.1 adds support for UUID and GIS datatypes in Mimer SQL.

Major changes:
* Support for the UUID datatype BUILTIN.UUID added.
* Support for GIS datatypes added. This include BUILTIN.GIS_LOCATION, BUILTIN.GIS_LATITUDE,
  and BUILTIN.GIS_LONGITUDE. This requires Mimer SQL version 11.0.8E or later.

