from setuptools import setup
from distutils.core import Extension
import platform

plat = platform.system()

incDirs = []
libDirs = []
libs = ['mimerapi']

if plat == 'Linux':
    pass
elif plat == 'Darwin':
    incDirs = ['/usr/local/include']
    libDirs = ['/usr/local/lib']
elif plat == 'Windows':
    libs = ['mimapi64']
else:
    raise Exception('Unsupported platform: ' + plat)

sources = ["src/mimerapi.c"]

extensions = [
    Extension('mimerapi',
              include_dirs = incDirs,
              library_dirs = libDirs,
              libraries = ['mimerapi'],
              sources = sources),
    ]

long_description = """
MimerPy - Python database interface for MimerSQL
=================================================
MimerPy is an adapter for `Mimer SQL`_ in Python which implements the
[PEP-0249]_ database interface.  It allows the user to access the powerful
tools and advantages of Mimer SQL through Python.  MimerPy is implemented as
a Cpython wrapper of the native MimerAPI interface.  A successfull install
requires that Mimer V11 is installed.
.. _[PEP-0249] https://www.python.org/dev/peps/pep-0249/
.. _`Mimer SQL` https://www.mimer.com
"""

setup (
    name='mimerpy',
#    version='1.0.11',
    use_scm_version = True,
    setup_requires = ['setuptools_scm'],
    url='https://www.mimer.com',
    description='Python database interface for Mimer SQL',
    long_description=long_description,
    #long_description_content_type="text/markdown",
    #download_url='www.developer.mimer.com/python/download',
    author='Erik Gunne & Magdalena Bostrom',
    author_email='erik.gunne@mimer.com',
    maintainer = 'Mimer Information Technology AB',
    maintainer_email = 'mimerpy@mimer.com',
    license='MIT',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='Mimer MimerSQL Database SQL PEP249',
    ext_modules = extensions,
    packages=['mimerpy'],
    package_dir={'mimerpy': 'mimerpy', 'mimerpy.tests': 'tests'},
    python_requires='>=3.6',
    #install_requires=['Mimer>=11.0']
    )
