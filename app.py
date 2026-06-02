@st.cache_data(ttl=60)
def get_data():
    data_list = []
    tickers_obj = yf.Tickers(" ".join(tickers))
    
    for ticker in tickers:
        try:
            stock = tickers_obj.tickers[ticker]
            # שימוש ב-info בצורה בטוחה
            info = stock.info
            hist = stock.history(period="1mo")
            
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
            volume = info.get('regularMarketVolume')
            
            # בדיקת תקינות - אם אין מחיר או נפח, נדלג על המניה
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
    
    # החזרת DataFrame ריק אם לא נאספו נתונים, במקום לקרוס
    if not data_list:
        return pd.DataFrame(columns=["Ticker", "Value", "AvgValue", "Price", "Change"])
    
    return pd.DataFrame(data_list)

# לאחר מכן בקוד הראשי:
df = get_data()

if df.empty:
    st.warning("לא נמצאו נתונים זמינים. השרת מנסה למשוך נתונים מ-Yahoo Finance...")
else:
    colors = ['green' if x >= 0 else 'red' for x in df['Change']]
    # ... המשך הקוד ...