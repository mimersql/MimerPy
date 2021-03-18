import mimerpy
from mimerpy.mimPyExceptions import DatabaseError, TransactionAbortError

def important_transaction(con):
    try: 
        cursor = con.cursor()
        cursor.execute("CREATE TABLE poff (c1 INTEGER, c2 FLOAT) in pybank")
        cursor.execute("INSERT into poff values (:a, :b)", (5, 5.5))
        con.commit()
    except TransactionAbortError as e:
        con.rollback()
        return 0
    except DatabaseError as e:
        con.rollback()
        print("Unexpected non-database error:", e)
        return -1
    return 1

if __name__ == "__main__":
    con = mimerpy.connect(dsn="pymeme", user = "SYSADM", password = "SYSADM")
    laps = 0
    while laps < 10:
        result = important_transaction(con)
        if result == 1:
            break
        laps = laps + 1

    if result == 1: 
        print("Succsess!")
    else:
        print("Failure!")