from flask import Flask, request, jsonify, render_template
from cryptography.fernet import Fernet
import sqlite3
import pandas as pd
import logging
import os
import pickle
from categorization import train_model, categorize as categorize_ml
from insights import calculate_health_score, generate_insights

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Key management
def load_or_generate_key():
    if os.path.exists('secret.key'):
        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
    return key

key = load_or_generate_key()
cipher = Fernet(key)

# Database setup
def get_db_connection():
    conn = sqlite3.connect('financegpt.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

def init_db():
    conn = get_db_connection()
    # Create users table first due to foreign key constraint
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT PRIMARY KEY, 
                  email TEXT UNIQUE NOT NULL, 
                  encrypted_key TEXT NOT NULL)''')

    # Create transactions table
    conn.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id TEXT, 
                  date TEXT, 
                  description TEXT, 
                  amount REAL, 
                  category TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        user_id = request.form.get('user_id', 'user1') # Default user_id for simplicity
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            # Validate and clean data
            if not all(col in df.columns for col in ['date', 'description', 'amount']):
                return jsonify({'error': 'Missing required columns in CSV file'}), 400
            df = df.dropna(subset=['date', 'description', 'amount'])

            # Categorize transactions
            categorized_df = categorize_ml(df)
            df['category'] = categorized_df['category']
            
            conn = get_db_connection()
            for _, row in df.iterrows():
                encrypted_description = cipher.encrypt(row['description'].encode()).decode()
                conn.execute("INSERT INTO transactions (user_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
                         (user_id, row['date'], encrypted_description, row['amount'], row['category']))
            conn.commit()
            conn.close()
            return jsonify({'message': 'File processed and transactions categorized successfully'}), 200
        return jsonify({'error': 'Unsupported file format'}), 400
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/dashboard/<user_id>', methods=['GET'])
def get_dashboard(user_id):
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT date, description, amount, category FROM transactions WHERE user_id = ?", (user_id,)).fetchall()
        conn.close()
        transactions = []
        for row in rows:
            decrypted_description = cipher.decrypt(row['description'].encode()).decode()
            transactions.append({'date': row['date'], 'description': decrypted_description, 'amount': row['amount'], 'category': row['category']})
        return jsonify({'transactions': transactions}), 200
    except Exception as e:
        logger.error(f"Error fetching dashboard data for user {user_id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/categorize', methods=['POST'])
def categorize_transactions():
    try:
        data = request.get_json()
        if not data or 'transactions' not in data:
            return jsonify({'error': 'Invalid request body'}), 400

        transactions = data['transactions']
        df = pd.DataFrame(transactions)

        if 'description' not in df.columns:
            return jsonify({'error': 'Missing description in transactions'}), 400

        categorized_df = categorize_ml(df)
        return jsonify(categorized_df.to_dict(orient='records')), 200
    except Exception as e:
        logger.error(f"Error categorizing transactions: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/insights/<user_id>', methods=['GET'])
def get_insights(user_id):
    try:
        insights = generate_insights(user_id)
        return jsonify({'insights': insights}), 200
    except Exception as e:
        logger.error(f"Error generating insights for user {user_id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/budget', methods=['POST'])
def budget_recommendations():
    # Placeholder for budget recommendations
    return jsonify({'message': 'Budget recommendations not implemented yet'}), 501

@app.route('/api/health-score/<user_id>', methods=['GET'])
def get_financial_health_score(user_id):
    try:
        score = calculate_health_score(user_id)
        return jsonify({'health_score': score}), 200
    except Exception as e:
        logger.error(f"Error calculating health score for user {user_id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

with app.app_context():
    init_db()
    if not os.path.exists('model.pkl'):
        train_model()

@app.route('/add_expense')
def add_expense_page():
    return render_template('add_expense.html')

@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user1')
        date = data.get('date')
        description = data.get('description')
        amount = data.get('amount')
        category = data.get('category')

        if not all([date, description, amount, category]):
            return jsonify({'error': 'Missing required fields'}), 400

        encrypted_description = cipher.encrypt(description.encode()).decode()
        
        conn = get_db_connection()
        conn.execute("INSERT INTO transactions (user_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
                     (user_id, date, encrypted_description, amount, category))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Transaction added successfully'}), 201
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
