import pandas as pd
import sqlite3
from cryptography.fernet import Fernet
import os

# Key management to decrypt data
def load_key():
    if not os.path.exists('secret.key'):
        raise FileNotFoundError("Encryption key 'secret.key' not found. Please run the main app first.")
    with open('secret.key', 'rb') as key_file:
        key = key_file.read()
    return key

key = load_key()
cipher = Fernet(key)

def get_transactions_df(user_id):
    conn = sqlite3.connect('financegpt.db')
    try:
        df = pd.read_sql_query("SELECT description, amount, category FROM transactions WHERE user_id = ?", conn, params=(user_id,))
    finally:
        conn.close()

    if df.empty:
        return pd.DataFrame(columns=['description', 'amount', 'category'])

    # Decrypt descriptions - This is for consistency, though not directly used in these calculations
    df['description'] = df['description'].apply(lambda x: cipher.decrypt(x.encode()).decode())
    return df

def calculate_health_score(user_id):
    df = get_transactions_df(user_id)
    if df.empty:
        return 0

    # More robust scoring logic
    income = df[df['category'] == 'Income']['amount'].sum()
    total_spending = df[df['category'] != 'Income']['amount'].sum()
    
    # 1. Savings Rate (50% weight)
    savings = income - total_spending
    savings_rate = (savings / income * 100) if income > 0 else 0
    savings_score = max(0, min(100, savings_rate * 5)) # Score based on savings rate, capped at 100

    # 2. Spending Consistency (30% weight)
    spending_std = df[df['category'] != 'Income']['amount'].std()
    consistency_score = max(0, 100 - (spending_std / 5)) # Lower standard deviation is better

    # 3. Category Diversification (20% weight)
    num_categories = df['category'].nunique()
    diversification_score = min(100, num_categories * 10) # More categories is a sign of diverse spending

    # Weighted average score
    health_score = int(savings_score * 0.5 + consistency_score * 0.3 + diversification_score * 0.2)
    return max(0, min(100, health_score))

def generate_insights(user_id):
    df = get_transactions_df(user_id)
    if df.empty:
        return ["Not enough data to generate insights."]

    insights = []
    income = df[df['category'] == 'Income']['amount'].sum()
    total_spending = df[df['category'] != 'Income']['amount'].sum()
    
    # Insight 1: Savings Rate
    if income > 0:
        savings_rate = ((income - total_spending) / income) * 100
        if savings_rate < 10:
            insights.append(f"Your savings rate is {savings_rate:.2f}%, which is low. Try to save at least 10-15% of your income.")
        else:
            insights.append(f"Great job on your savings rate of {savings_rate:.2f}%! Keep it up.")

    # Insight 2: Top Spending Category
    spending_df = df[df['category'] != 'Income']
    if not spending_df.empty:
        category_spending = spending_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        top_category = category_spending.index[0]
        top_amount = category_spending.iloc[0]
        if total_spending > 0 and (top_amount / total_spending) > 0.3:
            insights.append(f"Your highest spending category is '{top_category}', making up {top_amount/total_spending:.1%} of your expenses. Review this for potential savings.")

    if not insights:
        insights.append("Your spending habits look balanced. Keep up the great work!")

    return insights

if __name__ == '__main__':
    # This requires the database to be populated, e.g., by uploading a CSV in the main app
    try:
        score = calculate_health_score('user1')
        insights = generate_insights('user1')
        print(f"Financial Health Score for user1: {score}")
        print("Insights for user1:", insights)
    except Exception as e:
        print(f"Error: {e}. Please ensure 'financegpt.db' and 'secret.key' exist and the database is populated.")
