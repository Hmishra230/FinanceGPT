import pandas as pd
import sqlite3
from cryptography.fernet import Fernet
import os

# Key management to ensure consistency with the main application
def load_key():
    if not os.path.exists('secret.key'):
        raise FileNotFoundError("Encryption key 'secret.key' not found. Please run the main app or init_db.py first.")
    with open('secret.key', 'rb') as key_file:
        key = key_file.read()
    return key

def load_transactions():
    key = load_key()
    cipher = Fernet(key)

    if not os.path.exists('transactions.csv'):
        print("Error: transactions.csv not found.")
        return

    df = pd.read_csv('transactions.csv')
    conn = sqlite3.connect('financegpt.db')
    c = conn.cursor()

    # Clear existing transactions for the user to avoid duplicates
    c.execute("DELETE FROM transactions WHERE user_id = ?", ('user1',))
    print("Cleared existing transactions for user1.")

    for _, row in df.iterrows():
        encrypted_description = cipher.encrypt(row['description'].encode()).decode()
        c.execute("INSERT INTO transactions (user_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
                  (row['user_id'], row['date'], encrypted_description, row['amount'], row['category']))

    conn.commit()
    conn.close()
    print(f"{len(df)} transactions loaded successfully for user1 from transactions.csv")

if __name__ == '__main__':
    try:
        load_transactions()
    except Exception as e:
        print(f"An error occurred: {e}")
