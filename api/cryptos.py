import requests
import streamlit as st

class CryptoAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    
    def get_crypto_price(self, symbol: str):
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        params = {
            'convert': 'USD'
        }
        response = requests.get(self.base_url, headers=headers, params=params)
        
        if response.status_code != 200:
            st.error(f"API-Anfrage fehlgeschlagen mit Statuscode: {response.status_code}")
            return None
        
        data = response.json()
        st.write("API-Antwort:", data)  # Debugging-Ausgabe der gesamten API-Antwort
        
        if 'data' not in data:
            st.error("Antwort der API enthält nicht das 'data'-Feld.")
            return None
        
        st.write("Inhalt von data['data']:", data['data'])  # Debugging-Ausgabe der 'data'-Liste
        
        for crypto in data['data']:
            st.write("Überprüfe Symbol:", crypto.get('symbol'))  # Debugging-Ausgabe jedes Symbols
            if isinstance(crypto, dict) and crypto.get('symbol') == symbol:
                if 'quote' in crypto and 'USD' in crypto['quote']:
                    return crypto['quote']['USD']['price']
                else:
                    st.error(f"Preisinformationen für {symbol} sind nicht verfügbar.")
                    return None
        
        st.error(f"Symbol {symbol} nicht gefunden.")
        return None

# Beispiel für die Verwendung in der Streamlit-App
crypto_api = CryptoAPI(api_key="deine_api_schlüssel")
symbol = "ETHW"
price = crypto_api.get_crypto_price(symbol)
st.write(f"Preis für {symbol}:", price)



