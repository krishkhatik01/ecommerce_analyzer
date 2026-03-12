import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
st.set_page_config(page_title="Universal Market Scout", layout="wide")

# Sidebar for Settings
st.sidebar.title("⚙️ Global Settings")
manual_key = st.sidebar.text_input("Serper API Key:", type="password")
API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")

# --- DYNAMIC LIMITS ---
st.sidebar.subheader("🎯 Price Range Filter")
st.sidebar.write("Set these based on what you are searching for.")
min_p = st.sidebar.number_input("Min Price (₹)", value=1000, step=500)
max_p = st.sidebar.number_input("Max Price (₹)", value=200000, step=5000)

def extract_prices(text, low, high):
    """Extracts prices that fall within the user-defined range."""
    found = re.findall(r'(?:₹|Rs\.?|Price:?)\s?(\d{1,3}(?:,\d{2,3})+)', text, re.IGNORECASE)
    valid_prices = []
    for p in found:
        val = int(p.replace(',', ''))
        if low <= val <= high:
            valid_prices.append(val)
    return valid_prices

def get_data(query):
    if not API_KEY: return None
    url = "https://google.serper.dev/search"
    payload = {"q": f"{query} price in India amazon flipkart", "gl": "in"}
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, json=payload).json()

# --- MAIN UI ---
st.title("🌎 Universal Tech Market Scout")
st.markdown(f"Currently searching with a filter of **₹{min_p:,} to ₹{max_p:,}**")

product_name = st.text_input("Enter any product (Phone, Watch, GPU, etc.):", "iPhone 15")

if st.button("Scan All Platforms"):
    if not API_KEY:
        st.error("Bhai, API Key toh daal do sidebar mein!")
    else:
        with st.spinner(f"Searching for {product_name}..."):
            data = get_data(product_name)
            results = []
            prices_list = []

            if data and 'organic' in data:
                for item in data['organic']:
                    txt = item.get('title', '') + " " + item.get('snippet', '')
                    found_prices = extract_prices(txt, min_p, max_p)
                    
                    price = min(found_prices) if found_prices else None
                    if price: prices_list.append(price)
                    
                    results.append({
                        "Platform/Source": item.get('title')[:60] + "...",
                        "Price": f"₹{price:,}" if price else "N/A",
                        "Link": item.get('link'),
                        "raw": price
                    })

                if prices_list:
                    # Metrics
                    c1, c2, c3 = st.columns(3)
                    avg = sum(prices_list)//len(prices_list)
                    c1.metric("Lowest Price", f"₹{min(prices_list):,}")
                    c2.metric("Market Average", f"₹{avg:,}")
                    c3.metric("Total Listings", len(prices_list))

                    # Chart & Table
                    df = pd.DataFrame(results)
                    st.bar_chart(df.dropna(subset=['raw']).set_index('Platform/Source')['raw'])
                    st.dataframe(df.drop(columns=['raw']), use_container_width=True)
                else:
                    st.warning("Koi price nahi mila. Side bar mein 'Price Range' check karo!")

st.info("💡 Tip: Agar product sasta hai (jaise Mouse), toh Min Price ko 500 kar do.")
