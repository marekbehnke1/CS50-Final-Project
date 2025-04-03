import sqlite3

con = sqlite3.connect("database.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

#return query
res = cur.execute("SELECT * FROM users WHERE userid = 1").fetchall()[0]

print(res["fname"])