import sqlite3

#create and connect to database
# connects to db in current directory - creating it if it does not exist
db_con = sqlite3.connect("database.db")

# creates a cursor
db_cur = db_con.cursor()

username = "test4"
fname = "test4"
lname = "test4"
email = "test@test.com"
balance = 10000

user = (
    {"fname": fname,
    "lname": lname,
    "email": email,
    "balance": balance,}
)


# insert opens a transaction - this needs to be commited before changes are saved to the database
db_cur.execute("INSERT INTO users (username, fname, lname, email, balance) VALUES(?, ?, ?, ?, ?)", (username, fname, lname, email, balance))
#commit changes on the connection object
db_con.commit()

db_res = db_cur.execute("SELECT * FROM users")

print(db_res.fetchall())