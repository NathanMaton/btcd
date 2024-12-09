import json
import sqlite3
import os
from datetime import datetime
import yagmail
from pathlib import Path

# Use the same database path as other functions
data_dir = Path(__file__).parent.parent / 'data'
data_dir.mkdir(exist_ok=True)
DB_PATH = data_dir / 'crypto.db'

def send_daily_emails(event, context):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        # Get latest market data
        c.execute('''
            SELECT fear_greed_value, btc_dominance, total_market_cap, timestamp
            FROM market_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        market_data = c.fetchone()
        
        if not market_data:
            raise Exception('No market data available')
        
        # Get active subscribers
        c.execute('SELECT email FROM subscribers WHERE is_active = 1')
        subscribers = c.fetchall()
        conn.close()
        
        yag = yagmail.SMTP(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASSWORD'))
        
        for subscriber in subscribers:
            try:
                subject = "Daily Crypto Market Report"
                content = f"""
                Crypto Market Report ({datetime.now().strftime('%Y-%m-%d')})
                
                Fear and Greed Index: {market_data[0]}
                BTC Dominance: {market_data[1]:.2f}%
                Total Market Cap: ${market_data[2]:,.2f}
                """
                
                yag.send(to=subscriber[0], subject=subject, contents=content)
            except Exception as e:
                print(f"Error sending email to {subscriber[0]}: {str(e)}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Daily emails sent successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
