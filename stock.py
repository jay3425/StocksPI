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
from alpha_vantage.fundamentaldata import FundamentalData
from views import data
from views import prediction
from views import visuals
def app():
    st.set_page_config(
            page_title="Stock Related Data",
            page_icon="📈",
            layout="wide"
        )
    
    dat,predict,visual = st.tabs(["Real Time Data","Prediction","Visuals"])

    with dat:
        data.app()

    with predict:
        prediction.app()

    with visual:
        visuals.app()


                

    



