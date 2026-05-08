




def app():
    import streamlit as st
    import yfinance as yf
    import pandas as pd
    from datetime import timedelta
    st.header("visuals")

    symbol = st.text_input("Enter Stock Symbol AAPL or TCS.NS")
    if not symbol:
        st.stop()
    @st.cache_data
    def load_seven_years(symbol):
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="7y", interval="1d")
        data.reset_index(inplace=True)
        data["Date"] = pd.to_datetime(data["Date"])
        return data
    data = load_seven_years(symbol)


    # -----------------------------
    # Company statistics section
    # -----------------------------

    def get_stock_info(symbol):
        ticker = yf.Ticker(symbol)
        return ticker.info

    info = get_stock_info(symbol)

    # -------- Row 1: Price parameters --------
    current_price = info.get("currentPrice", "N/A")
    open_price = info.get("open", "N/A")
    close_price = info.get("previousClose", "N/A")  # last trading day's close

    # -------- Row 2: Other metrics --------
    volume = info.get("volume", "N/A")
    dividend_yield = info.get("dividendYield", "N/A")

    # Change %
    if current_price != "N/A" and close_price != "N/A" and close_price != 0:
        change_percent = ((current_price - close_price) / close_price) * 100
        change_percent = round(change_percent, 2)

        # Indicator text
        if change_percent > 0:
            change_display = f"▲ {change_percent}%"
        elif change_percent < 0:
            change_display = f"▼ {abs(change_percent)}%"
        else:
            change_display = "0%"
    else:
        change_display = "N/A"

    st.subheader("Key Stock Metrics")

    # =======================
    # ROW 1
    # =======================
    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        st.metric("Current Price", current_price)

    with row1_col2:
        st.metric("Open", open_price)

    with row1_col3:
        st.metric("Close", close_price)

    # =======================
    # ROW 2
    # =======================
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        st.metric("Change %", change_display)

    with row2_col2:
        st.metric("Volume", volume)

    with row2_col3:
        st.metric("Dividend Yield", dividend_yield)

    import yfinance as yf
    import plotly.graph_objects as go
    import pandas as pd
    import streamlit as st

    st.subheader("Technical Charts")

    if symbol:
        ticker = yf.Ticker(symbol)

        # -------- Quick time range buttons --------
        time_range = st.radio(
            "Select Time Range",
            options=["1m", "3m", "6m", "1y", "3y", "5y"],
            index=0,  # default = 1m
            horizontal=True
        )

        # -------- Fetch 7 years of data once --------
        hist = ticker.history(period="7y", interval="1d")
        hist.reset_index(inplace=True)

        # -------- Slice data based on selected range --------
        end_date = hist["Date"].max()
        if time_range == "1m":
            start_date = end_date - pd.DateOffset(months=1)
        elif time_range == "3m":
            start_date = end_date - pd.DateOffset(months=3)
        elif time_range == "6m":
            start_date = end_date - pd.DateOffset(months=6)
        elif time_range == "1y":
            start_date = end_date - pd.DateOffset(years=1)
        elif time_range == "3y":
            start_date = end_date - pd.DateOffset(years=3)
        elif time_range == "5y":
            start_date = end_date - pd.DateOffset(years=5)
        else:
            start_date = hist["Date"].min()

        hist_filtered = hist[hist["Date"] >= start_date]

        cand,linearea,hlcarea,volumebar,movingavg = st.tabs(["Candle Stick","Line Area","HLC Area","Volume","Moving Average"])

        with cand:
            fig = go.Figure()

            # -------- Candlestick chart --------
            fig.add_trace(
                go.Candlestick(
                    x=hist_filtered["Date"],
                    open=hist_filtered["Open"],
                    high=hist_filtered["High"],
                    low=hist_filtered["Low"],
                    close=hist_filtered["Close"],
                    name="Price",
                    increasing_line_color="#00ffff",
                    decreasing_line_color="white",
                    increasing_fillcolor="white",
                    decreasing_fillcolor="#00ffff"
                )
            )

            # -------- X-axis tick formatting --------
            total_points = len(hist_filtered)
            if total_points > 10:
                interval = total_points // 5
                tickvals = hist_filtered["Date"].iloc[::interval].tolist()
                tickvals.append(hist_filtered["Date"].iloc[-1])
                tickvals = sorted(list(set(tickvals)))
            else:
                tickvals = hist_filtered["Date"]

                

            # -------- Layout with border --------
            fig.update_layout(
                title=f"Candlestick Chart ({time_range}) — {symbol}",
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    tickmode="array",
                    tickvals=tickvals,
                    tickformat="%d-%b",
                    showgrid=True
                ),
                yaxis=dict(showgrid=True),
                plot_bgcolor="black",
                shapes=[
                    dict(
                        type="rect",
                        xref="paper",
                        yref="paper",
                        x0=0,
                        y0=0,
                        x1=1,
                        y1=1,
                        line=dict(color="black", width=2),
                        fillcolor="rgba(0,0,0,0)"
                    )
                ]
            )

            st.plotly_chart(fig, use_container_width=True)

        with linearea:
            st.subheader("Line Area Chart")
            fig = go.Figure()

            # -------- Main line + area --------
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'].squeeze(),
                mode='lines+markers',
                name='Close',
                line=dict(color='deepskyblue', width=3),
                fill='tozeroy',
                fillcolor='rgba(0,191,255,0.15)',
                marker=dict(
                    size=6,
                    color='deepskyblue',
                    line=dict(width=1, color='white')
                ),
                hovertemplate='<b>Date:</b> %{x|%d %b %Y}<br><b>Close:</b> ₹%{y:.2f}<extra></extra>'
            ))

            # -------- Glow line (blur effect) --------
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'].squeeze(),
                mode='lines',
                line=dict(color='deepskyblue', width=12),
                opacity=0.07,
                hoverinfo='skip',
                showlegend=False
            ))

            # -------- Glow area (soft background glow) --------
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'].squeeze(),
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(0,191,255,0.08)',
                line=dict(width=0),
                hoverinfo='skip',
                showlegend=False
            ))

            # -------- Layout (dark mode aesthetic) --------
            fig.update_layout(
                title=dict(
                    text=f"📈 {symbol.upper()} – Closing Price Over Time",
                    x=0.5,
                    xanchor='center',
                    font=dict(size=22, color='white')
                ),
                xaxis=dict(
                    title='Date',
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.08)',
                    tickfont=dict(color='lightgray'),
                    titlefont=dict(color='white')
                ),
                yaxis=dict(
                    title='Price (₹)',
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.08)',
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



        with hlcarea:
            fig = go.Figure()

            # -------- HIGH line --------
            fig.add_trace(go.Scatter(
                x=hist_filtered["Date"],
                y=hist_filtered["High"],
                mode="lines",
                name="High",
                line=dict(color="#00e5ff", width=2),
                hovertemplate="High: ₹%{y:.2f}<extra></extra>"
            ))

            # -------- LOW line --------
            fig.add_trace(go.Scatter(
                x=hist_filtered["Date"],
                y=hist_filtered["Low"],
                mode="lines",
                name="Low",
                line=dict(color="#ff2d75", width=2),
                hovertemplate="Low: ₹%{y:.2f}<extra></extra>"
            ))

            # -------- CLOSE line + soft area --------
            fig.add_trace(go.Scatter(
                x=hist_filtered["Date"],
                y=hist_filtered["Close"],
                mode="lines",
                name="Close",
                line=dict(color="#7b61ff", width=3),
                fill="tozeroy",
                fillcolor="rgba(123,97,255,0.12)",
                hovertemplate="Close: ₹%{y:.2f}<extra></extra>"
            ))

            # -------- X-axis ticks --------
            total_points = len(hist_filtered)
            if total_points > 10:
                interval = total_points // 5
                tickvals = hist_filtered["Date"].iloc[::interval].tolist()
                tickvals.append(hist_filtered["Date"].iloc[-1])
                tickvals = sorted(set(tickvals))
            else:
                tickvals = hist_filtered["Date"]

            # -------- Layout (matching your theme) --------
            fig.update_layout(
                title=f"HLC Area Chart ({time_range}) — {symbol.upper()}",
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    tickmode="array",
                    tickvals=tickvals,
                    tickformat="%d-%b",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)"
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)"
                ),
                plot_bgcolor="#0e0e0e",
                paper_bgcolor="#0e0e0e",
                font=dict(color="white"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig, use_container_width=True)




        with volumebar:
            fig = go.Figure()

            # -------- BASELINE (Close price) --------
            fig.add_trace(go.Scatter(
                x=hist_filtered["Date"],
                y=hist_filtered["Close"],
                mode="lines",
                name="Close",
                line=dict(color="#00e5ff", width=3),
                fill="tozeroy",
                fillcolor="rgba(0,229,255,0.15)",
                hovertemplate="<b>Date:</b> %{x|%d %b %Y}<br><b>Close:</b> ₹%{y:.2f}<extra></extra>",
                yaxis="y1"
            ))

            # -------- Glow line (optional but sexy) --------
            fig.add_trace(go.Scatter(
                x=hist_filtered["Date"],
                y=hist_filtered["Close"],
                mode="lines",
                line=dict(color="#00e5ff", width=10),
                opacity=0.07,
                hoverinfo="skip",
                showlegend=False,
                yaxis="y1"
            ))

            # # -------- VOLUME bars --------
            # fig.add_trace(go.Bar(
            #     x=hist_filtered["Date"],
            #     y=hist_filtered["Volume"],
            #     name="Volume",
            #     marker=dict(color="#00e5ff"),
            #     yaxis="y2",
            #     hovertemplate="<b>Volume:</b> %{y:,}<extra></extra>"
            # ))


            fig.add_trace(go.Bar(
            x=hist_filtered["Date"],
            y=hist_filtered["Volume"],
            name="Volume",
            yaxis="y2",
            marker=dict(
                color="rgba(255,255,255,0.25)",   # inner fill
                line=dict(
                    color="#00e5ff",               # border color
                    width=1                         # border thickness
                )
            ),
            hovertemplate="<b>Volume:</b> %{y:,}<extra></extra>"
        ))



            # -------- X-axis ticks --------
            total_points = len(hist_filtered)
            if total_points > 10:
                interval = total_points // 5
                tickvals = hist_filtered["Date"].iloc[::interval].tolist()
                tickvals.append(hist_filtered["Date"].iloc[-1])
                tickvals = sorted(set(tickvals))
            else:
                tickvals = hist_filtered["Date"]

            # -------- Layout (dual-axis setup) --------
            fig.update_layout(
                title=f"Baseline + Volume ({time_range}) — {symbol.upper()}",
                xaxis=dict(
                    tickmode="array",
                    tickvals=tickvals,
                    tickformat="%d-%b",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)"
                ),
                yaxis=dict(
                    title="Price",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)",
                    side="left"
                ),
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    rangemode="tozero"
                ),
                barmode="overlay",
                plot_bgcolor="#0e0e0e",
                paper_bgcolor="#0e0e0e",
                font=dict(color="white"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

        with movingavg:
            import plotly.graph_objects as go

            # ===============================
            # Parameters
            # ===============================
            ma_period = 20  # change to 9, 20, 50, 200

            # ===============================
            # Prepare data
            # ===============================
            df = hist_filtered.copy()

            # Moving Average
            df["SMA"] = df["Close"].rolling(window=ma_period).mean()

            # ===============================
            # Build chart
            # ===============================
            fig = go.Figure()

            # -------- Close price --------
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["Close"],
                mode="lines",
                name="Close",
                line=dict(color="#00e5ff", width=3),
                hovertemplate="<b>Date:</b> %{x|%d %b %Y}<br><b>Close:</b> ₹%{y:.2f}<extra></extra>"
            ))

            # -------- Moving Average --------
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["SMA"],
                mode="lines",
                name=f"SMA {ma_period}",
                line=dict(color="#ffb703", width=2),
                hovertemplate=f"SMA {ma_period}: ₹%{{y:.2f}}<extra></extra>"
            ))

            # ===============================
            # Layout (clean TradingView style)
            # ===============================
            fig.update_layout(
                title=f"Close Price + SMA {ma_period} — {symbol.upper()}",
                hovermode="x unified",

                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)",
                    tickformat="%d-%b"
                ),

                yaxis=dict(
                    title="Price",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)"
                ),

                plot_bgcolor="#0e0e0e",
                paper_bgcolor="#0e0e0e",
                font=dict(color="white"),
                height=500,
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

 