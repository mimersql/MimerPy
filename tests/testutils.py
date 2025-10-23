
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
Test utilities for MimerPy.
"""

import sys

# On Python < 3.7, fromisoformat() doesn't exist.
# Use dateutil.parser.isoparse instead (installed automatically via pyproject.toml).
if sys.version_info < (3, 7):
    from dateutil.parser import isoparse

    def tolerant_fromiso_datetime(val: str) -> datetime:
        """Parse ISO datetime on Python <3.7 using dateutil."""
        return isoparse(val)

    def tolerant_fromiso_time(val: str) -> time:
        """Parse ISO time on Python <3.7 using dateutil, extract timetz()."""
        return isoparse(val).timetz()

else:
    from datetime import datetime, time
    def tolerant_fromiso_datetime(val: str) -> datetime:
        """Parse ISO datetime tolerant across Python 3.7 - 3.13."""
        s = val.strip()

        # Fast path — succeeds on modern Python for most strings
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            pass

        # Normalize only when needed
        if ' ' in s and 'T' not in s:
            s = s.replace(' ', 'T', 1)

        dot = s.find('.')
        if dot != -1:
            end = dot + 1
            while end < len(s) and s[end].isdigit():
                end += 1
            frac = s[dot + 1:end]
            if len(frac) > 6:
                frac = frac[:6]
            elif 0 < len(frac) < 6:
                frac = frac.ljust(6, '0')
            s = s[:dot + 1] + frac + s[end:]

        return datetime.fromisoformat(s)


    def tolerant_fromiso_time(val: str) -> time:
        """Parse ISO time tolerant across Python 3.7 - 3.13."""
        s = val.strip()

        # Fast path first
        try:
            return time.fromisoformat(s)
        except ValueError:
            pass

        # Normalize fractional part when needed
        dot = s.find('.')
        if dot != -1:
            end = dot + 1
            while end < len(s) and s[end].isdigit():
                end += 1
            frac = s[dot + 1:end]
            if len(frac) > 6:
                frac = frac[:6]
            elif 0 < len(frac) < 6:
                frac = frac.ljust(6, '0')
            s = s[:dot + 1] + frac + s[end:]

        return time.fromisoformat(s)
