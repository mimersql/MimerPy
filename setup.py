from setuptools import setup, Extension
from distutils.core import Extension
import platform, os

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
    from winreg import HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY, ConnectRegistry, OpenKeyEx, QueryValueEx, CloseKey, EnumKey, OpenKeyEx
    root = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    mimer_key = OpenKeyEx(root, r"SOFTWARE\Mimer\Mimer SQL", 0,  KEY_READ | KEY_WOW64_64KEY)
    index = 0
    while True:
        try:
            key = EnumKey(mimer_key,index)
            if key != "License" and key != "SQLHosts":
                version = key
                break
            index = index + 1
        except OSError:
            break
    inner_key = OpenKeyEx(mimer_key, version)
    path = QueryValueEx(inner_key, 'PathName')[0]
    CloseKey(inner_key)
    CloseKey(root)
    if bits == '64':
        libDirs = [path + 'dev\\lib\\amd64']
    elif bits == '32': 
        libDirs = [path + 'dev\\lib\\x86']
    else: 
        raise Exception('Unsupported windows version, have to be 32 or 64 bits: ' + bits)
    incDirs.append(path + 'dev\\include')
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

setup (
    name='mimerpy',
    use_scm_version = True,
    setup_requires = ['setuptools_scm'],
    url='https://developer.mimer.com/mimerpy',
    description='Python database interface for Mimer SQL',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='Mimer MimerSQL Database SQL PEP249',
    ext_modules = extensions,
    packages=['mimerpy'],
    package_dir={'mimerpy': 'mimerpy', 'mimerpy.tests': 'tests'},
    python_requires='>=3.5',
    #install_requires=['Mimer>=11.0']
    )
