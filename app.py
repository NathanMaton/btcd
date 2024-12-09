from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime
import yagmail
from apscheduler.schedulers.background import BackgroundScheduler
import os
from models import db, Subscriber, MarketMetrics
from flask_migrate import Migrate
from config import config_by_name

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    
    return app

app = create_app(os.getenv('FLASK_ENV', 'dev'))

# CoinMarketCap API configuration
HEADERS = {
    'X-CMC_PRO_API_KEY': app.config['CMC_API_KEY'],
    'Accept': 'application/json'
}

def get_market_data():
    # Get Fear and Greed Index
    fear_greed_url = 'https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical'
    fear_greed_response = requests.get(fear_greed_url, headers=HEADERS)
    fear_greed_data = fear_greed_response.json()
    
    # Get Global Metrics
    global_metrics_url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'
    global_metrics_response = requests.get(global_metrics_url, headers=HEADERS)
    global_metrics_data = global_metrics_response.json()
    
    data = {
        'fear_greed': fear_greed_data['data'][0]['value'] if fear_greed_data['data'] else None,
        'btc_dominance': global_metrics_data['data']['btc_dominance'],
        'total_market_cap': global_metrics_data['data']['quote']['USD']['total_market_cap']
    }
    
    # Store metrics in database
    metrics = MarketMetrics(
        fear_greed_value=data['fear_greed'],
        btc_dominance=data['btc_dominance'],
        total_market_cap=data['total_market_cap']
    )
    with app.app_context():
        db.session.add(metrics)
        db.session.commit()
    
    return data

def send_email_report(recipient_email):
    try:
        data = get_market_data()
        
        # Email content
        subject = "Daily Crypto Market Report"
        content = f"""
        Crypto Market Report ({datetime.now().strftime('%Y-%m-%d')})
        
        Fear and Greed Index: {data['fear_greed']}
        BTC Dominance: {data['btc_dominance']:.2f}%
        Total Market Cap: ${data['total_market_cap']:,.2f}
        """
        
        # Initialize yagmail SMTP object
        yag = yagmail.SMTP(app.config['EMAIL_USER'], app.config['EMAIL_PASSWORD'])
        
        # Send email
        yag.send(to=recipient_email, subject=subject, contents=content)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/market-data')
def market_data():
    try:
        data = get_market_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Check if subscriber already exists
        subscriber = Subscriber.query.filter_by(email=email).first()
        if subscriber:
            if subscriber.is_active:
                return jsonify({'message': 'Email already subscribed!'}), 200
            else:
                subscriber.is_active = True
        else:
            subscriber = Subscriber(email=email)
            db.session.add(subscriber)
        
        # Send test email
        success = send_email_report(email)
        if success:
            db.session.commit()
            return jsonify({'message': 'Subscription successful! You will receive daily updates at 9:00 AM Pacific Time.'})
        else:
            db.session.rollback()
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Schedule daily email job at 9:00 AM Pacific Time
@scheduler.scheduled_job('cron', hour=9, minute=0, timezone='US/Pacific')
def scheduled_email_job():
    with app.app_context():
        active_subscribers = Subscriber.query.filter_by(is_active=True).all()
        for subscriber in active_subscribers:
            send_email_report(subscriber.email)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
