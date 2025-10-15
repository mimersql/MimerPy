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
"""
mimerapi.py — pure-Python ctypes wrapper for Mimer SQL C API.

Notes:
- Safe mimerGetError8 (null-guard) to avoid segfaults on ended/invalid handles.
- Keep Python buffers alive until EndStatement, or upon explicit reuse in BeginStatement8.
- Idempotent/null-safe EndStatement / CloseCursor.
- Range checks for int32/int64
- Safe memory lifecycle for LOB and string data via _keep_buffer() to avoid premature garbage collection.
"""

from __future__ import annotations

import platform
import os
import struct
import ctypes
from ctypes import (
    c_int16, c_int32, c_int64, c_size_t, c_char_p, c_void_p, c_double, c_float,
    POINTER, byref, create_string_buffer
)
from ctypes.util import find_library

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIMERPY_DATA_CONVERSION_ERROR = -25020
MIMERPY_NOMEM = -25030

# SQL type codes (adjust if your mimerapi.h defines different values)
MIMER_TYPE_VARCHAR   = 12
MIMER_TYPE_CHAR      = 1
MIMER_TYPE_NCHAR     = -15
MIMER_TYPE_NVARCHAR  = -9
MIMER_TYPE_LONGVAR   = -1
MIMER_TYPE_NLONGVAR  = -16
MIMER_TYPE_BINARY    = -2
MIMER_TYPE_VARBINARY = -3
MIMER_TYPE_LONGVARBINARY = -4
MIMER_TYPE_UUID      = 1111  # vendor-specific placeholder if needed

BUFLEN = 1024
CHUNK_SIZE = 100000

__version__ = ""
_version_tuple = (0, 0, 0, 'A')
_level = 0

# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
def _load_mimer():
    """Locate and load the native Mimer API library for the current platform."""
    plat = platform.system()
    bits = struct.calcsize("P") * 8  # 32 or 64

    # Allow override via env var
    env_path = os.getenv("MIMERAPI_PATH")
    if env_path and os.path.exists(env_path):
        return ctypes.CDLL(env_path)

    # Platform-specific setup
    if plat == "Windows":
        from os import add_dll_directory
        from winreg import (
            HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY,
            ConnectRegistry, OpenKeyEx, QueryValueEx, CloseKey, EnumKey
        )

        mimapilib = f"mimapi{bits}.dll"

        # Locate the Mimer SQL installation path
        try:
            root = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            mimer_key = OpenKeyEx(root, r"SOFTWARE\Mimer\Mimer SQL", 0, KEY_READ | KEY_WOW64_64KEY)
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

            if version:
                inner_key = OpenKeyEx(mimer_key, version)
                path = QueryValueEx(inner_key, "PathName")[0]
                CloseKey(inner_key)
                CloseKey(root)
                add_dll_directory(path)
        except Exception:
            pass

    elif plat == "Darwin":
        mimapilib = "/usr/local/lib/libmimerapi.dylib"

    elif plat == "Linux":
        mimapilib = "libmimerapi.so"

    elif plat == "OpenVMS":
        mimapilib = "MIMER$API"

    else:
        raise ImportError(f"Unsupported platform: {plat}")

    # Try to load
    try:
        return ctypes.CDLL(mimapilib)
    except OSError as e:
        raise ImportError(
            f"Could not load Mimer API for {plat} ({bits}-bit); "
            f"tried {mimapilib}; last error: {e}"
        )


_lib = _load_mimer()

# ---------------------------------------------------------------------------
# ctypes handle types
# ---------------------------------------------------------------------------

MimerSession = c_void_p
MimerStatement = c_void_p
MimerLob = c_void_p
MimerHandle = c_void_p

# ---------------------------------------------------------------------------
# Bind helper
# ---------------------------------------------------------------------------

def _bind(name, restype, *argtypes):
    try:
        fn = getattr(_lib, name)
    except AttributeError:
        raise ImportError(f"Symbol {name} not found in {_lib._name}")
    fn.restype = restype
    fn.argtypes = list(argtypes)
    return fn

# ---------------------------------------------------------------------------
# Native symbols
# ---------------------------------------------------------------------------

