import sqlite3

connection = sqlite3.connect('datas.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
follows = ["sport", "jeux", "informatique", "photographie", "theatre", "dessin", "débat", "cinéma"]
for title in follows:
    cur.execute('INSERT INTO follow (name, usedFor) VALUES (?, ?)',
                     (title, "BLOG"))
connection.commit()
connection.close()