******************
Installation guide
******************

The following section covers how to install MimerPy.

Requirements
------------------------

MimerPy can currently run with Python3.6 or later, keep in mind
to use the correct versions if you have multiple versions installed.

You need to install the Mimer SQL C API and have a Mimer SQL database server of version 11 or newer.

.. _sec-SQL-api:

Mimer SQL C API
------------------------

MimerPy requires the `Mimer SQL C API`_. This is a discrete C API that
is included with Mimer SQL.  To access the SQL C API, Mimer SQL has to be
installed. It can be downloaded and installed from the
`Mimer SQL developer site`_.

.. note:: MimerPy is only compatible with Mimer SQL 11.0 or newer.

Installing with pip
------------------------

MimerPy can be found at PyPI_, and installed using pip. 

First make sure your pip is up to date, then download the mimerpy
package using the command:

.. code-block:: console

    $ python3 -m pip install --upgrade pip   # Making sure pip is up to date
    $ python3 -m pip install mimerpy

Make sure pip installed MimerPy for Python3 and not Python2.

.. _PyPI: https://pypi.org/

Installing from source
------------------------

MimerPy’s source can be found on GitHub_.

To build MimerPy's source use the command:

.. code-block:: console

    $ python3 -m build
    $ python3 -m pip install -e .

If you wish to install the release distribution manually, you can download it from `PyPI`_ and then use pip to install:

To use the source distribution, use the command:

.. code-block:: console

  $ python3 -m pip install mimerpy-<version>.tar.gz

You can also use the pre-built wheel file using the command:

.. code-block:: console

  $ python3 -m pip install mimerpy-<version>-py3-none-any.whl



.. _GitHub: https://github.com/mimersql/MimerPy
.. _PyPI: https://pypi.org/
.. _Mimer SQL C API: https://developer.mimer.com/article/mimer-sql-c-api/
.. _Mimer SQL developer site: https://developer.mimer.com