_MimerAPIVersion            = _bind('MimerAPIVersion', c_char_p)
_MimerBeginSession8         = _bind('MimerBeginSession8', c_int32, c_char_p, c_char_p, c_char_p, POINTER(MimerSession))
_MimerEndSession            = _bind('MimerEndSession', c_int32, POINTER(MimerSession))
_MimerBeginTransaction      = _bind('MimerBeginTransaction', c_int32, MimerSession, c_int32)
_MimerEndTransaction        = _bind('MimerEndTransaction', c_int32, MimerSession, c_int32)
_MimerBeginStatement8       = _bind('MimerBeginStatement8', c_int32, MimerSession, c_char_p, c_int32, POINTER(MimerStatement))
_MimerEndStatement          = _bind('MimerEndStatement', c_int32, POINTER(MimerStatement))
_MimerOpenCursor            = _bind('MimerOpenCursor', c_int32, MimerStatement)
_MimerCloseCursor           = _bind('MimerCloseCursor', c_int32, MimerStatement)
_MimerAddBatch              = _bind('MimerAddBatch', c_int32, MimerStatement)
_MimerExecuteStatement8     = _bind('MimerExecuteStatement8', c_int32, MimerSession, c_char_p)
_MimerExecute               = _bind('MimerExecute', c_int32, MimerStatement)
_MimerParameterCount        = _bind('MimerParameterCount', c_int32, MimerStatement)
_MimerParameterName8        = _bind('MimerParameterName8', c_int32, MimerStatement, c_int16, c_char_p, c_size_t)
_MimerParameterType         = _bind('MimerParameterType', c_int32, MimerStatement, c_int16)
_MimerColumnCount           = _bind('MimerColumnCount', c_int32, MimerStatement)
_MimerColumnType            = _bind('MimerColumnType', c_int32, MimerStatement, c_int16)
_MimerColumnName8           = _bind('MimerColumnName8', c_int32, MimerStatement, c_int16, c_char_p, c_size_t)
_MimerFetch                 = _bind('MimerFetch', c_int32, MimerStatement)
_MimerGetInt32              = _bind('MimerGetInt32', c_int32, MimerStatement, c_int16, POINTER(c_int32))
_MimerGetInt64              = _bind('MimerGetInt64', c_int32, MimerStatement, c_int16, POINTER(c_int64))
_MimerGetString8            = _bind('MimerGetString8', c_int32, MimerStatement, c_int16, c_char_p, c_size_t)
_MimerGetDouble             = _bind('MimerGetDouble', c_int32, MimerStatement, c_int16, POINTER(c_double))
_MimerGetFloat              = _bind('MimerGetFloat', c_int32, MimerStatement, c_int16, POINTER(c_float))
_MimerSetInt32              = _bind('MimerSetInt32', c_int32, MimerStatement, c_int16, c_int32)
_MimerSetInt64              = _bind('MimerSetInt64', c_int32, MimerStatement, c_int16, c_int64)
_MimerSetString8            = _bind('MimerSetString8', c_int32, MimerStatement, c_int16, c_char_p)
_MimerSetDouble             = _bind('MimerSetDouble', c_int32, MimerStatement, c_int16, c_double)
_MimerSetFloat              = _bind('MimerSetFloat', c_int32, MimerStatement, c_int16, c_float)
_MimerGetError8             = _bind('MimerGetError8', c_int32, MimerHandle, POINTER(c_int32), c_char_p, c_size_t)
_MimerIsNull                = _bind('MimerIsNull', c_int32, MimerStatement, c_int16)
_MimerSetNull               = _bind('MimerSetNull', c_int32, MimerStatement, c_int16)

_MimerSetLob                = _bind('MimerSetLob', c_int32, MimerStatement, c_int16, c_size_t, POINTER(MimerLob))
_MimerGetLob                = _bind('MimerGetLob', c_int32, MimerStatement, c_int16, POINTER(c_size_t), POINTER(MimerLob))
_MimerSetBlobData           = _bind('MimerSetBlobData', c_int32, POINTER(MimerLob), c_void_p, c_size_t)
_MimerGetBlobData           = _bind('MimerGetBlobData', c_int32, POINTER(MimerLob), c_void_p, c_size_t)
_MimerSetNclobData8         = _bind('MimerSetNclobData8', c_int32, POINTER(MimerLob), c_char_p, c_size_t)
_MimerGetNclobData8         = _bind('MimerGetNclobData8', c_int32, POINTER(MimerLob), c_char_p, c_size_t)

