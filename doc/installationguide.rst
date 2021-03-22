******************
Installation guide
******************

The following section covers how to install MimerPy on your device.

.. _sec-SQL-api:

Mimer SQL C API
------------------------

MimerPy requires the `Mimer SQL C API`_. This is a discrete C API that
is included with Mimer.  To access the SQL C API, Mimer has to be
installed on your device. It can be downloaded and installed from the
`Mimer developer site`_.

.. note:: MimerPy is only compatible with Mimer 11.0 or newer.

Installing from PyPI
------------------------

MimerPy can be found at PyPI_.

First make sure your pip is up to date, then download the mimerpy
package using the command:

.. code-block:: console

    $ pip3 install --upgrade pip   # Making sure pip is up to date
    $ pip3 install mimerpy

Make sure pip installed MimerPy for Python3 and not Python2. If you
have both Python2 and Python3 installed on your system you can use the
command:

.. code-block:: console

    $ pip3 install mimerpy

.. _PyPI: https://pypi.python.org/pypi

Installing from source
------------------------

MimerPy’s source can be found on GitHub_.

To build MimerPy's source use the command:

.. code-block:: console

    $ python3 setup.py build
    $ python3 setup.py install

If you wish to install the built distribution, you can download it from `PyPI`_ and then use pip to install:

.. code-block:: console

  $ pip3 install mimerpy-current.version.tar.gz

.. _GitHub: https://github.com/mimersql/MimerPy
.. _PyPI: https://pypi.python.org/pypi
.. _Mimer SQL C API: https://developer.mimer.com/mimerapi

Requirements
------------------------

MimerPy can currently only run with Python3.5 or later, keep in mind
to use the correct versions if you have multiple versions installed.

Some Python header files are needed for the installation. To install all the
required files use the command:

.. code-block:: console

    $ sudo apt-get install python3-dev

Alternatively you can download the Python-dev package in any preferable way.

.. note:: The error “Python.h: No such file or directory”, is solved by downloading the -dev package.

The Mimer SQL C API is required.

.. note:: The error “mimerapi.h: No such file or directory”, is caused by Mimer not being installed or a Mimer version older than 11.

.. _Mimer developer site: https://developer.mimer.com
