


def app():
    import streamlit as st
    st.header("Prediction Engine")
    import streamlit as st
    import pandas as pd
    import numpy as np
    import yfinance as yf
    import requests
    from bs4 import BeautifulSoup
    from sklearn.model_selection import train_test_split
    from sklearn.svm import SVC
    from sklearn.linear_model import LinearRegression

    # ---------------------------------------------------------
    # Load S&P 500 Tickers (safe)
    # ---------------------------------------------------------
    @st.cache_data
    def get_sp500_tickers():
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        df = pd.read_html(str(table))[0]
        return sorted(df["Symbol"].tolist())

    tickers = get_sp500_tickers()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    st.set_page_config(page_title="Stock Buy/Sell Predictor", layout="wide")
    st.title("📈 Stock Buy/Sell & Next-Day Prediction")
    st.caption("Educational signal-based stock analysis")

    symbol = st.selectbox("Select a Stock (S&P 500)", tickers)

    # ---------------------------------------------------------
    # Prediction Logic
    # ---------------------------------------------------------
    if st.button("Run Prediction"):
        with st.spinner("Analyzing stock data..."):

            df = yf.download(symbol, period="1y")

            if df.empty:
                st.error("No data found.")
                st.stop()

            # -----------------------------
            # Feature Engineering
            # -----------------------------
            df["Open-Close"] = df["Open"] - df["Close"]
            df["High-Low"] = df["High"] - df["Low"]
            df.dropna(inplace=True)

            X = df[["Open-Close", "High-Low"]]
            y = np.where(df["Close"].shift(-1) > df["Close"], 1, -1)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=42
            )

            # -----------------------------
            # SVM Model (Buy / Sell)
            # -----------------------------
            svm_model = SVC(kernel="linear", probability=True)
            svm_model.fit(X_train, y_train)

            signal = svm_model.predict([X.iloc[-1].values])[0]
            confidence = svm_model.predict_proba([X.iloc[-1].values])[0].max() * 100

            signal_text = "BUY (Educational Signal)" if signal == 1 else "SELL (Educational Signal)"

            # -----------------------------
            # Linear Regression (Next Day Price)
            # -----------------------------
            df["Target"] = df["Close"].shift(-1)
            df.dropna(inplace=True)

            X_lr = df[["Open", "High", "Low", "Close", "Volume"]]
            y_lr = df["Target"]

            X_train_lr, X_test_lr, y_train_lr, y_test_lr = train_test_split(
                X_lr, y_lr, test_size=0.25, random_state=42
            )

            lr_model = LinearRegression()
            lr_model.fit(X_train_lr, y_train_lr)

            tomorrow_price = lr_model.predict([X_lr.iloc[-1].values])[0]
            r2_score = lr_model.score(X_test_lr, y_test_lr) * 100

            # -----------------------------
            # Stock Info
            # -----------------------------
            info = yf.Ticker(symbol).info
            name = info.get("longName", symbol)
            sector = info.get("sector", "N/A")
            market_cap = info.get("marketCap", "N/A")

        # ---------------------------------------------------------
        # Results
        # ---------------------------------------------------------
        st.subheader("📊 Analysis Result")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Stock", name)
            st.metric("Sector", sector)
            st.metric("Market Cap", market_cap)

        with col2:
            st.metric("Signal", signal_text)
            st.metric("Signal Confidence", f"{confidence:.2f}%")
            st.metric("Predicted Next-Day Close", f"${tomorrow_price:.2f}")
            st.metric("Regression Accuracy (R²)", f"{r2_score:.2f}%")

        st.info(
            "⚠️ This output is for educational and learning purposes only. "
            "Market conditions can change, and signals do not guarantee outcomes."
        )