_MimerSetBinary             = _bind('MimerSetBinary', c_int32, MimerStatement, c_int16, c_void_p, c_size_t)
_MimerGetBinary             = _bind('MimerGetBinary', c_int32, MimerStatement, c_int16, c_void_p, c_size_t)
_MimerSetBoolean            = _bind('MimerSetBoolean', c_int32, MimerStatement, c_int16, c_int32)
_MimerGetBoolean            = _bind('MimerGetBoolean', c_int32, MimerStatement, c_int16)
_MimerGetUUID               = _bind('MimerGetUUID', c_int32, MimerStatement, c_int16, c_void_p)
_MimerSetUUID               = _bind('MimerSetUUID', c_int32, MimerStatement, c_int16, c_void_p)

# ---------------------------------------------------------------------------
# Minimal tracking (buffers + pending bind errors)
# ---------------------------------------------------------------------------
# These helper maps keep Python-owned memory alive while Mimer SQL may still reference it.
# Without this, Python’s garbage collector could free strings or LOB chunks still used by C code.
_active_buffers: dict[int, list[object]] = {}
_stmt_bind_error: dict[int, int] = {}  # surfaced by AddBatch/Execute

def _keep_buffer(statement_ptr: int, buf: object) -> None:
    """
    Keep a reference to a Python buffer (e.g. ctypes string or memoryview)
    that has been passed to the Mimer C API for parameter binding.

    This prevents Python's garbage collector from freeing the memory
    while the Mimer statement is still active, since the native library
    may continue reading from that buffer until the statement is executed
    or ended (MimerEndStatement or MimerClearBuffers).

    Buffers are released explicitly in _release_buffers().
    """
    if not statement_ptr:
        return
    sp = int(statement_ptr)
    _active_buffers.setdefault(sp, []).append(buf)

def _release_buffers(statement_ptr: int) -> None:
    """Release any Python-side buffers and pending errors for the given statement."""
    sp = int(statement_ptr)
    if sp in _active_buffers:
        n = len(_active_buffers[sp])
        had_err = _stmt_bind_error.pop(sp, None) is not None
    _active_buffers.pop(sp, None)
    _stmt_bind_error.pop(sp, None)

def mimerClearBuffers(statement_ptr: int) -> None:
    _release_buffers(int(statement_ptr))

def _set_stmt_error(statement_ptr: int, err: int) -> None:
    sp = int(statement_ptr)
    if sp and err and err < 0 and sp not in _stmt_bind_error:
        _stmt_bind_error[sp] = int(err)

def _arg_i16(v: int) -> c_int16:
    return c_int16(int(v))

def _int64_overflow(x: int) -> bool:
    return x < -(1 << 63) or x > (1 << 63) - 1

def _int32_overflow(x: int) -> bool:
    return x < -(1 << 31) or x > (1 << 31) - 1

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_utf8_cstring_keep(stmt: int, raw: bytes) -> c_char_p:
    if not raw.endswith(b"\x00"):
        raw = raw + b"\x00"
    buf = create_string_buffer(raw)
    _keep_buffer(stmt, buf)
    return ctypes.cast(buf, c_char_p)

# ---------------------------------------------------------------------------
# API wrappers
# ---------------------------------------------------------------------------

def mimerAPIVersion() -> str:
    try:
        s = _MimerAPIVersion()
        return s.decode('ascii', 'ignore') if s else ''
    except Exception as e:
        return ''

def mimerBeginSession8(db_name: str, user: str, password: str):
    sess = MimerSession()
    rc = _MimerBeginSession8(
        db_name.encode('utf-8'),
        user.encode('utf-8'),
        password.encode('utf-8'),
        byref(sess)
    )
    return (sess.value or 0, int(rc))

def mimerEndSession(session_ptr: int):
    sess = MimerSession(session_ptr)
    return int(_MimerEndSession(byref(sess)))

def mimerBeginTransaction(session_ptr: int):
    return int(_MimerBeginTransaction(MimerSession(session_ptr), 0))

