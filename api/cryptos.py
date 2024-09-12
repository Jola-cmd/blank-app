import requests
import pandas as pd

class CryptoAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    
    def get_crypto_price(self, symbol: str, convert_currency='EUR'):
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        params = {
            'convert': convert_currency
        }
        response = requests.get(self.base_url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"API request failed with status code: {response.status_code}")
            return None
        
        data = response.json()
        if 'data' not in data:
            print("API response does not contain the 'data' field.")
            return None
        
        # Iterate over the cryptocurrencies and check for the matching symbol
        for crypto in data['data']:
            if isinstance(crypto, dict) and crypto.get('symbol') == symbol:
                if 'quote' in crypto and convert_currency in crypto['quote']:
                    # Return relevant data for the DataFrame
                    return {
                        'name': crypto.get('name'),
                        'symbol': crypto.get('symbol'),
                        'price': crypto['quote'][convert_currency]['price'],
                        'percent_change_24h': crypto['quote'][convert_currency].get('percent_change_24h'),
                        'market_cap': crypto['quote'][convert_currency].get('market_cap'),
                        'volume_24h': crypto['quote'][convert_currency].get('volume_24h'),
                    }
                else:
                    print(f"Price information for {symbol} is not available.")
                    return None
        
        print(f"Symbol {symbol} not found.")
        return None