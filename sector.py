import streamlit as st
from groq import Groq
import os

    # -----------------------------
    # SETUP
    # -----------------------------
def app():
    import streamlit as st
    from openai import OpenAI

    # -----------------------------
    # SETUP
    # -----------------------------
    

        # ---------------------------------------------------------
        # STREAMLIT PAGE CONFIG
        # ---------------------------------------------------------
    st.set_page_config(
            page_title="Pi - StocksPi Assistant",
            page_icon="🤖",
            layout="wide"
        )

        # ---------------------------------------------------------
        # API KEY (SECURE)
        # ---------------------------------------------------------
        # Put your key in .streamlit/secrets.toml
        # OPENAI_API_KEY = "sk-xxxx"

    # client = OpenAI(api_key="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")
    client = Groq(api_key="Put Your Groq API Key")
        # ---------------------------------------------------------
        # PI SYSTEM PROMPT
        # ---------------------------------------------------------
    PI_SYSTEM_PROMPT = PI_SYSTEM_PROMPT = """
You are Pi — an AI stock analysis and suggestion assistant inside the StocksPi platform.

Your role:
- Analyze stock charts, indicators, volume, tabular values, sentiment, predictions, and provided news context.
- Provide market-oriented, educational suggestions that help users understand whether current conditions appear favorable or unfavorable.

Analysis responsibilities:
1. News-aware reasoning:
   - If news, earnings, sector updates, or events are mentioned, explain how they may have influenced price or volume.
   - Clearly connect news → market reaction when possible.

2. Market stance labeling:
   - Classify the current setup as one of:
     Bullish / Neutral / Bearish
   - Explain briefly why this label fits, based on data.

3. Confidence meter:
   - Assign a confidence level: Low / Medium / High
   - Confidence reflects alignment of signals (trend, volume, momentum, news), NOT certainty.

4. Why-price-moved explanation:
   - Explain recent price movement using:
     trend direction,
     volume behavior,
     indicator position,
     and any available news or sentiment.

5. Time-frame based perspective:
   - Short-term view (days to weeks): focus on momentum, volume, recent signals.
   - Long-term view (months): focus on trend stability, structure, and consistency.
   - Clearly separate short-term vs long-term observations.

Guided suggestion rules:
- You MAY provide conditional, educational suggestions.
- Use phrases like:
  “based on current signals”,
  “this setup is often viewed as”,
  “from a short-term perspective”,
  “conditions appear supportive / mixed / weak”.
- Do NOT give direct buy/sell/hold instructions.
- Do NOT guarantee outcomes.

Style:
- Clear, confident, and practical (not academic).
- Beginner-friendly but insightful.
- Keep responses under 150 words unless asked for deep analysis.
- Use short sections or bullet points when helpful.

End every response with a short disclaimer:
“This interpretation is for learning purposes, and market conditions can change.”

Great question — and you’re thinking about this **exactly the right way** 👍
Short answer first:

👉 **YES, PI can handle sentiment, reports, and other sections — that line was just ONE example.**

Let me explain clearly and safely.

---

## 🧠 How PI Actually Works (Conceptually)

PI has **two roles** inside StocksPI:

### 1️⃣ **Market & Sentiment Assistant**

PI already:

* explains **sentiment results**
* answers **stock-related questions**
* gives **educational interpretations**
* explains **why sentiment is positive / neutral / negative**

That part is already covered by:

> *Analyze sentiment, predictions, tabular values, and news context*

---

### 2️⃣ **Platform Guide (UI Navigation Assistant)**

The sentence

> *“Select the Stocks option, enter the stock name…”*

is **just an example**, not a limitation.

PI should:

* explain **where to view sentiment**
* explain **where to view reports**
* explain **how to use each feature**
* guide beginners step-by-step

---

**Platform navigation assistance:**

* If a user asks how to view any feature (stock data, sentiment reports, CSV outputs, or analysis), explain the relevant steps within the StocksPI interface.
* Guide users based on the section they are asking about, such as *Stocks*, *Sentiment*, or *Reports*.
* Use clear, step-by-step, beginner-friendly instructions.
* Only describe features and navigation options that exist in the StocksPI platform.
* Do not mention help buttons, advanced financial sections, or features not explicitly available.
* If a feature is unavailable, explain the closest available alternative instead.
When a user asks how to view stock data, sentiment results, or reports, provide only the steps that exist in the StocksPI platform.

Do not mention login, account creation, help buttons, stock detail pages, or advanced sections.

Guide users using simple, step-by-step instructions such as:
“Select the Stocks option, enter the stock name in the textbox, and press the submit button.”

If the user asks about sentiment reports, instruct them to navigate to the Reports section where CSV-based sentiment outputs are available.

Keep instructions short, clear, and beginner-friendly.

If a requested feature is not available, explain that it is not currently supported instead of inventing functionality.

Do not mention or rely on technical indicators (such as RSI, MACD, moving averages, or oscillators).

Do not provide intraday or short-term trading analysis.

Avoid references to time-frame-based trading (intraday, scalping, or live market signals).

Base explanations only on available sentiment results and basic stock information provided by the system.

If asked about indicators or intraday analysis, clearly state that these features are not supported in the current version of StocksPI.
* Examples include:

  * Viewing stock data
  * Checking sentiment results
  * Accessing saved CSV sentiment reports

"""


        # ---------------------------------------------------------
        # UI HEADER
        # ---------------------------------------------------------
    st.title("🤖 Pi — StocksPi AI Assistant")
    st.write("Ask anything about stocks, market sentiment, predictions, or concepts.")

        # ---------------------------------------------------------
        # INPUTS
        # ---------------------------------------------------------
    ticker = st.text_input("Stock Ticker (optional)", placeholder="e.g., RELIANCE.NS")
    prediction = st.text_input("Next-Day Prediction (optional)", placeholder="e.g., Possible upward movement")
    sentiment = st.text_input("Sentiment Result (optional)", placeholder="e.g., Positive (72/100)")
    summary = st.text_area("Stock Summary (optional)", placeholder="Short 1–2 line summary of this stock...")

    user_msg = st.text_area("Your Question to Pi", placeholder="Type your message here...", height=120)

    submit = st.button("Ask Pi")

        # ---------------------------------------------------------
        # ASK PI FUNCTION
        # ---------------------------------------------------------
    def ask_pi(user_message, ticker, prediction, sentiment, summary):

            # Build context
            context = ""
            if ticker:
                context += f"\nTicker: {ticker}"
            if prediction:
                context += f"\nPrediction: {prediction}"
            if sentiment:
                context += f"\nSentiment: {sentiment}"
            if summary:
                context += f"\nSummary: {summary}"

            # Final user message with context
            final_user_prompt = f"""
    Context from StocksPi:
    {context}

    User Question:
    {user_message}
    """

            # OpenAI Chat Completion
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                # model="gpt-4o-mini", 
                   # fast + cheap + perfect for chatbots
                messages=[
                    {"role": "system", "content": PI_SYSTEM_PROMPT},
                    {"role": "user", "content": final_user_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            return response.choices[0].message.content

        # ---------------------------------------------------------
        # MAIN ACTION
        # ---------------------------------------------------------
    if submit:
            if user_msg.strip() == "":
                st.warning("Please type a message.")
            else:
                with st.spinner("Pi is thinking..."):
                    reply_text = ask_pi(user_msg, ticker, prediction, sentiment, summary)

                st.success("Pi's Response:")
                st.write(reply_text)




    # import streamlit as st
    # from groq import Groq
    # import os

    # # ---------------------------------------------------------
    # # STREAMLIT PAGE CONFIG
    # # ---------------------------------------------------------
    # st.set_page_config(
    #     page_title="Pi - StocksPi Assistant",
    #     page_icon="🤖",
    #     layout="wide"
    # )

    # # ---------------------------------------------------------
    # # API KEY
    # # ---------------------------------------------------------
    # # GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")
    # client = Groq(api_key="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")

    # # ---------------------------------------------------------
    # # PI SYSTEM PROMPT
    # # ---------------------------------------------------------
    # PI_SYSTEM_PROMPT = """
    # You are Pi — an AI financial learning tutor inside the StocksPi platform.
    # Your goal is to EXPLAIN the stock market to beginners.

    # Guidelines:
    # - Use simple, beginner-friendly language.
    # - Break down concepts using small examples.
    # - If user asks about decisions, explain the logic + add a small disclaimer.
    # - When context (ticker, prediction, sentiment, summary) is provided, include it briefly.
    # - Keep replies under 150 words.
    # - never use recommendations word.
    # """

    # # ---------------------------------------------------------
    # # UI HEADER
    # # ---------------------------------------------------------
    # st.title("🤖 Pi — StocksPi AI Assistant")
    # st.write("Ask anything about stocks, market sentiment, predictions, or concepts.")

    # # ---------------------------------------------------------
    # # INPUTS
    # # ---------------------------------------------------------
    # ticker = st.text_input("Stock Ticker (optional)", placeholder="e.g., RELIANCE.NS")
    # prediction = st.text_input("Next-Day Prediction (optional)", placeholder="e.g., Possible upward movement")
    # sentiment = st.text_input("Sentiment Result (optional)", placeholder="e.g., Positive (72/100)")
    # summary = st.text_area("Stock Summary (optional)", placeholder="Short 1–2 line summary of this stock...")

    # user_msg = st.text_area("Your Question to Pi", placeholder="Type your message here...", height=120)

    # submit = st.button("Ask Pi")

    # # ---------------------------------------------------------
    # # ASK PI FUNCTION
    # # ---------------------------------------------------------
    # def ask_pi(user_message, ticker, prediction, sentiment, summary):

    #     # Build context
    #     context = ""
    #     if ticker:
    #         context += f"\nTicker: {ticker}"
    #     if prediction:
    #         context += f"\nPrediction: {prediction}"
    #     if sentiment:
    #         context += f"\nSentiment: {sentiment}"
    #     if summary:
    #         context += f"\nSummary: {summary}"

    #     # Final combined prompt
    #     final_prompt = f"""
    # {PI_SYSTEM_PROMPT}

    # Context from StocksPi:
    # {context}

    # User Question:
    # {user_message}
    # """

    #     # Call Groq LLM
    #     response = client.chat.completions.create(
    #         model="llama-3.1-8b-instant",   # ✅ best for chatbot
    #         messages=[
    #             {"role": "system", "content": PI_SYSTEM_PROMPT},
    #             {"role": "user", "content": final_prompt}
    #         ],
    #         max_tokens=350,
    #         temperature=0.3,
    #     )

    #     # ✅ FIXED RETURN (Groq’s new format)
    #     return response.choices[0].message.content


    # # ---------------------------------------------------------
    # # MAIN ACTION
    # # ---------------------------------------------------------
    # if submit:
    #     if user_msg.strip() == "":
    #         st.warning("Please type a message.")
    #     else:
    #         with st.spinner("Pi is thinking..."):
    #             reply_text = ask_pi(user_msg, ticker, prediction, sentiment, summary)

    #         st.success("Pi's Response:")
    #         st.write(reply_text)

















# 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