def mimerEndTransaction(session_ptr: int, commit_rollback: int):
    return int(_MimerEndTransaction(MimerSession(session_ptr), int(commit_rollback)))

def mimerBeginStatement8(session_ptr: int, sql: str, opt: int):
    st = MimerStatement()
    rc = _MimerBeginStatement8(MimerSession(session_ptr), sql.encode('utf-8'), int(opt), byref(st))
    sp = int(st.value or 0)
    if sp:
        # If a previous buffers list exists for this handle (address reuse), release old buffers now.
        if sp in _active_buffers:
            _release_buffers(sp)
    return (int(rc), sp)

def mimerEndStatement(statement_ptr: int):
    sp = int(statement_ptr or 0)
    if sp == 0:
        return 0
    st = MimerStatement(sp)
    try:
        rc = int(_MimerEndStatement(byref(st)))
    except Exception as ex:
        rc = 0
    # Release buffers on EndStatement (simple, matches original usage)
    _release_buffers(sp)
    return int(rc or 0)

def mimerOpenCursor(statement_ptr: int):
    return int(_MimerOpenCursor(MimerStatement(statement_ptr)))

def mimerCloseCursor(statement_ptr: int):
    sp = int(statement_ptr or 0)
    if sp == 0:
        return 0
    try:
        rc = int(_MimerCloseCursor(MimerStatement(sp)))
    except Exception as ex:
        rc = 0
    return int(rc or 0)

def mimerAddBatch(statement_ptr: int):
    sp = int(statement_ptr)
    perr = _stmt_bind_error.pop(sp, None)
    if perr is not None:
        return int(perr)
    rc = _MimerAddBatch(MimerStatement(sp))
    return int(rc)

def mimerExecuteStatement8(session_ptr: int, sql: str):
    return int(_MimerExecuteStatement8(MimerSession(session_ptr), sql.encode('utf-8')))

def mimerExecute(statement_ptr: int):
    sp = int(statement_ptr)
    perr = _stmt_bind_error.pop(sp, None)
    if perr is not None:
        return int(perr)
    rc = _MimerExecute(MimerStatement(sp))
    return int(rc)

def mimerParameterCount(statement_ptr: int):
    return int(_MimerParameterCount(MimerStatement(statement_ptr)))

def _get_text_varying(getter, handle_ptr: int, ordinal: int):
    if _MimerIsNull(MimerStatement(handle_ptr), _arg_i16(ordinal)) == 1:
        return (0, None)
    buf = create_string_buffer(BUFLEN)
    rc = getter(MimerStatement(handle_ptr), _arg_i16(ordinal), buf, c_size_t(BUFLEN))
    if rc >= BUFLEN:
        needed = int(rc) + 1
        try:
            big = create_string_buffer(needed)
        except Exception:
            return (MIMERPY_NOMEM, '')
        rc = getter(MimerStatement(handle_ptr), _arg_i16(ordinal), big, c_size_t(needed))
        s = (big.raw[:max(0, int(rc))]).decode('utf-8', 'strict') if rc > 0 else ''
        return (int(rc), s)
    else:
        s = (buf.raw[:max(0, int(rc))]).decode('utf-8', 'strict') if rc > 0 else ''
        return (int(rc), s)

def mimerParameterName8(statement_ptr: int, parameter_number: int):
    rc, s = _get_text_varying(_MimerParameterName8, statement_ptr, parameter_number)
    return (rc, s)

def mimerParameterType(statement_ptr: int, parameter_number: int):
    return int(_MimerParameterType(MimerStatement(statement_ptr), _arg_i16(parameter_number)))

def mimerColumnCount(statement_ptr: int):
    return int(_MimerColumnCount(MimerStatement(statement_ptr)))

def mimerColumnType(statement_ptr: int, column_number: int):
    return int(_MimerColumnType(MimerStatement(statement_ptr), _arg_i16(column_number)))

def mimerColumnName8(statement_ptr: int, column_number: int):
    rc, s = _get_text_varying(_MimerColumnName8, statement_ptr, column_number)
    return (rc, s)

def mimerFetch(statement_ptr: int):
    return int(_MimerFetch(MimerStatement(statement_ptr)))

