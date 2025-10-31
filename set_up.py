import sqlite3

conn = sqlite3.connect("adoption.db")
c = conn.cursor()

# Pets table
c.execute('''CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    breed TEXT,
    image TEXT,
    status TEXT DEFAULT 'Available'
)''')

# Requests table
c.execute('''CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER,
    user_name TEXT,
    user_email TEXT,
    status TEXT DEFAULT 'Pending'
)''')

conn.commit()
conn.close()
print("Database setup completed ✅")
