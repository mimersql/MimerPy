from setuptools import setup
from distutils.core import Extension
import platform

plat = platform.system()
bits = platform.architecture()[0][0:2]

incDirs = []
libDirs = []
libs = ['mimerapi']

if plat == 'Linux':
    pass
elif plat == 'Darwin':
    incDirs = ['/usr/local/include']
    libDirs = ['/usr/local/lib']
elif plat == 'Windows':
    libs = ['mimapi' + bits]
else:
    raise Exception('Unsupported platform: ' + plat)

sources = ["src/mimerapi.c"]

extensions = [
    Extension('mimerapi',
              include_dirs = incDirs,
              library_dirs = libDirs,
              libraries = libs,
              sources = sources),
    ]

with open("README.rst", "r") as f:
    long_description = f.read()

setup (
    name='mimerpy',
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
    python_requires='>=3.5',
    #install_requires=['Mimer>=11.0']
    )