def mimerGetInt32(statement_ptr: int, column_number: int):
    if _MimerIsNull(MimerStatement(statement_ptr), _arg_i16(column_number)) == 1:
        return (0, None)
    out = c_int32()
    rc = _MimerGetInt32(MimerStatement(statement_ptr), _arg_i16(column_number), byref(out))
    return (int(rc), int(out.value))

def mimerGetInt64(statement_ptr: int, column_number: int):
    if _MimerIsNull(MimerStatement(statement_ptr), _arg_i16(column_number)) == 1:
        return (0, None)
    out = c_int64()
    rc = _MimerGetInt64(MimerStatement(statement_ptr), _arg_i16(column_number), byref(out))
    return (int(rc), int(out.value))

def mimerGetString8(statement_ptr: int, column_number: int):
    return _get_text_varying(_MimerGetString8, statement_ptr, column_number)

def mimerGetDouble(statement_ptr: int, column_number: int):
    if _MimerIsNull(MimerStatement(statement_ptr), _arg_i16(column_number)) == 1:
        return (0, None)
    out = c_double()
    rc = _MimerGetDouble(MimerStatement(statement_ptr), _arg_i16(column_number), byref(out))
    return (int(rc), float(out.value))

def mimerGetFloat(statement_ptr: int, column_number: int):
    if _MimerIsNull(MimerStatement(statement_ptr), _arg_i16(column_number)) == 1:
        return (0, None)
    out = c_float()
    rc = _MimerGetFloat(MimerStatement(statement_ptr), _arg_i16(column_number), byref(out))
    return (int(rc), float(out.value))

def mimerSetInt32(statement_ptr: int, parameter_number: int, value):
    sp = int(statement_ptr)
    if value is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if isinstance(value, bool):
        iv = int(value)
    elif isinstance(value, int):
        iv = value
    else:
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    if _int32_overflow(iv):
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    rc = _MimerSetInt32(MimerStatement(sp), _arg_i16(parameter_number), c_int32(iv))
    return int(rc)

def mimerSetInt64(statement_ptr: int, parameter_number: int, value):
    sp = int(statement_ptr)
    if value is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if isinstance(value, bool):
        iv = int(value)
    elif isinstance(value, int):
        iv = value
    else:
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    if _int64_overflow(iv):
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    rc = _MimerSetInt64(MimerStatement(sp), _arg_i16(parameter_number), c_int64(iv))
    return int(rc)

def mimerSetString8(statement_ptr: int, parameter_number: int, val: str):
    sp = int(statement_ptr)
    if val is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    try:
        raw = val.encode('utf-8')
    except Exception:
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    buf = create_string_buffer(raw + b'\x00')
    _keep_buffer(sp, buf)
    return int(_MimerSetString8(MimerStatement(sp), _arg_i16(parameter_number),
                                ctypes.cast(buf, c_char_p)))


def mimerSetDouble(statement_ptr: int, parameter_number: int, value):
    sp = int(statement_ptr)
    if value is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if isinstance(value, int) and _int64_overflow(value):
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    try:
        dv = float(value)
    except Exception:
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    return int(_MimerSetDouble(MimerStatement(sp), _arg_i16(parameter_number), c_double(dv)))

def mimerSetFloat(statement_ptr: int, parameter_number: int, value):
    sp = int(statement_ptr)
    if value is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if isinstance(value, int) and _int64_overflow(value):
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    try:
        fv = float(value)
    except Exception:
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    return int(_MimerSetFloat(MimerStatement(sp), _arg_i16(parameter_number), c_float(fv)))

def mimerGetError8(handle_ptr: int):
    """Simple safe wrapper for MimerGetError8 — avoids segfault on null/invalid handle."""
    sp = int(handle_ptr or 0)
    if sp == 0:
        return (0, 0, "")
    try:
        evalue = c_int32(0)
        ELEN = 128
        buf = create_string_buffer(ELEN)
        rc = _MimerGetError8(MimerHandle(sp), byref(evalue), buf, c_size_t(ELEN))
        if rc >= 0:
            if rc > ELEN:
                rc = ELEN
            msg = buf.raw[:int(rc)].decode('utf-8', 'ignore')
            rc = 0
        else:
            msg = ''
        return (int(rc), int(evalue.value), msg)
    except Exception as ex:
        return (0, 0, "")

