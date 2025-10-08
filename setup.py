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
# LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# See license for more details.
#
# This setup.py is now optional — it only exists to handle
# platform-specific logic for locating Mimer API headers and libraries.

import platform, os, sys, subprocess, ast, re

# --- Choose between setuptools and distutils depending on platform plattform ---
if platform.system() == 'OpenVMS':
    from distutils.core import setup, Extension
else:
    from setuptools import setup, Extension

# --- Detect OpenVMS and warn about build isolation ---
if platform.system() == "OpenVMS":
    import importlib.util
    missing = []
    for pkg in ("setuptools", "wheel"):
        if importlib.util.find_spec(pkg) is None:
            missing.append(pkg)
    if missing:
        print(
            f"\nWARNING: On OpenVMS, build isolation does not work reliably.\n"
            f"The following packages must be preinstalled globally: {', '.join(missing)}\n"
            f"Please run:\n"
            f"    python -m pip install {' '.join(missing)}\n"
            f"and then reinstall using:\n"
            f"    python -m pip install --no-build-isolation mimerpy\n"
        )
        sys.exit(1)
    else:
        print(
            "\nNOTE: Running on OpenVMS — build isolation will not be used.\n"
            "Make sure 'setuptools' and 'wheel' are installed globally.\n"
            "Install using:\n"
            "    python -m pip install --no-build-isolation mimerpy\n"
        )
        
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
        brew_prefix = None
        try:
            brew_prefix = subprocess.check_output(["brew", "--prefix"], text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            pass
        if brew_prefix:
            incDirs = [os.path.join(brew_prefix, "include")]
            libDirs = [os.path.join(brew_prefix, "lib")]
        else:
            incDirs = ['/usr/local/include', '/opt/homebrew/include']
            libDirs = ['/usr/local/lib', '/opt/homebrew/lib']
        if machine in ("arm64", "aarch64"):
            extraLinkArgs = ["-arch", "arm64"]
        elif machine in ("x86_64",):
            extraLinkArgs = ["-arch", "x86_64"]

    elif plat == 'Windows':
        libs = ['mimapi' + bits]
        from winreg import HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY
        from winreg import ConnectRegistry, OpenKeyEx, QueryValueEx, CloseKey, EnumKey
        root = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        mimer_key = OpenKeyEx(root, r"SOFTWARE\\Mimer\\Mimer SQL", 0, KEY_READ | KEY_WOW64_64KEY)
        index = 0
        version_key = None
        while True:
            try:
                key = EnumKey(mimer_key, index)
                if key not in ("License", "SQLHosts"):
                    version_key = key
                    break
                index += 1
            except OSError:
                break
        if not version_key:
            raise RuntimeError("Could not find installed Mimer SQL version in registry.")
        inner_key = OpenKeyEx(mimer_key, version_key)
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


# --- Read version from _version.py ---
fallback_version = "1.2.1"
version = fallback_version
try:
    version_ns = {}
    with open("src/mimerpy/_version.py") as f:
        exec(f.read(), version_ns)
    version = version_ns.get("__version__", fallback_version)
except FileNotFoundError:
    pass


def format_people(lst):
    if isinstance(lst, list):
        return ", ".join([p.get("name", "") for p in lst if isinstance(p, dict)])
    return lst


def format_list(lst):
    if isinstance(lst, list):
        return lst
    return [lst]


plat = platform.system()

if plat == "OpenVMS":
    # Classic setuptools/distutils, ingen PEP-517
    # --- Read metadata from pyproject.toml ---
    metadata = {}
    pyproject_file = "pyproject.toml"
    if os.path.exists(pyproject_file):
        with open(pyproject_file) as f:
            content = f.read()
        project_block = re.search(r"\[project\](.*?)\n\[", content, re.DOTALL)
        if project_block is None:
            project_block = re.search(r"\[project\](.*)", content, re.DOTALL)
        if project_block:
            block = project_block.group(1)
            lines = [l.strip() for l in block.splitlines() if l.strip() and not l.strip().startswith("#")]
            for line in lines:
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    try:
                        val_parsed = ast.literal_eval(val)
                    except Exception:
                        val_parsed = val.strip('"').strip("'")
                    metadata[key] = val_parsed

    setup(
        name="mimerpy",
        version=version,
        description=metadata.get("description", ""),
        long_description=open(metadata.get("readme", "README.rst")).read() if metadata.get("readme") else "",
        long_description_content_type="text/x-rst",
        author=format_people(metadata.get("authors", [])),
        maintainer=format_people(metadata.get("maintainers", [])),
        license=metadata.get("license", "MIT"),
        classifiers=format_list(metadata.get("classifiers", [])),
        keywords=" ".join(format_list(metadata.get("keywords", []))),
        ext_modules=build_extensions(),
    )

else:
    # Modern setup on other platforms, generate _version.py via setuptools_scm
    setup(
        name="mimerpy",
        use_scm_version={
            "write_to": "src/mimerpy/_version.py",
            "version_scheme": "guess-next-dev",
            "local_scheme": "node-and-date",
        },
        ext_modules=build_extensions(),
    )

# Comment:
# On modern platforms, setuptools_scm is used to automatically generate _version.py
# based on the latest Git tag. This ensures that the version is always correct,
# even when building from CI or an sdist, without needing to manually remove _version.py.
# On OpenVMS, classic distutils with a static version is used instead, for maximum compatibility.
