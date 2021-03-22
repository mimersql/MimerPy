***************
Release Notes
***************

.. _sec-release-notes:

MimerPy Version 1.0
-------------------
MimerPy version 1.0 is the first public version.

Known problems:

* DDL and DML statments can not be mixed in one transaction.
  DDL statements are always committed

* DDL statments in a transaction can not be rolled back.

* The methods :meth:`setinputsizes` and :meth:`setoutputsize` are not
  implemented for cursors.
