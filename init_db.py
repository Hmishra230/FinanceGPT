import sqlite3
from cryptography.fernet import Fernet
import os

# Key management - ensures the same key is used as in the main app
def load_or_generate_key():
    if os.path.exists('secret.key'):
        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
    return key

def init_database():
    key = load_or_generate_key()
    cipher = Fernet(key)
    
    conn = sqlite3.connect('financegpt.db')
    c = conn.cursor()
    
    # Drop existing tables for a clean setup (optional, use with caution)
    c.execute('DROP TABLE IF EXISTS transactions')
    c.execute('DROP TABLE IF EXISTS users')

    # Create transactions table with a primary key
    c.execute('''CREATE TABLE transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id TEXT, 
                  date TEXT, 
                  description TEXT, 
                  amount REAL, 
                  category TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    # Create users table
    c.execute('''CREATE TABLE users 
                 (user_id TEXT PRIMARY KEY, 
                  email TEXT UNIQUE NOT NULL, 
                  encrypted_key TEXT NOT NULL)''')
    
    # Insert a sample user
    # In a real app, the user's key would be derived from their password
    user_specific_key = Fernet.generate_key() # Example key for the user
    encrypted_user_key = cipher.encrypt(user_specific_key).decode()
    
    try:
        c.execute("INSERT INTO users (user_id, email, encrypted_key) VALUES (?, ?, ?)",
                  ('user1', 'user@example.com', encrypted_user_key))
        print("Sample user 'user1' created.")
    except sqlite3.IntegrityError:
        print("User 'user1' already exists.")

    conn.commit()
    conn.close()
    print("Database initialized successfully with 'users' and 'transactions' tables.")

if __name__ == '__main__':
    # This will delete existing data. Use with caution.
    print("WARNING: This script will reset the database.")
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() == 'y':
        init_database()
    else:
        print("Database initialization cancelled.")
