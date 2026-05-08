# sentiments.py
"""
Streamlit Sentiment Analysis panel for StocksPi

Features:
- Input a ticker (NSE/NYSE style, e.g., RELIANCE.NS or AAPL)
- Fetch latest news via NewsAPI (requires env NEWSAPI_KEY) -- graceful fallback if missing
- Analyze sentiment per article using HF transformers pipeline (if installed) or VaderSentiment
- Produce per-source and aggregated sentiment scores (0-100)
- Visualize results (bar chart + pie + table) and simple textual explanation
- Designed to be plug-and-play into StocksPi dashboard or used standalone

Install required packages (recommended):
pip install streamlit yfinance requests pandas numpy plotly transformers torch vaderSentiment

Environment variables (optional, recommended for real news):
- NEWSAPI_KEY    (https://newsapi.org/)
- GROQ_API_KEY   (if you later want to call Groq for Pi explanations — optional)
"""

import os
import time
from typing import List, Dict, Tuple
import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()


# Visualization
import plotly.express as px

def app():
    st.set_page_config(
            page_title="Sentiments",
            page_icon="📺",
            layout="wide"
        )
    # Sentiment engines
    SENTIMENT_ENGINE = None
    use_transformers = False
    try:
        from transformers import pipeline
        # load a light sentiment model — will try to reuse cache if available
        sentiment_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        SENTIMENT_ENGINE = "transformers"
        use_transformers = True
    except Exception:
        # fallback to vader
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        vader = SentimentIntensityAnalyzer()
        SENTIMENT_ENGINE = "vader"


    st.set_page_config(page_title="StocksPi — Sentiment Panel", layout="wide", initial_sidebar_state="expanded")

    # -------------------------
    # Helper: fetch company news
    # -------------------------
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()

    @st.cache_data(ttl=60*10)
    def fetch_news_via_newsapi(query: str, page_size: int = 10) -> List[Dict]:
        """
        Fetch recent news articles for `query` via NewsAPI.
        Requires NEWSAPI_KEY env var. Returns list of articles (title, source, description, url)
        """
        if not NEWSAPI_KEY:
            return []
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "pageSize": page_size,
            "sortBy": "publishedAt",
            "apiKey": NEWSAPI_KEY
        }
        try:
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            data = r.json()
            articles = []
            for a in data.get("articles", []):
                articles.append({
                    "title": a.get("title") or "",
                    "source": (a.get("source") or {}).get("name") or "Unknown",
                    "description": a.get("description") or "",
                    "content": a.get("content") or "",
                    "url": a.get("url") or "",
                    "publishedAt": a.get("publishedAt")
                })
            return articles
        except Exception as e:
            st.warning(f"NewsAPI fetch failed: {e}")
            return []




    def sample_fallback_news(ticker: str) -> List[Dict]:
        """Return placeholder/simulated articles when NewsAPI key is missing."""
        t = ticker.split('.')[0].upper()
        return [
            {"title": f"{t} quarterly results beat estimates", "source": "ExampleNews", "description": f"{t} posted stronger-than-expected revenues this quarter.", "content": f"{t} revenue surge, market optimism", "url": "", "publishedAt": ""},
            {"title": f"Analysts cautious on {t} valuation", "source": "MarketWatch", "description": f"Valuation concerns for {t} spark debate among analysts.", "content": f"{t} high PE noted, cautious outlook", "url": "", "publishedAt": ""},
            {"title": f"Social buzz grows around {t}", "source": "Twitter", "description": f"Influencers discuss {t} and its future prospects.", "content": f"{t} trending topics show mixed sentiment", "url": "", "publishedAt": ""}
        ]

    # -------------------------
    # Sentiment analysis utils
    # -------------------------
    def analyze_text_transformers(text: str) -> Tuple[float, str]:
        """Return score 0-100 and label using HF pipeline (POSITIVE/NEGATIVE)."""
        if not text or len(text.strip()) == 0:
            return 50.0, "NEUTRAL"
        try:
            out = sentiment_pipe(text[:512])  # limit length
            label = out[0]["label"]  # POSITIVE/NEGATIVE
            score = float(out[0]["score"])
            # Map to 0-100: NEGATIVE -> 0..50, POSITIVE -> 50..100
            if label.upper().startswith("POS"):
                mapped = 50 + score * 50
                return round(mapped, 2), "POSITIVE"
            else:
                mapped = 50 - score * 50
                return round(mapped, 2), "NEGATIVE"
        except Exception:
            return 50.0, "NEUTRAL"

    def analyze_text_vader(text: str) -> Tuple[float, str]:
        """Return score 0-100 and label using VADER (compound)."""
        if not text or len(text.strip()) == 0:
            return 50.0, "NEUTRAL"
        vs = vader.polarity_scores(text)
        compound = vs["compound"]  # -1 .. +1
        mapped = 50 + compound * 50
        label = "POSITIVE" if compound >= 0.05 else ("NEGATIVE" if compound <= -0.05 else "NEUTRAL")
        return round(mapped, 2), label

    def analyze_article_sentiment(article: Dict) -> Dict:
        """Analyze single article, return article dict enriched with 'sentiment_score' and 'sentiment_label'"""
        text = " ".join([article.get("title",""), article.get("description",""), article.get("content","")])
        if SENTIMENT_ENGINE == "transformers":
            score, label = analyze_text_transformers(text)
        else:
            score, label = analyze_text_vader(text)
        article_copy = article.copy()
        article_copy["sentiment_score"] = score
        article_copy["sentiment_label"] = label
        return article_copy

    # -------------------------
    # Aggregation & normalization
    # -------------------------
    def aggregate_sentiment(articles: List[Dict]) -> Dict:
        """
        Compute per-source and total weighted sentiment.
        Output:
        - source_scores: {source: avg_score}
        - overall_score: 0-100
        - counts: totals
        """
        if not articles:
            return {"overall_score": 50.0, "source_scores": {}, "counts": 0}
        df = pd.DataFrame(articles)
        # If any article missing sentiment_score, compute now
        if "sentiment_score" not in df.columns:
            df = pd.DataFrame([analyze_article_sentiment(a) for a in articles])
        # group by source
        source_scores = df.groupby("source")["sentiment_score"].mean().to_dict()
        # compute overall as weighted mean by length of article content (proxy for importance)
        df["length"] = df["title"].fillna("").str.len() + df["description"].fillna("").str.len() + df["content"].fillna("").str.len()
        # avoid zero lengths
        df["length"] = df["length"].replace(0, 1)
        overall = np.average(df["sentiment_score"], weights=df["length"])
        return {"overall_score": round(float(overall), 2), "source_scores": {k: round(float(v),2) for k,v in source_scores.items()}, "counts": len(df)}

    # -------------------------
    # Streamlit UI
    # -------------------------
    st.title("StocksPi — Sentiment Panel")
    st.write("Analyze market/news sentiment for any stock. This panel aggregates news/social signals into a simple 0–100 sentiment score.")

    col1, col2 = st.columns([2,1])

    with col1:
        ticker = st.text_input("Enter ticker (e.g., RELIANCE.NS or AAPL)", value="RELIANCE.NS")
        st.markdown("**Sentiment engine:** " + (SENTIMENT_ENGINE or "unknown"))
        fetch_news_button = st.button("Fetch & Analyze Sentiment")

    with col2:
        st.markdown("**Data sources**")
        st.write("- NewsAPI (optional)")
        st.write("- yfinance (price fetch)")
        st.write("- HF transformers / VADER for sentiment")
        # if not NEWSAPI_KEY:
            # st.warning("No NEWSAPI_KEY found. Using fallback sample articles. Set NEWSAPI_KEY env var to enable live news.")
        # st.markdown("---")
        # st.write("Env variables (optional):")
        # st.code("NEWSAPI_KEY=your_key_here")

    if fetch_news_button:
        with st.spinner("Fetching stock info and news..."):
            # 1) get basic stock info from yfinance
            try:
                yf_t = yf.Ticker(ticker)
                info = yf_t.info
                # Some tickers may not have 'currentPrice' on all exchanges - handle gracefully
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or None
                prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or None
                name = info.get("shortName") or info.get("longName") or ticker.upper()
            except Exception:
                current_price = None
                prev_close = None
                name = ticker.upper()

            # 2) fetch news
            articles = fetch_news_via_newsapi(name, page_size=30)
            if not articles:
                articles = sample_fallback_news(ticker)

            # 3) analyze each article
            analyzed = []
            for a in articles:
                analyzed.append(analyze_article_sentiment(a))
                # small sleep to avoid hf rate limits if using transformers local model (optional)
                if use_transformers:
                    time.sleep(0.05)

            # 4) aggregate
            agg = aggregate_sentiment(analyzed)

        # -----------------------
        # Display Overview
        # -----------------------
        st.subheader(f"{name} — Market Sentiment")
        c1, c2, c3 = st.columns(3)
        c1.metric("Price", f"₹{current_price}" if current_price else "N/A", delta=(f"Prev: ₹{prev_close}" if prev_close else ""))
        c2.metric("Overall Sentiment (0-100)", agg["overall_score"])
        c3.metric("Articles analyzed", agg["counts"])

        # color-coded interpretation
        score = agg["overall_score"]
        if score >= 70:
            label = "Positive"
            emoji = "😊"
        elif score >= 50:
            label = "Neutral"
            emoji = "😐"
        else:
            label = "Negative"
            emoji = "😟"

        st.markdown(f"### Overall Market Mood: **{label} {emoji}** (Score: {score}/100)")

        # per-source bar chart
        if agg["source_scores"]:
            df_src = pd.DataFrame(list(agg["source_scores"].items()), columns=["source","score"])
            fig = px.bar(df_src, x="source", y="score", text="score", range_y=[0,100], title="Sentiment by Source")
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # pie chart of counts by sentiment label
        df_an = pd.DataFrame(analyzed)
        # bucket by label
        df_an['bucket'] = df_an['sentiment_score'].apply(lambda s: 'Positive' if s>=70 else ('Neutral' if s>=50 else 'Negative'))
        pie = df_an['bucket'].value_counts().reset_index()
        pie.columns = ['sentiment','count']
        fig2 = px.pie(pie, names='sentiment', values='count', title="Article Sentiment Distribution", color='sentiment',
                    color_discrete_map={'Positive':'#10b981','Neutral':'#f59e0b','Negative':'#ef4444'})
        st.plotly_chart(fig2, use_container_width=True)

        # table of analyzed articles
        st.markdown("### Articles & Scores")
        table_cols = ["publishedAt","source","title","sentiment_label","sentiment_score","url"]
        df_show = df_an[["publishedAt","source","title","sentiment_label","sentiment_score","url"]].fillna("")
        st.dataframe(df_show)

        # short textual explanation (Pi-ready)
        st.markdown("### Quick explanation (for Pi / UI summary)")
        expl = (f"Aggregated sentiment for {name} is {score}/100 ({label}). "
                f"The main sources show: " +
                ", ".join([f"{k}: {v}/100" for k,v in agg["source_scores"].items()]) +
                f". We analyzed {agg['counts']} articles.")
        st.info(expl)

        # copyable summary for poster
        st.markdown("### Copyable Summary (for poster / report)")
        st.code(expl)

        # option to download CSV
        csv = df_an.to_csv(index=False)
        st.download_button("Download analyzed articles CSV", csv, file_name=f"{ticker}_sentiment.csv", mime="text/csv")

    else:
        st.info("Enter a ticker and click 'Fetch & Analyze Sentiment' to begin. If you don't have a NEWSAPI_KEY, the app will use sample headlines.")


