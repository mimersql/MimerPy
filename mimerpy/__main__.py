import mimerpy
import argparse
import re

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
                        help="Display MimerPy version number",
                        action="store_true")
    parser.add_argument("-t", "--tag",
                        help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("sql", default=None, nargs='?',
                        help="A SQL command to execute")
    args = parser.parse_args()

    something = False

    if args.tag:
        something = True
        tags = re.findall(r'^\d+\.\d+\.\d+$', mimerpy.__version__)
        if len(tags):
            print(tags[0])
        else:
            print("No-clean-tag")

    if args.version:
        something = True
        print("Mimerpy version %s" % mimerpy.__version__)

    if args.sql:
        something = True
        try:
            with mimerpy.connect(dsn = args.database,
                                 user = args.user,
                                 password = args.password,
                                 autocommit = True) as con:
                with con.cursor() as cur:
                    cur.execute(args.sql)
                    if cur.description is not None:
                        r = cur.fetchall()
                        print(r)
        except Exception as e:
            print(e)

    if not something:
        print("Use option -h to get help")
