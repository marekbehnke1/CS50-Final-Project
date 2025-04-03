import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

#return query
res = cur.execute("SELECT * FROM users WHERE userid = 1").fetchall()

print(res[0])