import sqlite3

uname = 'test'
db = sqlite3.connect("database.db")
cur = db.cursor()

print(cur.execute("SELECT * FROM users WHERE username = ?", (uname,)).fetchone()[1])
db.close()