import pandas as pd
import streamlit as st
import plotly.express as px
from api.stocks import StockAPI
from api.etfs import ETFAPI
from api.cryptos import CryptoAPI

# API Keys
ALPHA_VANTAGE_API_KEY = 'VEVMANA84U4HI8XH'
COINMARKETCAP_API_KEY = '4bacb768-5717-44ca-a678-1fa6cc71d634'

# Initialize API clients
stock_api = StockAPI(api_key=ALPHA_VANTAGE_API_KEY)
etf_api = ETFAPI(api_key=ALPHA_VANTAGE_API_KEY)
crypto_api = CryptoAPI(api_key=COINMARKETCAP_API_KEY)

# Load portfolio from CSV
portfolio_df = pd.read_csv('data/portfolio.csv', delimiter=';')
portfolio_df.head();

def get_current_prices():
    prices = []
    
    for _, row in portfolio_df.iterrows():
        asset_type = row['Asset class']
        symbol = row['Asset']
        
        if asset_type == 'stock':
            current_price = stock_api.get_stock_price(symbol)
        elif asset_type == 'etf':
            current_price = etf_api.get_etf_price(symbol)
        elif asset_type == 'Cryptocurrency':
            current_price = crypto_api.get_crypto_price(symbol.upper())
        
        prices.append(current_price)
    
    return prices

# Add current prices to the DataFrame
portfolio_df['current_price'] = get_current_prices()
portfolio_df['current_value'] = portfolio_df['quantity'] * portfolio_df['current_price']
portfolio_df['purchase_value'] = portfolio_df['quantity'] * portfolio_df['purchase_price']

# Calculate total portfolio value
total_value = portfolio_df['current_value'].sum()

# Streamlit App
st.title("Investment Portfolio Dashboard")

# Portfolio Overview
st.header("Portfolio Overview")
st.metric(label="Current Portfolio Value", value=f"${total_value:,.2f}")

# Allocation Pie Chart
st.subheader("Asset Allocation")

allocation = portfolio_df.groupby('type')['current_value'].sum().reset_index()
fig_pie = px.pie(allocation, values='current_value', names='type', title="Asset Allocation")
st.plotly_chart(fig_pie)

# Performance Bar Chart
st.subheader("Asset Performance")

portfolio_df['performance'] = portfolio_df['current_value'] - portfolio_df['purchase_value']
fig_bar = px.bar(portfolio_df, x='symbol', y=['purchase_value', 'current_value'], 
                 title="Performance Since Purchase",
                 labels={'value': 'USD'},
                 barmode='group')
st.plotly_chart(fig_bar)

# Detailed View
st.subheader("Detailed Asset Information")
st.dataframe(portfolio_df[['type', 'symbol', 'quantity', 'purchase_price', 'current_price', 'purchase_value', 'current_value', 'performance']])