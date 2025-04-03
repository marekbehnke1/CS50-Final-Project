import sqlite3

uname = 'test'
db = sqlite3.connect("database.db")
cur = db.cursor()

print(cur.execute("SELECT userid FROM users WHERE username = ?", (uname,)).fetchone()[0])
db.close()