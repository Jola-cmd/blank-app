import pandas as pd
import streamlit as st
import plotly.express as px
from api.stocks import StockAPI
from api.etfs import ETFAPI
from api.cryptos import CryptoAPI

def get_current_prices(portfolio_df, stock_api, etf_api, crypto_api, marketdata_df):
    prices = []
    
    for _, row in portfolio_df.iterrows():
        asset_type = row['Asset class']
        symbol = row['Asset']
        
        if asset_type == 'stock':
            # Preis für eine Aktie abrufen
            current_price = stock_api.get_stock_price(symbol)
        
        elif asset_type == 'etf':
            # Preis für einen ETF abrufen
            current_price = etf_api.get_etf_price(symbol)
        
        elif asset_type == 'Cryptocurrency':
            # Sicherstellen, dass das Symbol in Großbuchstaben ist
            symbol = symbol.upper()
            
            # Prüfen, ob der Preis bereits im marketdata_df vorhanden ist
            if symbol in marketdata_df['symbol'].values:
                current_price = marketdata_df.loc[marketdata_df['symbol'] == symbol, 'price'].values[0]
            else:
                # Wenn das Symbol nicht vorhanden ist, eine API-Abfrage durchführen
                crypto_data = crypto_api.get_crypto_price(symbol)
                if crypto_data:
                    # Erstelle einen DataFrame aus dem neuen Datensatz
                    new_data = pd.DataFrame([crypto_data])
                    # Daten in den DataFrame einfügen mit pd.concat()
                    marketdata_df = pd.concat([marketdata_df, new_data], ignore_index=True)
                    current_price = crypto_data['price']
                else:
                    current_price = None  # Fehlerbehandlung, falls Preis nicht gefunden wurde
        
        else:
            current_price = None  # Fehlerbehandlung für unbekannte Asset-Klassen
        
        prices.append(current_price)
    
    return prices, marketdata_df  # Preise und aktualisierten DataFrame zurückgeben

# API Keys
ALPHA_VANTAGE_API_KEY = 'VEVMANA84U4HI8XH'
COINMARKETCAP_API_KEY = '0866730f-992b-4b95-804b-813eb18ddce9'

# Initialize API clients
stock_api = StockAPI(api_key=ALPHA_VANTAGE_API_KEY)
etf_api = ETFAPI(api_key=ALPHA_VANTAGE_API_KEY)
crypto_api = CryptoAPI(api_key=COINMARKETCAP_API_KEY)

# Load portfolio from CSV
portfolio_df = pd.read_csv('data/portfolio.csv', delimiter=';')
portfolio_df.head();

# Reziproke Anpassung des Betrags für Verkäufe
# Positive Werte für Käufe beibehalten und für Verkäufe negieren
portfolio_df['Amount Asset'] = portfolio_df.apply(
    lambda row: row['Amount Asset'] if row['Transaction Type'] == 'buy'
    else -row['Amount Asset'], axis=1
)

# Erstellen eines leeren DataFrames für die Marktinformationen
marketdata_df = pd.DataFrame(columns=['name', 'symbol', 'price', 'percent_change_24h', 'market_cap', 'volume_24h'])

# Add current prices to the DataFrame

# Preise abrufen und den aktualisierten DataFrame erhalten
prices, updated_marketdata_df = get_current_prices(portfolio_df, stock_api, etf_api, crypto_api, marketdata_df)

portfolio_df['current_price'] = prices
portfolio_df['current_value'] = portfolio_df['Amount Asset'] * portfolio_df['current_price']
portfolio_df['purchase_value'] = portfolio_df['Amount Asset'] * portfolio_df['Asset market price']

# Calculate total portfolio value
total_value = portfolio_df['current_value'].sum()

# Streamlit App
st.title("Investment Portfolio Dashboard")

# Portfolio Overview
st.header("Portfolio Overview")
st.metric(label="Current Portfolio Value", value=f"{total_value:,.2f} €")

# Allocation Pie Chart
st.subheader("Asset Class Allocation")

allocation = portfolio_df.groupby('Asset class')['current_value'].sum().reset_index()
fig_pie = px.pie(allocation, values='current_value', names='Asset class', title="Asset Allocation")
st.plotly_chart(fig_pie)

# Allocation Pie Chart
st.subheader("Current Asset Allocation")

allocation = portfolio_df.groupby('Asset')['current_value'].sum().reset_index()
fig_pie = px.pie(allocation, values='current_value', names='Asset', title="Asset Allocation")
st.plotly_chart(fig_pie)

# Performance Bar Chart
st.subheader("Asset Performance")

# Aggregation der Werte für jedes Asset
aggregated_df = portfolio_df.groupby('Asset', as_index=False).agg({
    'purchase_value': 'sum',
    'current_value': 'sum'
})

# Berechnung der Performance
portfolio_df['performance'] = aggregated_df['performance'] = aggregated_df['current_value'] - aggregated_df['purchase_value']

# Erstellen des Balkendiagramms
fig_bar = px.bar(aggregated_df, x='Asset', y=['purchase_value', 'current_value'], 
                 title="Performance Since Purchase",
                 labels={'value': 'EUR'},
                 barmode='group')

# Streamlit Chart anzeigen
st.plotly_chart(fig_bar)

# Aggregation der Werte für jedes Asset
aggregated_df = portfolio_df.groupby(['Asset class', 'Asset'], as_index=False).agg({
    'Amount Asset': 'sum',
    'Asset market price': 'mean',
    'purchase_value': 'sum',
    'current_price': 'mean',
    'current_value': 'sum',
    'performance': 'sum'
})

# Detailed View
st.subheader("Detailed Asset Information")

# Tabelle mit aggregierten Werten anzeigen
st.dataframe(aggregated_df)

# Aufklappbare Details für jedes Asset
for _, asset_row in aggregated_df.iterrows():
    asset_name = asset_row['Asset']
    
    with st.expander(f"Details for {asset_name}"):
        # Zeige alle Transaktionen für das aktuelle Asset
        asset_details = portfolio_df[portfolio_df['Asset'] == asset_name]
        st.dataframe(asset_details)

st.subheader("Detailed Market Data Information")
st.dataframe(updated_marketdata_df[['name', 'symbol', 'price', 'percent_change_24h', 'market_cap', 'volume_24h']])