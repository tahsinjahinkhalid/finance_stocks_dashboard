# import modules
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from streamlit_option_menu import option_menu

from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

st.set_page_config(layout="wide",
                   page_title="Finance Stocks Web App",
                   page_icon=":chart_with_upwards_trend:")

# add title
st.title("Finance Stock Dashboard")
st.subheader("By: Tahsin Jahin Khalid")

# add sidebar selectors
ticker = st.sidebar.selectbox("Ticker", options=["AAPL", "MSFT", "GOOGL",
                                                 "GOOG", "AMZN", "NVDA",
                                                 "TSLA", "META"])
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

data = yf.download(ticker,
                   start=str(start_date),
                   end=str(end_date))


def add_chart():
    fig = px.line(data,
                  x=data.index, y=data["Adj Close"],
                  title=ticker)
    st.plotly_chart(fig)


def price_movements():
    pricing_data, fundamental_data = st.tabs(
        ["Pricing Data",
         "Fundamental Data"])
    
    with pricing_data:
        # st.write("A")
        data2 = data
        data2["% Change"] = data["Adj Close"] / data["Adj Close"].shift(1) - 1 
        data2.dropna(inplace=True)
        st.dataframe(data2)

        annual_return = data2["% Change"].mean() * 252 * 100
        st.markdown(f"**Annual Return is {np.round(annual_return, 2)}%**")
        stdev = np.std(data2["% Change"]) * np.sqrt(252)
        st.markdown(f"**Standard Deviation is {np.round(stdev, 2)}%**")
        st.markdown(f"**Risk Adj. Return is {np.round(annual_return/(stdev * 100), 2)}**")

    with fundamental_data:
        # st.write("B")
        try:
            key = st.secrets["av_key"]
            fd = FundamentalData(key, 
                                output_format = "pandas")
            # balance sheet
            st.subheader("Balance Sheet")
            balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
            bs = balance_sheet.T[2:]
            bs.columns = list(
                balance_sheet.T.iloc[0])
            st.write(balance_sheet)
        except Exception as e:
            st.write(e)
        # income statement
        try:
            st.subheader("Income Statement")
            income_statement = fd.get_income_statement_annual(ticker)[0]
            is1 = income_statement.T[2:]
            is1.columns = list(
                income_statement.T.iloc[0])
            st.write(is1)
        except Exception as e:
            st.write(e)
        # cash flow statement
        try:
            st.subheader("Cash Flow Statement")
            cash_flow = fd.get_cash_flow_annual(ticker)[0]
            cf = cash_flow.T[2:]
            cf.columns = list(
                cash_flow.T.iloc[0])
            st.write(cf)
        except Exception as e:
            st.write(e)


def show_news():
    st.header(f"News of {ticker}")
    sn = StockNews(ticker,
                   save_news=False)
    df_news = sn.read_rss()
    for i in range(5):
        st.subheader(f"News {i + 1}")
        st.write(df_news["published"][i])
        st.write(df_news["title"][i])
        st.write(df_news["summary"][i])

        title_sentiment = df_news["sentiment_title"][i]
        st.write(f"Title Sentiment: {np.round(title_sentiment, 2)}")
        news_sentiment = df_news["sentiment_summary"][i]
        st.write(f"News Sentiment: {np.round(news_sentiment, 2)}")


selected = option_menu("Explore Web App",
                       ["Chart", "Price Movements", "Stock News"], 
                       menu_icon="cast", 
                       default_index=1)

if selected == "Chart":
    # st.write("Chart")
    add_chart()
elif selected == "Price Movements":
    # st.write("Price Movements")
    price_movements()
else:
    show_news()
