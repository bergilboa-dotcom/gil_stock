import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# הגדרת הדף לרוחב מלא
st.set_page_config(layout="wide", page_title="Gilboa Fragile Alert")

st.title("Gilboa Fragile Alert 📊")

tickers = ["NVDA", "INTC", "MU", "SNDK", "DELL", "HPE", "AVGO", 
           "MRVL","NVTS", "MDB", "IBM", "ORCL", "META", 
           "MSFT", "GOOGL", "QBTS"]

@st.cache_data(ttl=60)
def get_data():
    data_list = []
    tickers_obj = yf.Tickers(" ".join(tickers))
    
    for ticker in tickers:
        try:
            stock = tickers_obj.tickers[ticker]
            # שליפת היסטוריה ומידע
            hist = stock.history(period="1mo")
            info = stock.info
            
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
            volume = info.get('regularMarketVolume')
            
            if price and prev_close and volume:
                change = ((price - prev_close) / prev_close) * 100
                data_list.append({
                    "Ticker": ticker,
                    "Value": price * volume,
                    "AvgValue": hist['Volume'].mean() * price if not hist.empty else 0,
                    "Price": price,
                    "Change": change
                })
        except:
            continue
    
    return pd.DataFrame(data_list)

# טעינת הנתונים
df = get_data()

if df.empty:
    st.warning("לא נמצאו נתונים זמינים כרגע. אנא נסה לרענן.")
else:
    # יצירת צבעים
    colors = ['green' if x >= 0 else 'red' for x in df['Change']]

    # יצירת הגרף
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Ticker'], 
        y=df['Value'], 
        marker_color=colors,
        customdata=df[['Price', 'Change']].values,
        hovertemplate="<b>%{x}</b><br>Price: $%{customdata[0]:.2f}<br>Vs Prev: %{customdata[1]:.2f}%<extra></extra>"
    ))

    # הוספת קווי ממוצע
    shapes = [dict(type="line", x0=i-0.4, y0=row['AvgValue'], x1=i+0.4, y1=row['AvgValue'], 
                   line=dict(color="black", width=3)) for i, row in df.iterrows()]

    fig.update_layout(
        shapes=shapes, 
        template="plotly_white", 
        margin=dict(b=50),
        xaxis_title="Tickers",
        yaxis_title="Money Flow"
    )

    st.plotly_chart(fig, use_container_width=True)

# כפתור רענון ידני
if st.button('רענן נתונים כעת'):
    st.rerun()
