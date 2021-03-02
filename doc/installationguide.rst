******************
Installation guide
******************

The following section covers how to install Mimerpy on your device.

.. note:: Currently Mimerpy installation is only possible for Unix systems.

.. _sec-micro-api:

Mimer Micro C API
------------------------

Mimerpy requires the `Mimer Micro C API`_. This is a discrete C API that is included with Mimer.
To access the Micro C API, Mimer has to be installed on your device and can be downloaded and installed
at the `Mimer developer site`_.

.. note:: Mimerpy is only compatible with Mimer 11.0 or newer.

Installing from PyPI
------------------------

Mimerpy can be found at PyPI_ and is currently only available for Unix systems.

First make sure your pip is up to date, then download the mimerpy package using the command:

.. code-block:: console

    $ pip3 install --upgrade pip   # Making sure pip is up to date
    $ pip3 install mimerpy

Make sure pip installed Mimerpy for Python3 and not Python2. If you have both Python2 and Python3
installed on your system you can use the command:

.. code-block:: console

    $ pip3 install mimerpy

.. _PyPI: https://pypi.python.org/pypi

Installing from source
------------------------

Mimerpy’s source can be found on the `Mimer developer site`_.

To build Mimerpy's source use the command:

.. code-block:: console

    $ python3 setup.py build
    $ python3 setup.py install

If you wish to install the built distribution, you can download it from `PyPI`_ and then use pip to install:

.. code-block:: console

  $ pip3 install mimerpy-current.version.tar.gz

.. _PyPI: https://pypi.python.org/pypi
.. _Mimer Micro C API: http://developer.mimer.se/documentation/html_101/Mimer_SQL_Engine_DocSet/microapi.html

Requirements
------------------------

Mimerpy can currently only run with Python3, keep in mind to use the correct
versions if you have multiple versions installed.

Some Python header files are needed for the installation. To install all the
required files use the command:

.. code-block:: console

    $ sudo apt-get install python3-dev

Alternatively you can download the Python-dev package in any preferable way.

.. note:: The error “Python.h: No such file or directory”, is solved by downloading the -dev package.

The Mimer Micro C API is required. More installation help can be found at the
:ref:`Mimer Micro C API` documentation.

.. note:: The error “mimermicroapi.h: No such file or directory”, is caused by Mimer not being installed or a Mimer version older than 11.

.. _Mimer developer site: http://developer.mimer.com


Still have problems?
--------------------------
Mimerpy is still in Alpha, if you are experiencing any difficulties with the
product itself, its installation, usage or documentation please contact us.
All feedback is appreciated to help us at Mimer Information Technology to
improve our product. Contact us at: emailadress.
