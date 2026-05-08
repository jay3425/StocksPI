

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import date,datetime
import time
from streamlit_autorefresh import st_autorefresh
import requests



def app():
    # ------------------ Page Config ------------------
    st.set_page_config(page_title="📈 Stock Data Viewer", layout="centered")

    # ------------------ Title ------------------
    st.header("📆 Real-Time Stock Data")

    st.markdown("""
    Enter a stock **ticker symbol** (like `AAPL`, `TSLA`, `INFY`) and a date range below 
    to view the stock's **closing prices**.
    """)

    ticker = st.text_input("🔍 Enter Stock Ticker:", value="AAPL").upper()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date", value=date(2024, 1, 1))
    with col2:
        end_date = st.date_input("📅 End Date", value=date.today())

    # ------------------ Data Fetching and Validation ------------------
    if ticker and start_date and end_date:
        if start_date >= end_date:
            st.warning("⚠️ Start date must be before end date.")
        else:
            try:
                st.info(f"Fetching data for **{ticker}**...")
                data = yf.download(ticker, start=start_date, end=end_date)

                if data.empty:
                    st.error("❌ No data found. Please check the ticker symbol or date range.")
                elif 'Close' not in data.columns:
                    st.error("❌ 'Close' column not found in the data.")
                else:
                    st.success("✅ Data loaded successfully!")

                    # Plotting
                    # fig = px.line(
                    #     x=data.index,
                    #     y=data['Close'].squeeze(),
                    #     labels={"x": "Date", "y": "Closing Price"},
                    #     title=f"{ticker} - Closing Price Over Time"
                    # )
                    # st.plotly_chart(fig, use_container_width=True)



                    # Create a more interactive and styled line chart
                    fig = go.Figure()

                    # Add glowing effect using shadow-style layering
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Close'].squeeze(),
                        mode='lines+markers',
                        name='Close',
                        line=dict(color='deepskyblue', width=4),
                        marker=dict(size=6, color='deepskyblue', line=dict(width=1, color='white')),
                        hovertemplate='<b>Date:</b> %{x|%d %b %Y}<br><b>Close:</b> ₹%{y:.2f}<extra></extra>'
                    ))

                    # Add blurred "glow" using wider transparent line underneath (fake glow)
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Close'].squeeze(),
                        mode='lines',
                        line=dict(color='deepskyblue', width=10),
                        opacity=0.08,
                        name='',
                        hoverinfo='skip',
                        showlegend=False
                    ))

                    # Layout customization for dark mode
                    fig.update_layout(
                        title=dict(
                            text=f"📈 {ticker.upper()} – Closing Price Over Time",
                            x=0.5,
                            xanchor='center',
                            font=dict(size=22, family='Arial', color='white')
                        ),
                        xaxis=dict(
                            title='Date',
                            showgrid=True,
                            gridcolor='rgba(255,255,255,0.1)',
                            tickfont=dict(color='lightgray'),
                            titlefont=dict(color='white')
                        ),
                        yaxis=dict(
                            title='Price (₹)',
                            showgrid=True,
                            gridcolor='rgba(255,255,255,0.1)',
                            tickfont=dict(color='lightgray'),
                            titlefont=dict(color='white')
                        ),
                        hovermode='x unified',
                        margin=dict(t=70, l=60, r=40, b=60),
                        plot_bgcolor='#111111',
                        paper_bgcolor='#111111',
                        font=dict(color='white'),
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"❌ An error occurred: `{e}`")
    else:
        st.info("👆 Please enter a ticker symbol and select a valid date range.")

    st.subheader("📊 Real-Time Financial Metrics")

    if ticker:
            stock = yf.Ticker(ticker)
            info = stock.info

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${info['regularMarketPrice']}")
                st.metric("Previous Close", f"${info['previousClose']}")
            with col2:
                st.metric("Market Cap", f"${round(info['marketCap'] / 1e9, 2)} B")
                st.metric("P/E Ratio", info.get("trailingPE", "N/A"))
            with col3:
                st.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.metric("52W Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}")


    # st.subheader("🔍 Latest Data Snapshot")
    # data2 = data.copy()
    # data2['% Change'] = data2['Close'] / data2['Close'].shift(1) - 1
    # data2.dropna(inplace=True)
    # st.dataframe(data2, use_container_width=True)
    # ------------------ Tabs ------------------
    pricing_data,live_data , news = st.tabs(["Pricing Data","Live data", "Top News"])

        # Show data
    with pricing_data:
        st.subheader("📊 Pricing Data Overview")

        # Copy and process data
        data2 = data.copy()
        data2['% Change'] = data2['Close'].pct_change()
        data2.dropna(inplace=True)
        annual_return = data2['% Change'].mean()*252*100
        stdev = np.std(data2["% Change"]*np.sqrt(252))

        # Format % Change with directional markers
        def format_change(val):
            if val > 0:
                return f"🟢 +{val:.2%}"
            elif val < 0:
                return f"🔴 {val:.2%}"
            else:
                return f"➖ {val:.2%}"

        data2['% Change'] = data2['% Change'].apply(format_change)

        # Optional: Format index for better readability
        data2.index = data2.index.strftime('%Y-%m-%d %H:%M')

        st.markdown("### 🔍 Latest Snapshot with Directional Movement")
        st.dataframe(data2[['Open', 'High', 'Low', 'Close', '% Change']], use_container_width=True)
        st.write("Annualized Return: " ,annual_return,"%")
        st.write("Standard Deviation: " ,stdev*100,"%")
        st.write("Risk Adj. Return is ",annual_return/(stdev*100))




    with live_data:
        st.subheader("🔁 Live Price Tracker")

        # Slider to choose refresh interval
        refresh_rate = st.slider("⏱️ Refresh every X seconds", 5, 60, 10)

        # Initialize session state
        if "live_tracking" not in st.session_state:
            st.session_state.live_tracking = False
        if "prev_price" not in st.session_state:
            st.session_state.prev_price = None

        # Start and Stop buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Live Tracking"):
                st.session_state.live_tracking = True
        with col2:
            if st.button("⏹️ Stop Tracking"):
                st.session_state.live_tracking = False

        # Placeholder to display price
        live_placeholder = st.empty()

        # If tracking is enabled
        if st.session_state.live_tracking:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=refresh_rate * 1000, limit=20, key="live_refresh")

            try:
                live_data = yf.Ticker(ticker).history(period="1d", interval="1m")

                if not live_data.empty:
                    current_price = live_data["Close"].iloc[-1]
                    prev_price = st.session_state.prev_price

                    # Direction arrow
                    if prev_price is None:
                        direction = "⏳"
                        color = "white"
                    elif current_price > prev_price:
                        direction = "🔺"
                        color = "green"
                    elif current_price < prev_price:
                        direction = "🔻"
                        color = "red"
                    else:
                        direction = "➖"
                        color = "gray"

                    # Display price
                    live_placeholder.markdown(
                        f"<h2 style='color:{color}; text-align:center;'>💵 {ticker}: {current_price:.2f} {direction}</h2>",
                        unsafe_allow_html=True
                    )
                    st.session_state.prev_price = current_price
                else:
                    live_placeholder.error("❌ Failed to fetch live data.")
            except Exception as e:
                live_placeholder.error(f"⚠️ Error fetching live data: `{e}`")



    with news:
        def fetch_news(ticker):
            api_key = '66470d4c9fb541efb09116ab59d3a101'
            url = f'https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&apiKey={api_key}'
            response = requests.get(url)
            news_data = response.json()
            return news_data['articles'][:5]

        st.subheader("📰 Latest News")

        ticker = st.text_input("Enter Ticker (e.g., AAPL)")
        if ticker:
            try:
                articles = fetch_news(ticker)
                for article in articles:
                    st.markdown(f"**{article['title']}**")
                    st.write(f"{article['source']['name']} | {article['publishedAt']}")
                    st.write(article['description'])
                    st.markdown(f"[Read more]({article['url']})", unsafe_allow_html=True)
                    st.markdown("---")
            except:
                st.warning("Unable to fetch news.")









 



