# Crypto Market Dashboard

A web application that displays real-time cryptocurrency market metrics including the Fear & Greed Index, Bitcoin dominance, and total market capitalization. It also provides daily email updates with these metrics.

## Features

- Real-time display of crypto market metrics
- Modern, responsive UI using Tailwind CSS
- Daily email updates
- Easy email subscription system

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the environment variables in `.env`:
- Set your Gmail credentials:
  - `EMAIL_USER`: Your Gmail address
  - `EMAIL_PASSWORD`: Your Gmail app password (not your regular password)
    - To get an app password:
      1. Go to your Google Account settings
      2. Navigate to Security
      3. Enable 2-Step Verification if not already enabled
      4. Create an App Password under 2-Step Verification

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Email Configuration

The application uses Gmail to send daily updates. Make sure to:
1. Use a Gmail account
2. Generate an app password for the email account
3. Update the `.env` file with your email credentials

## API Documentation

The application uses the following CoinMarketCap API endpoints:
- Fear and Greed Index: `GET https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical`
- Global Metrics: `GET https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest`
