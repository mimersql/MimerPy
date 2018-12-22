import mimerpy

import db_config

if __name__ == '__main__':
    with mimerpy.connect(**db_config.SYSUSR) as syscon:
        with syscon.cursor() as c:
            c.execute("drop ident mimerpy cascade")
        syscon.commit()
