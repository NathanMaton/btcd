import json
import yagmail
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Use the same database path as market_data.py
data_dir = Path(__file__).parent.parent / 'data'
data_dir.mkdir(exist_ok=True)
DB_PATH = data_dir / 'crypto.db'

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def send_email_report(recipient_email):
    try:
        # Get latest market data from SQLite
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('''
            SELECT fear_greed_value, btc_dominance, total_market_cap, timestamp
            FROM market_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        market_data = c.fetchone()
        conn.close()

        if not market_data:
            raise Exception('No market data available')

        subject = "Daily Crypto Market Report"
        content = f"""
        Crypto Market Report ({datetime.now().strftime('%Y-%m-%d')})
        
        Fear and Greed Index: {market_data[0]}
        BTC Dominance: {market_data[1]:.2f}%
        Total Market Cap: ${market_data[2]:,.2f}
        """
        
        yag = yagmail.SMTP(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASSWORD'))
        yag.send(to=recipient_email, subject=subject, contents=content)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Initialize database if it doesn't exist
        init_db()
        
        body = json.loads(event['body'])
        email = body.get('email')
        
        if not email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email is required'})
            }
        
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        # Check if subscriber exists
        c.execute('SELECT is_active FROM subscribers WHERE email = ?', (email,))
        result = c.fetchone()
        
        if result:
            if result[0]:
                conn.close()
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Email already subscribed!'})
                }
            else:
                # Reactivate subscriber
                c.execute('UPDATE subscribers SET is_active = 1 WHERE email = ?', (email,))
        else:
            # Add new subscriber
            c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        
        # Send test email
        if send_email_report(email):
            conn.commit()
            conn.close()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Subscription successful! You will receive daily updates at 9:00 AM Pacific Time.'})
            }
        else:
            conn.rollback()
            conn.close()
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to send test email'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
