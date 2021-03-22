***************
Release Notes
***************

.. _sec-release-notes:

Mimerpy Version 1.0
-------------------
Mimerpy version 1.0 is the first public version of Mimerpy.

Known problems:
* DDL and DML statments can not be mixed in one transaction.
  DDL statements are always committed

* DDL statments in a transaction can not be rolled back.

* The methods :meth:`setinputsizes` and :meth:`setoutputsize` are not
  implemented for cursors.
