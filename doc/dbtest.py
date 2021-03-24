import mimerPy

# Creating a connection
con = mimerPy.connect(dsn ="testDB11", user="SYSADM", password="SYSADM")

# Creating a cursor
cur = con.cursor()

# Creating a databank
cur.execute("create databank bankoftest")

# Createing a table
cur.execute("create table test_table(c1 NVARCHAR(128)) in bankoftest")

# Instering a string
cur.execute("insert into test_table values ('Using mimerPy is easy!')")

# Selecting the inserted string
cur.execute("select * from test_table")

# Fetching the data from the result set
fetchValue = cur.fetchone()

# Closing the cursor
cur.close()

# Committing the changes
con.commit()

# Closing the connection
con.close()

print(fetchValue[0])