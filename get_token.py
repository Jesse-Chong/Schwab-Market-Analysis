import os
from dotenv import load_dotenv
import requests
import base64
import json

# Load environment variables
load_dotenv()

# Get credentials from environment variables
appKey = os.getenv('SCHWAB_CLIENT_ID')
appSecret = os.getenv('SCHWAB_CLIENT_SECRET')
redirect_uri = os.getenv('SCHWAB_REDIRECT_URI')

print("\nChecking credentials:")
print(f"Client ID loaded: {appKey}")
print(f"Client Secret loaded: {appSecret}")
print(f"Redirect URI loaded: {redirect_uri}")

if not all([appKey, appSecret, redirect_uri]):
    print("\nError: Missing environment variables!")
    print("Please check your .env file")
    exit(1)

# Update authorization URL with properly formatted scopes
authUrl = (
    'https://api.schwabapi.com/v1/oauth/authorize'
    f'?client_id={appKey}'
    f'&redirect_uri={redirect_uri}'
    '&response_type=code'
    '&scope=market_data%20trader%20historical_quotes'
)

print("\nSchwab API Authentication")
print("========================")
print(f'\nClick to authenticate: {authUrl}')
print("\nAfter login, copy the FULL redirect URL, including all parameters")

# Get the redirect URL from user
returnedLink = input("\nPaste the redirect URL here: ")

# Extract the code from the returned URL
code = returnedLink[returnedLink.index('code=')+5:returnedLink.index('%40')] + '@'

# Create headers and data for token request
headers = {
    'Authorization': f'Basic {base64.b64encode(bytes(f"{appKey}:{appSecret}", "utf-8")).decode("utf-8")}',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'X-API-Key': appKey
}

data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': redirect_uri,
    'client_id': appKey,
    'client_secret': appSecret,
    'scope': 'market_data trader historical_quotes'
}

print("\nRequesting access token...")
response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
token_data = response.json()

if 'access_token' in token_data:
    # Save tokens to a file
    with open('tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    print("\nTokens saved successfully!")
    print(f"Scopes granted: {token_data.get('scope', 'Not specified')}")
else:
    print("\nError getting token")
    print(json.dumps(token_data, indent=2))