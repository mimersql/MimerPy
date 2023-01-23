******************
Installation guide
******************

The following section covers how to install MimerPy.

Requirements
------------------------

MimerPy can currently run with Python3.5 or later, keep in mind
to use the correct versions if you have multiple versions installed.

If you are running on Ubuntu or Linux, some Python header files are needed for the installation. To install all the
required files use the command:

.. code-block:: console

    $ sudo apt-get install python3-dev

Alternatively you can download the Python-dev package in any preferable way.

.. note:: The error “Python.h: No such file or directory”, is solved by downloading the -dev package.

You need to install the Mimer SQL C API and have a Mimer SQL database server of version 11 or newer.

.. note:: The error “mimerapi.h: No such file or directory”, is caused by Mimer SQL not being installed or a Mimer SQL version older than 11.

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

    $ python3 setup.py build
    $ python3 setup.py install

If you wish to install the built distribution, you can download it from `PyPI`_ and then use pip to install:

.. code-block:: console

  $ python3 -m pip install mimerpy-current.version.tar.gz

.. _GitHub: https://github.com/mimersql/MimerPy
.. _PyPI: https://pypi.org/
.. _Mimer SQL C API: https://developer.mimer.com/article/mimer-sql-c-api/
.. _Mimer SQL developer site: https://developer.mimer.com
