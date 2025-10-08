# Copyright (c) 2017 Mimer Information Technology

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# See license for more details.
#
# This setup.py is now optional — it only exists to handle
# platform-specific logic for locating Mimer API headers and libraries.

from setuptools import setup, Extension
import platform, os, sys, subprocess

def build_extensions():
    plat = platform.system()
    bits = platform.architecture()[0][0:2]
    machine = platform.machine().lower()

    incDirs = []
    libDirs = []
    libs = ['mimerapi']
    extraLinkArgs = []

    if plat == 'Linux':
        pass

    elif plat == 'Darwin':
        # Detect Homebrew prefix for both Intel and ARM macOS
        brew_prefix = None
        try:
            brew_prefix = subprocess.check_output(
                ["brew", "--prefix"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            pass

        if brew_prefix:
            incDirs = [os.path.join(brew_prefix, "include")]
            libDirs = [os.path.join(brew_prefix, "lib")]
        else:
            # fallback to default macOS locations
            incDirs = ['/usr/local/include', '/opt/homebrew/include']
            libDirs = ['/usr/local/lib', '/opt/homebrew/lib']

        # macOS ARM64 specific tweaks (Apple Silicon)
        if machine in ("arm64", "aarch64"):
            extraLinkArgs = ["-arch", "arm64"]
        elif machine in ("x86_64",):
            extraLinkArgs = ["-arch", "x86_64"]

    elif plat == 'Windows':
        libs = ['mimapi' + bits]
        from winreg import (
            HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY,
            ConnectRegistry, OpenKeyEx, QueryValueEx, CloseKey, EnumKey
        )
        root = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        mimer_key = OpenKeyEx(root, r"SOFTWARE\\Mimer\\Mimer SQL", 0, KEY_READ | KEY_WOW64_64KEY)
        index = 0
        version = None
        while True:
            try:
                key = EnumKey(mimer_key, index)
                if key not in ("License", "SQLHosts"):
                    version = key
                    break
                index += 1
            except OSError:
                break
        if not version:
            raise RuntimeError("Could not find installed Mimer SQL version in registry.")

        inner_key = OpenKeyEx(mimer_key, version)
        path = QueryValueEx(inner_key, 'PathName')[0]
        CloseKey(inner_key)
        CloseKey(root)

        if bits == '64':
            libDirs = [os.path.join(path, 'dev', 'lib', 'amd64')]
        elif bits == '32':
            libDirs = [os.path.join(path, 'dev', 'lib', 'x86')]
        else:
            raise Exception(f'Unsupported Windows version: {bits}')

        incDirs.append(os.path.join(path, 'dev', 'include'))

    elif plat == 'OpenVMS':
        incDirs = ['MIMER$LIB']
        libs = []
        extraLinkArgs = [',MIMER$LIB:MIMER$API64/OPT'] if bits == '64' else [',MIMER$LIB:MIMER$API/OPT']

    else:
        raise Exception(f'Unsupported platform: {plat}')

    return [Extension(
        'mimerapi',
        include_dirs=incDirs,
        library_dirs=libDirs,
        libraries=libs,
        extra_link_args=extraLinkArgs,
        sources=["src/mimerpy/mimerapi.c"]
    )]

if __name__ == "__main__":
    setup(
        name="mimerpy",
        use_scm_version=True,
        ext_modules=build_extensions(),
    )