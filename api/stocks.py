import requests

class StockAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "<https://www.alphavantage.co/query>"
    
    def get_stock_price(self, symbol: str):
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()
        last_refreshed = data['Meta Data']['3. Last Refreshed']
        closing_price = data['Time Series (Daily)'][last_refreshed]['4. close']
        return float(closing_price)