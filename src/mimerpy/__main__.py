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

import mimerpy
from mimerpy import mimerapi
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = "mimerpy", description="""
A simple command line program for the MimerPy library. It can
display the version number of the MimerPy library (-v switch) or
connect to a Mimer SQL database server and execute a singe SQL
statement (provide database, user, and password arguments and a
SQL statement).
""")
    parser.add_argument("-d", "--database",
                        help="Database to connect to")
    parser.add_argument("-u", "--user",
                        help="User name to use in connection")
    parser.add_argument("-p", "--password",
                        help="Password for the user")
    parser.add_argument("-v", "--version",
                        help="Display MimerPy and MimerAPI version numbers",
                        action="store_true")
    parser.add_argument("-t", "--tag",
                        help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--trace",
                        help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("sql", default=None, nargs='?',
                        help="A SQL command to execute")
    args = parser.parse_args()

    something = False

    if args.tag:
        something = True
        print(mimerpy.version)

    if args.version:
        something = True
        print("MimerPy   version %s" % mimerpy.__version__)
        print("Mimer API version %s" % mimerapi.__version__)

    if args.sql:
        something = True
        try:
            if args.trace:
                mimerpy._trace()
            with mimerpy.connect(dsn = args.database,
                                 user = args.user,
                                 password = args.password,
                                 autocommit = True) as con:
                with con.cursor() as cur:
                    cur.execute(args.sql)
                    if cur.description is not None:
                        for r in cur:
                            print(r)
        except Exception as e:
            print(e)

    if not something:
        print("Use option -h to get help")
