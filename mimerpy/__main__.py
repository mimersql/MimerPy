import mimerpy
import argparse
import re

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple connectivity test")
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
                        help="Display MimerPy tag number in short form",
                        action="store_true")
    parser.add_argument("sql", default=None, nargs='?',
                        help="A SQL command to execute")
    args = parser.parse_args()

    something = False

    if args.tag:
        something = True
        tags = re.findall(r'\d+\.\d+\.\d+', mimerpy.__version__)
        if len(tags):
            print(tags[0])
        else:
            print("No tag found")

    if args.version:
        something = True
        print("Mimerpy version %s" % mimerpy.__version__)

    if args.sql:
        something = True
        print("SQL: %s" % args.sql)

    if not something:
        print("Use option -h to get help")
