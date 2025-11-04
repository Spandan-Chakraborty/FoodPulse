import sqlite3

# Establish a connection to the database file
connection = sqlite3.connect('database.db')

# Open and read the schema file
with open('schema.sql') as f:
    connection.executescript(f.read())

print("Database initialized successfully.")

connection.close()