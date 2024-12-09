from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Subscriber {self.email}>'

class MarketMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    fear_greed_value = db.Column(db.Float)
    btc_dominance = db.Column(db.Float)
    total_market_cap = db.Column(db.Float)

    def __repr__(self):
        return f'<MarketMetrics {self.timestamp}>'
