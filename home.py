import streamlit as st
from streamlit_option_menu import option_menu




import streamlit as st
def app():
    st.set_page_config(
            page_title="Home",
            page_icon="🏠",
            layout="wide"
        )
    st.markdown("""
        <style>
        /* ==== CONTAINER ANIMATION ==== */
        .home-container {
            animation: slideFadeIn 1.2s ease-in-out;
            padding: 60px 10px;
            text-align: center;
        }

        @keyframes slideFadeIn {
            0% { opacity: 0; transform: translateY(-40px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        /* ==== GLOWING TITLE ==== */
        .home-title {
            font-size: 44px;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 6px #00ffff, 0 0 12px #00ffff, 0 0 18px #00ffff;
            animation: glowPulse 3s infinite ease-in-out;
            margin-bottom: 15px;
        }

        @keyframes glowPulse {
            0% { text-shadow: 0 0 6px #00ffff, 0 0 12px #00ffff; }
            50% { text-shadow: 0 0 14px #00ffff, 0 0 28px #00ffff; }
            100% { text-shadow: 0 0 6px #00ffff, 0 0 12px #00ffff; }
        }

        /* ==== TYPEWRITER TEXT ==== */
        .typewriter {
            color: #00ffee;
            font-size: 22px;
            font-family: monospace;
            overflow: hidden;
            white-space: nowrap;
            border-right: 2px solid #00ffee;
            width: 0;
            animation: typing 5s steps(60, end) forwards, blink .75s step-end infinite;
            margin: 10px auto 25px auto;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink {
            50% { border-color: transparent; }
        }

        /* ==== DESCRIPTION ==== */
        .home-description {
            font-size: 18px;
            color: lightgray;
            max-width: 800px;
            margin: 0 auto 20px auto;
            line-height: 1.6;
            animation: fadeInText 2s ease-in;
        }

        @keyframes fadeInText {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* ==== FLOATING ICON ==== */
        .floating-icon {
            font-size: 40px;
            animation: floatY 3s ease-in-out infinite;
            color: #00ffff;
            margin-top: 20px;
        }

        @keyframes floatY {
            0% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0); }
        }

        /* ==== BUTTON STYLE ==== */
        .custom-button {
            display: inline-block;
            margin: 15px 10px 0 10px;
            padding: 10px 20px;
            background-color: #00ffff10;
            color: #00ffff;
            border: 1px solid #00ffff;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background-color 0.3s ease;
        }

        .custom-button:hover {
            background-color: #00ffff33;
        }
        </style>

        <div class="home-container">
            <div class="home-title"></div>
            <div class="typewriter">Initializing smart market insights...</div>
            <div class="home-description">
                Welcome to StocksPI — a simple and smart platform designed to help beginners 
                understand the stock market with confidence.
                <br><br>
                With an easy-to-use interface, accurate real-time market data, 
                and the power of the PI AI Agent, StocksPI breaks down complex market concepts into clear, 
                actionable insights — making investing easier for everyone.
            </div>
            <a href="#" class="custom-button" title="Click on 📈 Stocks">🚀 Getting Started ?</a>
            <div class="floating-icon">✨</div>
        </div>
    """, unsafe_allow_html=True)



def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css(r"C:\Users\user\OneDrive\Desktop\Sector Analyzer\style.css")

animation_symbole = "💶"

st.markdown(
    f"""
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    <div class = "snowflake">{animation_symbole}</div>
    """,
    unsafe_allow_html=True
)



