import csv
import sqlite3

with open("data.csv") as dataFile:
    reader = csv.DictReader(dataFile)

    #connect to db
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    for row in reader:
        # write to db
        cur.execute("INSERT INTO stocks (ticker, exchange, type, currency) VALUES(?, ?, ?, ?)", (row['ticker'], row['exchange'], row['assetType'], row['priceCurrency']))

    con.commit()
    con.close