import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# הגדרת דף כ-Wide כדי לנצל את כל רוח המסך
st.set_page_config(layout="wide", page_title="Gilboa Fragile Alert")

st.title("Gilboa Fragile Alert 📊")

tickers = ["NVDA", "INTC", "AMD", "TSMC", "MU", "SNDK", "DELL", "HPE", "AVGO", "CRWD", 
           "MRVL", "NVTS", "MDB", "IBM", "ORCL", "META", "AMZN", "TSLA", "AAPL", 
           "MSFT", "GOOGL", "PLTR", "PANW", "RGTI", "IONQ", "QBTS"]

@st.cache_data(ttl=60) # שומר בזיכרון לעדכון כל דקה
def get_data():
    data_list = []
    tickers_obj = yf.Tickers(" ".join(tickers))
    for ticker in tickers:
        try:
            stock = tickers_obj.tickers[ticker]
            hist = stock.history(period="1mo")
            info = stock.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
            volume = info.get('regularMarketVolume')
            
            if price and prev_close and volume and not hist.empty:
                change = ((price - prev_close) / prev_close) * 100
                data_list.append({
                    "Ticker": ticker,
                    "Value": price * volume,
                    "AvgValue": hist['Volume'].mean() * price,
                    "Price": price,
                    "Change": change
                })
        except: continue
    return pd.DataFrame(data_list)

df = get_data()
colors = ['green' if x >= 0 else 'red' for x in df['Change']]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df['Ticker'], y=df['Value'], marker_color=colors,
    customdata=df[['Price', 'Change']].values,
    hovertemplate="<b>%{x}</b><br>Price: $%{customdata[0]:.2f}<br>Vs Prev: %{customdata[1]:.2f}%<extra></extra>"
))

shapes = [dict(type="line", x0=i-0.4, y0=row['AvgValue'], x1=i+0.4, y1=row['AvgValue'], 
               line=dict(color="black", width=3)) for i, row in df.iterrows()]

fig.update_layout(shapes=shapes, template="plotly_white", margin=dict(b=50))

st.plotly_chart(fig, use_container_width=True)

if st.button('רענן נתונים'):
    st.rerun()