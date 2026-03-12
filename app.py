import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- SECURITY & CONFIG ---
# 1. Tries to load from a .env file if it exists
load_dotenv()

# 2. Priority: Manual User Input > Environment Variable
st.sidebar.title("🔐 Security Settings")
manual_key = st.sidebar.text_input("Enter Serper API Key:", type="password", help="Get a free key at serper.dev")

# Determine which API key to use
API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")

def extract_prices(text):
    """Filters out EMIs and small numbers to find real laptop prices."""
    found = re.findall(r'(?:₹|Rs\.?|Price:?)\s?(\d{1,3}(?:,\d{2,3})+)', text, re.IGNORECASE)
    valid_prices = []
    for p in found:
        val = int(p.replace(',', ''))
        # Logical filter for the Indian Gaming Laptop market
        if 45000 <= val <= 115000:
            valid_prices.append(val)
    return valid_prices

def get_live_data(query):
    """Fetches real-time search results from Google."""
    if not API_KEY:
        st.error("Missing API Key! Please enter it in the sidebar or set an environment variable.")
        return None
    
    url = "https://google.serper.dev/search"
    payload = {"q": f"{query} price in India amazon flipkart", "gl": "in"}
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Network Error: {e}")
        return None

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Market Intelligence", layout="wide", page_icon="💻")
st.title("🚀 AI Market Intelligence Scout")
st.markdown("Automated Price Analysis & Scam Detection for the Indian Tech Market.")

query = st.text_input("What product are we tracking today?", "Acer ALG")

if st.button("Deep Scan Market"):
    if not API_KEY:
        st.warning("⚠️ You need an API Key to run this. Please add it in the sidebar.")
    else:
        with st.spinner(f"Scanning Google for {query}..."):
            data = get_live_data(query)
            market_results = []
            all_prices = []

            if data and 'organic' in data:
                for result in data['organic']:
                    combined_text = result.get('title', '') + " " + result.get('snippet', '')
                    prices = extract_prices(combined_text)
                    
                    best_price = min(prices) if prices else None
                    if best_price:
                        all_prices.append(best_price)
                    
                    market_results.append({
                        "Source": result.get('title'),
                        "Detected Price": f"₹{best_price:,}" if best_price else "No Price Found",
                        "Link": result.get('link'),
                        "raw_price": best_price
                    })

                # --- DASHBOARD METRICS ---
                if all_prices:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Lowest Market Price", f"₹{min(all_prices):,}")
                    c2.metric("Market Average", f"₹{sum(all_prices)//len(all_prices):,}")
                    c3.metric("Reliability Score", f"{len(all_prices)} Sources Found")

                    df = pd.DataFrame(market_results)
                    
                    st.subheader("📉 Price Visualization")
                    chart_df = df.dropna(subset=['raw_price'])
                    st.bar_chart(chart_df.set_index('Source')['raw_price'])
                    
                    st.subheader("📊 Full Comparison Table")
                    st.dataframe(df.drop(columns=['raw_price']), use_container_width=True)
                else:
                    st.info("Results found, but no realistic prices (₹45k+) were detected in the snippets.")
            else:
                st.error("No data received from the search engine.")

st.sidebar.divider()
st.sidebar.info("""
**How to use:**
1. Get a free key at [Serper.dev](https://serper.dev)
2. Paste it in the box above.
3. Search for any product!
""")
