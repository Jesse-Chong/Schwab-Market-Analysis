import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Load tokens from file
with open('tokens.json', 'r') as f:
    token_data = json.load(f)

access_token = token_data['access_token']
appKey = os.getenv('SCHWAB_CLIENT_ID')

def get_stock_quote(symbol):
    """Single API call for quote and fundamental data"""
    endpoint = 'https://api.schwabapi.com/marketdata/v1/quotes'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'X-API-Key': appKey
    }
    
    params = {
        'symbols': symbol,
        'fields': 'quote,fundamental'
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_price_history(symbol, period_type='year', period=2, frequency_type='daily'):
    """Single API call for historical data"""
    endpoint = 'https://api.schwabapi.com/marketdata/v1/pricehistory'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'X-API-Key': appKey
    }
    
    params = {
        'symbol': symbol,
        'periodType': period_type,
        'period': period,
        'frequencyType': frequency_type,
        'frequency': 1
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def calculate_metrics(prices, quote, fundamental):
    """Calculate all available metrics from the data"""
    return {
        # Original metrics
        'moving_averages': calculate_moving_averages(prices),
        'price_channels': calculate_price_channels(prices),
        'volume_metrics': calculate_volume_metrics(prices),
        'volatility_metrics': calculate_volatility_metrics(prices),
        
        # New metrics
        'value_metrics': calculate_value_metrics(fundamental),
        'risk_metrics': calculate_risk_metrics(prices)
    }

def calculate_moving_averages(prices):
    """Calculate moving averages for multiple periods"""
    if not prices:
        return {}
    
    closes = [p['close'] for p in prices]
    current_price = closes[-1]
    periods = [5, 10, 20, 50, 100, 200]
    
    mas = {}
    for period in periods:
        if len(closes) >= period:
            ma = sum(closes[-period:]) / period
            mas[f'{period}MA'] = ma
            mas[f'{period}MA_Diff'] = ((current_price / ma - 1) * 100)
    return mas

def calculate_price_channels(prices):
    """Calculate price channels and positions"""
    if not prices:
        return {}
    
    periods = [5, 10, 20, 50]
    channels = {}
    
    for period in periods:
        if len(prices) >= period:
            period_prices = prices[-period:]
            high = max(p['high'] for p in period_prices)
            low = min(p['low'] for p in period_prices)
            current = prices[-1]['close']
            channels[f'{period}D'] = {
                'high': high,
                'low': low,
                'position': ((current - low) / (high - low) * 100)
            }
    return channels

def calculate_volume_metrics(prices):
    """Calculate volume-based metrics"""
    if not prices:
        return {}
    
    periods = [5, 10, 20, 50]
    metrics = {}
    current_vol = prices[-1]['volume']
    
    for period in periods:
        if len(prices) >= period:
            period_vol = prices[-period:]
            avg_vol = sum(p['volume'] for p in period_vol) / period
            metrics[f'{period}D'] = {
                'avg_volume': avg_vol,
                'ratio': current_vol / avg_vol if avg_vol else 0
            }
    return metrics

def calculate_volatility_metrics(prices):
    """Calculate volatility and ATR"""
    if not prices:
        return {}
    
    periods = [5, 10, 20, 50]
    metrics = {}
    
    for period in periods:
        if len(prices) >= period:
            period_prices = prices[-period:]
            daily_returns = []
            true_ranges = []
            
            for i in range(1, len(period_prices)):
                # Daily returns
                daily_return = (period_prices[i]['close'] - period_prices[i-1]['close']) / period_prices[i-1]['close']
                daily_returns.append(daily_return)
                
                # True Range
                high = period_prices[i]['high']
                low = period_prices[i]['low']
                prev_close = period_prices[i-1]['close']
                true_range = max(high - low, abs(high - prev_close), abs(low - prev_close))
                true_ranges.append(true_range)
            
            if daily_returns:
                volatility = (sum(r*r for r in daily_returns) / len(daily_returns)) ** 0.5 * (252 ** 0.5)
                atr = sum(true_ranges) / len(true_ranges)
                
                metrics[f'{period}D'] = {
                    'volatility': volatility,
                    'atr': atr
                }
    return metrics

def calculate_value_metrics(fundamental):
    """Calculate value metrics from available fundamental data"""
    try:
        pe_ratio = fundamental.get('peRatio')
        earnings_yield = (1 / pe_ratio * 100) if pe_ratio and pe_ratio != 0 else None
        
        return {
            'pe_ratio': pe_ratio,
            'earnings_yield': earnings_yield,
            'dividend_yield': fundamental.get('divYield', 0),
            'eps': fundamental.get('eps')
        }
    except Exception as e:
        print(f"Error calculating value metrics: {e}")
        return {}

def calculate_risk_metrics(prices):
    """Calculate risk metrics including beta"""
    try:
        if not prices:
            return {}
            
        # Calculate daily returns
        returns = []
        for i in range(1, len(prices)):
            daily_return = (prices[i]['close'] - prices[i-1]['close']) / prices[i-1]['close']
            returns.append(daily_return)
            
        # Calculate beta (using market volatility as 1 for simplification)
        if returns:
            volatility = (sum(r*r for r in returns) / len(returns)) ** 0.5 * (252 ** 0.5)
            beta = volatility  # Simplified beta calculation
            
            return {
                'beta': beta,
                'volatility_annual': volatility
            }
        return {}
    except Exception as e:
        print(f"Error calculating risk metrics: {e}")
        return {}

def display_metrics(symbol, quote, fundamental, prices, metrics):
    """Display metrics with improved formatting"""
    def print_section(title):
        print(f"\n{title}")
        print("=" * 50)
        
    def print_subsection(title):
        print(f"\n{title}")
        print("-" * 50)
    
    def format_price(value):
        return f"${value:,.2f}" if value is not None else "N/A"
    
    def format_percent(value):
        return f"{value:,.2f}%" if value is not None else "N/A"
    
    def format_volume(value):
        return f"{value:,}" if value is not None else "N/A"

    # Main Display
    print_section("Comprehensive Stock Analysis")
    
    # Basic Information
    print_subsection(f"Basic Information for {symbol}")
    current_price = quote.get('lastPrice')
    print(f"Current Price: {format_price(current_price)}")
    print(f"Day Range: {format_price(quote.get('lowPrice'))} - {format_price(quote.get('highPrice'))}")
    print(f"52-Week Range: {format_price(quote.get('52WeekLow'))} - {format_price(quote.get('52WeekHigh'))}")
    print(f"Volume: {format_volume(quote.get('totalVolume'))}")
    print(f"Avg Daily Volume (1Y): {format_volume(fundamental.get('avg1YearVolume'))}")
    
    # Value Metrics
    print_subsection("Value Metrics")
    value = metrics.get('value_metrics', {})
    print(f"P/E Ratio: {format_percent(value.get('pe_ratio')).replace('%', '')}")
    print(f"Earnings Yield: {format_percent(value.get('earnings_yield'))}")
    print(f"Dividend Yield: {format_percent(value.get('dividend_yield'))}")
    print(f"EPS: {format_price(value.get('eps'))}")
    
    # Technical Analysis
    print_subsection("Moving Averages")
    mas = metrics.get('moving_averages', {})
    for period in [5, 10, 20, 50, 100, 200]:
        if f'{period}MA' in mas:
            ma_price = mas[f'{period}MA']
            ma_diff = mas[f'{period}MA_Diff']
            print(f"{period:3d}-Day MA: {format_price(ma_price)} ({format_percent(ma_diff)})")
    
    # Price Channels
    print_subsection("Price Channels")
    channels = metrics.get('price_channels', {})
    for period in [5, 10, 20, 50]:
        channel = channels.get(f'{period}D')
        if channel:
            print(f"\n{period}-Day Channel:")
            print(f"  High: {format_price(channel['high'])}")
            print(f"  Low: {format_price(channel['low'])}")
            print(f"  Position: {format_percent(channel['position'])}")
    
    # Volume Analysis
    print_subsection("Volume Analysis")
    vol_metrics = metrics.get('volume_metrics', {})
    for period in [5, 10, 20, 50]:
        vol = vol_metrics.get(f'{period}D')
        if vol:
            print(f"{period:2d}-Day Avg Volume: {format_volume(vol['avg_volume'])}")
            print(f"{period:2d}-Day Volume Ratio: {vol['ratio']:.2f}x")
    
    # Volatility Metrics
    print_subsection("Volatility Metrics")
    vol = metrics.get('volatility_metrics', {})
    for period in [5, 10, 20, 50]:
        metrics = vol.get(f'{period}D')
        if metrics:
            print(f"\n{period}-Day Metrics:")
            print(f"  Volatility: {format_percent(metrics['volatility'])}")
            print(f"  ATR: {format_price(metrics['atr'])}")

def get_focused_metrics(symbol):
    """Main function to get and display all metrics"""
    print(f"\nFetching data for {symbol}...")
    quote_data = get_stock_quote(symbol)
    
    if not quote_data or symbol not in quote_data:
        print(f"Error: Unable to fetch quote data for {symbol}")
        return
    
    # Extract data
    stock = quote_data[symbol]
    quote = stock.get('quote', {})
    fundamental = stock.get('fundamental', {})
    
    # Get historical data
    print("Fetching historical data...")
    historical_data = get_price_history(symbol)
    prices = historical_data.get('candles', []) if historical_data else []
    
    # Calculate all metrics
    metrics = calculate_metrics(prices, quote, fundamental)
    
    # Display results
    display_metrics(symbol, quote, fundamental, prices, metrics)

if __name__ == "__main__":
    print("\nSchwab Market Data API - Focused Analysis")
    print("=" * 40)
    
    while True:
        symbol = input("\nEnter a stock symbol (or 'quit' to exit): ").upper()
        if symbol == 'QUIT':
            break
        
        get_focused_metrics(symbol)