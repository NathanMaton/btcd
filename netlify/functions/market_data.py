from http.server import BaseHTTPRequestHandler
import requests
import json
from datetime import datetime
import sqlite3
import os
from pathlib import Path

# Ensure the data directory exists
data_dir = Path(__file__).parent.parent / 'data'
data_dir.mkdir(exist_ok=True)
DB_PATH = data_dir / 'crypto.db'

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS market_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            fear_greed_value REAL,
            btc_dominance REAL,
            total_market_cap REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_market_data():
    headers = {
        'X-CMC_PRO_API_KEY': os.environ.get('CMC_API_KEY'),
        'Accept': 'application/json'
    }
    
    # Get Fear and Greed Index
    fear_greed_url = 'https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical'
    fear_greed_response = requests.get(fear_greed_url, headers=headers)
    fear_greed_data = fear_greed_response.json()
    
    # Get Global Metrics
    global_metrics_url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'
    global_metrics_response = requests.get(global_metrics_url, headers=headers)
    global_metrics_data = global_metrics_response.json()
    
    data = {
        'fear_greed': fear_greed_data['data'][0]['value'] if fear_greed_data['data'] else None,
        'btc_dominance': global_metrics_data['data']['btc_dominance'],
        'total_market_cap': global_metrics_data['data']['quote']['USD']['total_market_cap']
    }
    
    # Store metrics in SQLite
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''
        INSERT INTO market_metrics (fear_greed_value, btc_dominance, total_market_cap)
        VALUES (?, ?, ?)
    ''', (data['fear_greed'], data['btc_dominance'], data['total_market_cap']))
    conn.commit()
    conn.close()
    
    return data

def handler(event, context):
    try:
        # Initialize database if it doesn't exist
        init_db()
        
        data = get_market_data()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(data)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
