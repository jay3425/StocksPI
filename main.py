import streamlit as st
from streamlit_option_menu import option_menu

st.logo(r"\Sector Ana 2 - Copy\2.png")

st.markdown("""
    <style>
    /* Container Fade & Slide */
    .intro-container {
        animation: fadeSlide 1.8s ease-in-out;
        text-align: center;
        padding: 40px 0 20px 0;
    }

    @keyframes fadeSlide {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Glowing Title */
    .glow-title {
        font-size: 40px;
        font-weight: bold;
        color: #00ffff;
        text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff;
        animation: pulse 2s infinite ease-in-out;
        margin-bottom: 10px;
    }

    @keyframes pulse {
        0% { text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff; }
        50% { text-shadow: 0 0 15px #00ffff, 0 0 30px #00ffff; }
        100% { text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff; }
    }

    /* Subtitle Fade */
    .intro-subtitle {
        font-size: 20px;
        color: lightgray;
        animation: fadeInSubtitle 2.5s ease-in;
    }

    @keyframes fadeInSubtitle {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>

    <div class="intro-container">
        <div class="glow-title">📈 StocksPI</div>
        <div class="intro-subtitle">Real-time tracking | Prediction engine | Sentiment</div>
    </div>
""", unsafe_allow_html=True)





# Import pages
import stock
import sentiment
import sector
import home

selected = option_menu(
    menu_title=None,
    options=["Home","Stock","Sentiment","Pi"],
    icons=["house", "graph-up", "bar-chart-line","grid"],
    menu_icon=None,
    default_index=0,
    orientation="horizontal",
    styles={
        "container":{"background-color":"#091019"
                     ,"border": "2px solid #00ffff"
                     },
        "icon":{"color":"#00ffff"},
        "nav-link":{
            "text-align":"center",
            "color":"lightgray",
            "--hover-color":"#0b182a",},
        "nav-link-selected":{
            "background-color":"#091019",
             "color":"#00ffff"
             ,"border": "2px solid #00ffff",
             "box-shadow": "0 0 8px #00ffff",
             },
            }

  
)

if selected == "Stock":
    stock.app()
elif selected == "Sentiment":
    sentiment.app()
elif selected == "Pi":
    sector.app()
elif selected == "Home":
    home.app()