def mimerSetBlobData(statement_ptr: int, parameter_number: int, data):
    sp = int(statement_ptr)
    if data is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if not isinstance(data, (bytes, bytearray, memoryview)):
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    mv_all = memoryview(data)
    length = len(mv_all)
    lob = MimerLob()
    rc = _MimerSetLob(MimerStatement(sp), _arg_i16(parameter_number), c_size_t(length), byref(lob))
    if rc < 0:
        return int(rc)
    offset = 0
    rc_local = 0
    max_chunk = 9_900_000
    while rc_local == 0 and offset < length:
        part_mv = mv_all[offset: offset + max_chunk]
        buf = (ctypes.c_ubyte * len(part_mv)).from_buffer_copy(part_mv)
        _keep_buffer(sp, buf)
        rc_local = _MimerSetBlobData(byref(lob), ctypes.cast(buf, c_void_p), c_size_t(len(part_mv)))
        offset += len(part_mv)
    return int(rc_local)

def mimerSetNclobData8(statement_ptr: int, parameter_number: int, text: str | None):
    sp = int(statement_ptr)
    if text is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    raw = text.encode('utf-8')
    lob = MimerLob()
    rc = _MimerSetLob(MimerStatement(sp), _arg_i16(parameter_number), c_size_t(len(raw)), byref(lob))
    if rc < 0:
        return int(rc)
    cptr = _set_utf8_cstring_keep(sp, raw)
    return int(_MimerSetNclobData8(byref(lob), cptr, c_size_t(len(raw))))

def mimerGetBlobData(statement_ptr: int, parameter_number: int):
    sp = int(statement_ptr)
    if _MimerIsNull(MimerStatement(sp), _arg_i16(parameter_number)) == 1:
        return (0, None)
    lob = MimerLob()
    length = c_size_t(0)
    rc = _MimerGetLob(MimerStatement(sp), _arg_i16(parameter_number), byref(length), byref(lob))
    if rc < 0:
        return (int(rc), None)
    total = int(length.value)
    try:
        buf = bytearray(total)
    except Exception:
        return (MIMERPY_NOMEM, None)
    got = 0
    rc_local = 0
    while got < total:
        part = min(CHUNK_SIZE, total - got)
        Arr = ctypes.c_ubyte * part
        chunk = Arr.from_buffer(buf, got)
        rc_local = _MimerGetBlobData(byref(lob), ctypes.cast(chunk, c_void_p), c_size_t(part))
        if rc_local < 0:
            return (int(rc_local), None)
        got += part
    return (int(rc_local), bytes(buf))

def mimerGetNclobData8(statement_ptr: int, parameter_number: int):
    sp = int(statement_ptr)
    if _MimerIsNull(MimerStatement(sp), _arg_i16(parameter_number)) == 1:
        return (0, None)
    lob = MimerLob()
    length = c_size_t(0)
    rc = _MimerGetLob(MimerStatement(sp), _arg_i16(parameter_number), byref(length), byref(lob))
    if rc < 0:
        return (int(rc), None)
    need = 4 * int(length.value) + 1
    try:
        buf = create_string_buffer(need)
    except Exception:
        return (MIMERPY_NOMEM, None)
    rc = _MimerGetNclobData8(byref(lob), buf, c_size_t(need))
    s = buf.value.decode('utf-8', 'strict') if rc >= 0 else ''
    return (int(rc), s)

def mimerSetBinary(statement_ptr: int, parameter_number: int, value):
    sp = int(statement_ptr)
    if value is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if not isinstance(value, (bytes, bytearray, memoryview)):
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    mv = memoryview(value)
    buf = (ctypes.c_ubyte * len(mv)).from_buffer_copy(mv)
    _keep_buffer(sp, buf)
    return int(_MimerSetBinary(MimerStatement(sp), _arg_i16(parameter_number),
                               ctypes.cast(buf, c_void_p), c_size_t(len(mv))))

