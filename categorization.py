import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pickle
import os

# Expanded synthetic training data with 15 categories
data = {
    'description': [
        'STARBUCKS', 'MCDONALDS', 'CHEESECAKE FACTORY', 'DOORDASH',
        'SAFEWAY', 'TRADER JOES', 'WHOLE FOODS MARKET',
        'UBER TRIP', 'LYFT RIDE', 'BART FARE',
        'PG&E', 'COMCAST', 'T-MOBILE',
        'RENT PAYMENT', 'MORTGAGE PAYMENT',
        'AMAZON.COM', 'TARGET', 'NORDSTROM',
        'NETFLIX.COM', 'SPOTIFY', 'AMC THEATRES',
        'CVS PHARMACY', '24 HOUR FITNESS', 'KAISER PERMANENTE',
        'UNITED AIRLINES', 'MARRIOTT HOTELS', 'EXPEDIA',
        'UNIVERSITY OF CALIFORNIA', 'COURSERA',
        'SEPHORA', 'ULTA BEAUTY',
        'RED CROSS DONATION', 'UNICEF',
        'ROBINHOOD', 'COINBASE',
        'PAYCHECK DEPOSIT', 'FREELANCE INCOME',
        'MISC PURCHASE', 'ATM WITHDRAWAL'
    ],
    'category': [
        'Food & Dining', 'Food & Dining', 'Food & Dining', 'Food & Dining',
        'Groceries', 'Groceries', 'Groceries',
        'Transportation', 'Transportation', 'Transportation',
        'Utilities', 'Utilities', 'Utilities',
        'Rent/Mortgage', 'Rent/Mortgage',
        'Shopping', 'Shopping', 'Shopping',
        'Entertainment', 'Entertainment', 'Entertainment',
        'Health & Wellness', 'Health & Wellness', 'Health & Wellness',
        'Travel', 'Travel', 'Travel',
        'Education', 'Education',
        'Personal Care', 'Personal Care',
        'Gifts & Donations', 'Gifts & Donations',
        'Investments', 'Investments',
        'Income', 'Income',
        'Miscellaneous', 'Miscellaneous'
    ]
}
df = pd.DataFrame(data)

# Create ML pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=100, stop_words='english')),
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Train model
def train_model():
    X = df['description']
    y = df['category']
    pipeline.fit(X, y)
    with open('model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    print("Model trained and saved as model.pkl")

# Categorize transactions
def categorize(transactions_df):
    if not os.path.exists('model.pkl'):
        train_model()
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    descriptions = transactions_df['description']
    predictions = model.predict(descriptions)
    probabilities = model.predict_proba(descriptions)
    confidence = [max(prob) for prob in probabilities]
    
    result_df = pd.DataFrame({
        'description': descriptions,
        'category': predictions,
        'confidence': confidence
    })
    return result_df

if __name__ == '__main__':
    train_model()
    # Test categorization
    test_data = pd.DataFrame({'description': ['Supermarket', 'Taxi Fare', 'AMAZON PURCHASE']})
    result = categorize(test_data)
    print("\n--- Test Categorization ---")
    print(result)
