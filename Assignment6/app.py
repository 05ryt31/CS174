from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
TIINGO_API_KEY = os.getenv('TIINGO_API_KEY', 'YOUR_TIINGO_API_KEY_HERE')  # Set via environment variable
DB_NAME = "stock_tracker.db"

# Database setup
def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create SearchHistory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create CachedStockData table for extra credit caching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CachedStockData (
            ticker TEXT PRIMARY KEY,
            company_json TEXT,
            stock_json TEXT,
            last_updated DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cached_data(ticker):
    """Check if we have cached data for the ticker that's less than 15 minutes old."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT company_json, stock_json, last_updated 
        FROM CachedStockData 
        WHERE ticker = ?
    ''', (ticker.upper(),))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        company_json, stock_json, last_updated = result
        # Check if data is less than 15 minutes old
        cache_time = datetime.fromisoformat(last_updated)
        if datetime.now() - cache_time < timedelta(minutes=15):
            return {
                'company': json.loads(company_json) if company_json else None,
                'stock': json.loads(stock_json) if stock_json else None,
                'from_cache': True
            }
    
    return None

def save_to_cache(ticker, company_data, stock_data):
    """Save API responses to cache."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO CachedStockData 
        (ticker, company_json, stock_json, last_updated)
        VALUES (?, ?, ?, ?)
    ''', (
        ticker.upper(),
        json.dumps(company_data) if company_data else None,
        json.dumps(stock_data) if stock_data else None,
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def save_search_history(ticker):
    """Save a search to the history table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO SearchHistory (ticker, timestamp)
        VALUES (?, ?)
    ''', (ticker.upper(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_search_history():
    """Get the last 10 searches from history."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ticker, timestamp 
        FROM SearchHistory 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"ticker": row[0], "timestamp": row[1]} for row in results]

def fetch_stock_data(ticker):
    """Fetch stock data from Tiingo API or cache."""
    # Check cache first
    cached_data = get_cached_data(ticker)
    if cached_data:
        return {
            'company': cached_data['company'],
            'stock': cached_data['stock'],
            'from_cache': True
        }
    
    # If not in cache, fetch from API
    company_data = None
    stock_data = None
    
    try:
        # Fetch company outlook data
        company_url = f"https://api.tiingo.com/tiingo/daily/{ticker}?token={TIINGO_API_KEY}"
        company_response = requests.get(company_url)
        
        if company_response.status_code == 200:
            company_data = company_response.json()
        else:
            return {'error': 'No record has been found, please enter a valid symbol.'}
        
        # Fetch stock summary data
        stock_url = f"https://api.tiingo.com/iex/{ticker}?token={TIINGO_API_KEY}"
        stock_response = requests.get(stock_url)
        
        if stock_response.status_code == 200:
            stock_data = stock_response.json()
            if isinstance(stock_data, list) and len(stock_data) > 0:
                stock_data = stock_data[0]  # Get the first element if it's a list
        
        # Save to cache
        save_to_cache(ticker, company_data, stock_data)
        
        # Save to search history
        save_search_history(ticker)
        
        return {
            'company': company_data,
            'stock': stock_data,
            'from_cache': False
        }
        
    except Exception as e:
        return {'error': f'Error fetching data: {str(e)}'}

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/search')
def search_stock():
    """API endpoint for stock search."""
    ticker = request.args.get('ticker')
    
    if not ticker:
        return jsonify({'error': 'Ticker parameter is required'}), 400
    
    result = fetch_stock_data(ticker.strip().upper())
    
    # Add cache header for extra credit
    response = jsonify(result)
    if 'from_cache' in result:
        response.headers['X-Cache'] = 'HIT' if result['from_cache'] else 'MISS'
    
    return response

@app.route('/history')
def search_history():
    """API endpoint for search history."""
    history = get_search_history()
    return jsonify(history)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)