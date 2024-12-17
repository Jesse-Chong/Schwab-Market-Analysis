# Schwab Market Data API Application

This application allows users to fetch real-time stock quotes and market data using the Schwab API.

## Features

- Real-time stock quote retrieval
- Historical price data analysis
- Advanced stock metrics calculation, including:
  - Moving averages
  - Price channels
  - Volume analysis
  - Volatility metrics
  - Value metrics

## Prerequisites

- Python 3.11+
- Active Schwab Brokerage Account (Make sure you're signed up for individual brokerage account)
- Schwab Developer API Credentials (Approved for Market Data Production API)

## Setup

1. Clone the repository
2. Create a virtual environment:

`python -m venv venv`
`source venv/bin/activate # On Windows: venv\Scripts\activate`

3. Install dependencies:

`pip install -r requirements.txt`

4. Create a `.env` file using `.env.template` as a guide:
   env

`SCHWAB_CLIENT_ID=your_client_id_here`
`SCHWAB_CLIENT_SECRET=your_client_secret_here`
`SCHWAB_REDIRECT_URI=your_redirect_uri_here`

## Usage

### 1. Authentication (`get_token.py`) (tokens last 30 minutes)

This script handles OAuth2 authentication with Schwab's API:

- Generates authentication URL
- Handles the OAuth2 flow
- Saves access tokens for API requests

To authenticate:
python get_token.py

- Follow the URL provided
- Login to your Schwab account
- Copy and paste the redirect URL when prompted

### 2. Fetching Stock Data (`get_market_data.py`)

This script fetches and displays stock quotes:

- Real-time stock prices
- Company information
- Market data metrics
- Formatted display of stock information

To get stock quotes:

`python get_market_data.py`

- Enter a stock symbol (e.g., 'AAPL' for Apple)
- View formatted stock data
- Type 'quit' to exit

## Data Display

The application shows:

- Company name
- Current stock price
- Price change and percentage
- Day's trading range
- Trading volume
- P/E ratio
- Dividend yield
- Exchange information

## Error Handling

- Handles invalid stock symbols
- Common typo detection (e.g., 'APPL' → 'AAPL')
- API connection errors
- Authentication failures

## Security Notes

- Never commit `.env` file or `tokens.json`
- Keep your API credentials secure
- Refresh tokens every 30 minutes
- Recommended to run in a secure, private environment

## Disclaimer

This tool is for informational purposes only. Always conduct your own research and consult financial advisors before making investment decisions.