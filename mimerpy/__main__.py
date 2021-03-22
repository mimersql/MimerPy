import mimerpy
import mimerapi
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = "mimerpy", description="""
A simple command line program for the MimerPy library. It can
display the version number of the MimerPy library (-v switch) or
connect to a Mimer database server and execute a singe SQL
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
        print("MimerPy  version %s" % mimerpy.__version__)
        print("MimerAPI version %s" % mimerapi.__version__)

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
