import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

#uname = 'test'

db = sqlite3.connect("database.db")
cur = db.cursor()

#print(cur.execute("SELECT * FROM users WHERE username = ?", (uname,)).fetchone()[1])
#db.close()
uname = "new_testing"
fname = "test"
lname = ""
email = "test@test.com"
password = "password"
password_check = "password"


new_user = {
    "username" : uname,
    "fname": fname,
    "lname" : lname,
    "email" : email,
    "password": generate_password_hash(password)
}

#for row in new_user:
    
for key, value in new_user.items():
    if not value:
        print("no " + key)