def mimerGetBinary(statement_ptr: int, parameter_number: int):
    sp = int(statement_ptr)
    if _MimerIsNull(MimerStatement(sp), _arg_i16(parameter_number)) == 1:
        return (0, None)
    SmallArr = ctypes.c_ubyte * BUFLEN
    small = SmallArr()
    rc = _MimerGetBinary(MimerStatement(sp), _arg_i16(parameter_number), small, c_size_t(BUFLEN))
    if rc > BUFLEN:
        need = int(rc)
        try:
            BigArr = ctypes.c_ubyte * need
            big = BigArr()
        except Exception:
            return (MIMERPY_NOMEM, None)
        rc = _MimerGetBinary(MimerStatement(sp), _arg_i16(parameter_number), big, c_size_t(need))
        if rc <= 0:
            return (int(rc), None)
        return (int(rc), bytes(bytearray(big))[:int(rc)])
    else:
        if rc <= 0:
            return (int(rc), None)
        return (int(rc), bytes(bytearray(small))[:int(rc)])

def mimerSetBoolean(statement_ptr: int, parameter_number: int, value):
    sp = int(statement_ptr)
    if value is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    v = 1 if bool(value) else 0
    return int(_MimerSetBoolean(MimerStatement(sp), _arg_i16(parameter_number), c_int32(v)))

def mimerGetBoolean(statement_ptr: int, parameter_number: int):
    sp = int(statement_ptr)
    if _MimerIsNull(MimerStatement(sp), _arg_i16(parameter_number)) == 1:
        return (0, None)
    rc = _MimerGetBoolean(MimerStatement(sp), _arg_i16(parameter_number))
    return (int(rc), int(rc))

def mimerGetUUID(statement_ptr: int, parameter_number: int):
    sp = int(statement_ptr)
    if _MimerIsNull(MimerStatement(sp), _arg_i16(parameter_number)) == 1:
        return (0, None)
    buf = (ctypes.c_ubyte * 16)()
    rc = _MimerGetUUID(MimerStatement(sp), _arg_i16(parameter_number), ctypes.cast(buf, c_void_p))
    if rc < 0:
        return (int(rc), None)
    return (int(rc), bytes(bytearray(buf)))

def mimerSetUUID(statement_ptr: int, parameter_number: int, uuid_bytes: bytes):
    sp = int(statement_ptr)
    if uuid_bytes is None:
        return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))
    if not isinstance(uuid_bytes, (bytes, bytearray, memoryview)) or len(uuid_bytes) != 16:
        _set_stmt_error(sp, MIMERPY_DATA_CONVERSION_ERROR)
        return int(MIMERPY_DATA_CONVERSION_ERROR)
    mv = memoryview(uuid_bytes)
    buf = (ctypes.c_ubyte * 16).from_buffer_copy(mv[:16])
    _keep_buffer(sp, buf)
    return int(_MimerSetUUID(MimerStatement(sp), _arg_i16(parameter_number), ctypes.cast(buf, c_void_p)))

def mimerSetNull(statement_ptr: int, parameter_number: int, _ignored=None):
    sp = int(statement_ptr)
    return int(_MimerSetNull(MimerStatement(sp), _arg_i16(parameter_number)))

def mimerTestMalloc(v: int):
    # No-op in ctypes version; kept for API parity.
    return 0

__all__ = [
    'mimerAPIVersion', 'mimerGetError8',
    'mimerBeginSession8', 'mimerEndSession',
    'mimerBeginTransaction', 'mimerEndTransaction',
    'mimerBeginStatement8', 'mimerEndStatement',
    'mimerOpenCursor', 'mimerCloseCursor',
    'mimerExecuteStatement8', 'mimerExecute',
    'mimerAddBatch',
    'mimerParameterCount', 'mimerParameterName8', 'mimerParameterType',
    'mimerColumnCount', 'mimerColumnType', 'mimerColumnName8',
    'mimerFetch',
    'mimerGetInt32', 'mimerGetInt64', 'mimerGetString8', 'mimerGetDouble', 'mimerGetFloat',
    'mimerGetBinary', 'mimerGetBoolean', 'mimerGetUUID',
    'mimerGetBlobData', 'mimerGetNclobData8',
    'mimerSetInt32', 'mimerSetInt64', 'mimerSetString8', 'mimerSetDouble', 'mimerSetFloat',
    'mimerSetBinary', 'mimerSetBoolean', 'mimerSetUUID',
    'mimerSetBlobData', 'mimerSetNclobData8', 'mimerSetNull',
    'mimerClearBuffers',
    '__version__', '_version_tuple', '_level'
]
