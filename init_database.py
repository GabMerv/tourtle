# encoding=utf8
import sqlite3

connection = sqlite3.connect('datas.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
follows = ["Sport-⚽", "Jeux-🎲", "Informatique-💻", "Photographie-📷", "Theatre-🎭", "Dessin-🖌️", "Debat-🗣️", "Cinema-🎥", "Musique-🎼"]
for title in follows:
    cur.execute('INSERT INTO follow (name, usedFor) VALUES (?, ?)',
                     (title, "BLOG"))
connection.commit()
connection.close()