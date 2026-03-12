import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
st.set_page_config(page_title="Lapzer Price Scout", layout="wide", page_icon="💻")

# Sidebar for Settings
st.sidebar.title("⚙️ Global Settings")
manual_key = st.sidebar.text_input("Serper API Key:", type="password", help="Enter your API key from serper.dev")
API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")

# --- DYNAMIC LIMITS ---
st.sidebar.subheader("🎯 Price Range Filter")
st.sidebar.write("Set these boundaries to filter out accessories or installments.")
min_p = st.sidebar.number_input("Min Price (₹)", value=1000, step=500)
max_p = st.sidebar.number_input("Max Price (₹)", value=200000, step=5000)

def extract_prices(text, low, high):
    """Extracts numerical prices that fall within the specified range."""
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
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception:
        return None

# --- MAIN UI ---
st.title("🌎 Lapzer Price Scout")
st.markdown(f"Currently filtering results between **₹{min_p:,}** and **₹{max_p:,}**")

product_name = st.text_input("Enter product name (e.g., iPhone 15, RTX 4060, Sony WH-1000XM5):", "iPhone 15")

if st.button("Scan Market Platforms"):
    if not API_KEY:
        st.error("Please enter a valid API Key in the sidebar to proceed.")
    else:
        with st.spinner(f"Scanning online retailers for {product_name}..."):
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
                        "Source": item.get('title')[:65] + "...",
                        "Price": f"₹{price:,}" if price else "Price Not Found",
                        "Link": item.get('link'),
                        "raw": price
                    })

                if prices_list:
                    # Metrics Dashboard
                    c1, c2, c3 = st.columns(3)
                    avg = sum(prices_list)//len(prices_list)
                    c1.metric("Lowest Found", f"₹{min(prices_list):,}")
                    c2.metric("Market Average", f"₹{avg:,}")
                    c3.metric("Verified Sources", len(prices_list))

                    # Visualization
                    df = pd.DataFrame(results)
                    st.subheader("📊 Price Distribution")
                    chart_df = df.dropna(subset=['raw'])
                    st.bar_chart(chart_df.set_index('Source')['raw'])
                    
                    st.subheader("📋 Detailed Comparison Table")
                    st.dataframe(df.drop(columns=['raw']), use_container_width=True)
                else:
                    st.warning("No valid prices found within your selected range. Try adjusting the Min/Max filters.")
            else:
                st.error("Unable to fetch data. Please check your API key or network connection.")

st.info("💡 **Pro-Tip:** For budget items like mice or keyboards, set the 'Min Price' to ₹500 for better results.")
