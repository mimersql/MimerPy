***************
Release Notes
***************

.. _sec-release-notes:

Mimerpy Version 1.0.5
----------------------------
Mimerpy version 1.0.5 is the first public version of Mimerpy. This means that
everything is new. We have aimed to implement everything from the `PEP 249`_ and
this has been done for all of the obligatory content of the interface.
There are currently some extensions that are not yet implemented. There are also
some limitations and missing MimerSQL data types.


.. _PEP 249: https://www.python.org/dev/peps/pep-0249/

.. What's new
.. ------------------------
.. With current version being the first.

Project status
------------------------
Development Stages:

*   3 - Alpha

*   4 - Beta

*   5 - Production/Stable


Mimerpy current development state is 3, Alpha.


Future
------------------------

The future is looking bright.
There are a few things we would like to implement in the future, and a few bug fixes that are to come.
Some of them are:

* Being able to mix DDL and DML statments in one transaction.

* Be able to rollback DDL statments.

* Implement the methods :meth:`setinputsizes` and :meth:`setoutputsize` for cursor.
* Implement custom data types, adapters.

* Implement all the MimerSQL data types.

* Raise warnings from the Mimer Micro C API.
