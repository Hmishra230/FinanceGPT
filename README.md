# FinanceGPT Backend

This is the Flask backend for the FinanceGPT project. It provides a serverless-compatible API for managing personal finance data.

## Features

- File uploads for transaction data (CSV format)
- Secure, encrypted storage of financial data
- API endpoints for:
  - Transaction categorization
  - Dashboard data retrieval
  - AI-generated insights
  - Budget recommendations
  - Financial health scoring

## Prerequisites

- Python 3.10

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd FinanceGPT
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database (optional, for a clean setup):**
    This script will create the necessary tables and a sample user. **Warning:** Running this script will delete all existing data.
    ```bash
    python init_db.py
    ```

5.  **Load sample data (optional):**
    To populate the database with sample transactions, run the following command. This will load data from `transactions.csv`.
    ```bash
    python load_data.py
    ```

## Running the Application

1.  **Start the Flask development server:**
    ```bash
    python app.py
    ```
    The application will be running at `http://127.0.0.1:5001`.

2.  **Running with Gunicorn (for production-like environment):**
    ```bash
    gunicorn --bind 0.0.0.0:5001 app:app
    ```

## Deployment to Vercel

This project is configured for serverless deployment on Vercel.

1.  **Install the Vercel CLI:**
    ```bash
    npm install -g vercel
    ```

2.  **Log in to your Vercel account:**
    ```bash
    vercel login
    ```

3.  **Deploy the application:**
    From the project's root directory, run the following command:
    ```bash
    vercel --prod
    ```
    Vercel will automatically detect the `vercel.json` configuration and deploy the application.

## API Endpoints

- `POST /api/upload`
  - Upload a CSV file with transaction data.
  - `user_id` can be passed as a form field.
- `GET /api/dashboard/<user_id>`
  - Retrieve all transactions for a given user.
- `POST /api/categorize`
  - (Not Implemented) Categorize transactions.
- `GET /api/insights/<user_id>`
  - (Not Implemented) Get AI-generated financial insights.
- `POST /api/budget`
  - (Not Implemented) Get budget recommendations.
- `GET /api/health-score/<user_id>`
  - (Not Implemented) Get a financial health score.

## Security

Financial data is encrypted at rest using the Fernet symmetric encryption algorithm from the `cryptography` package. A secret key is generated automatically and stored in `secret.key`. This file should be kept secure and should not be committed to version control (`.gitignore` is configured to ignore it).
