import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- PAGE CONFIG ---
load_dotenv()
st.set_page_config(
    page_title="Lapzer | Market Scout",
    # *** Pointing to the clean icon image (Image 1) ***
    page_icon="assets/logo1.png", 
    layout="wide"
)

# --- CUSTOM CSS (GHOST MODE) ---
st.markdown("""
    <style>
    /* Hide Streamlit Header (GitHub Icon & Menu) */
    header {visibility: hidden;}
    
    /* Hide Streamlit Footer */
    footer {visibility: hidden;}
    
    /* Main App Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Center the logo in sidebar */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }

    /* Button Styling */
    div.stButton > button {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #2ea043;
        border-color: #8b949e;
    }

    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-family: 'SF Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    # *** Showing the minimalist icon in the sidebar (Image 1) ***
    st.image("assets/logo1.png", use_container_width=True)
    # The 'st.title("LAPZER")' line is removed to keep it clean, as requested.
    st.markdown("---")
    
    manual_key = st.text_input("Serper API Key", type="password")
    API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")
    
    st.markdown("---")
    st.subheader("🎯 Price Filters")
    col_min, col_max = st.columns(2)
    with col_min:
        min_p = st.number_input("Min (₹)", value=1000, step=500)
    with col_max:
        max_p = st.number_input("Max (₹)", value=200000, step=5000)

# --- LOGIC FUNCTIONS ---
def extract_prices(text, low, high):
    pattern = r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{2,3})+)'
    found = re.findall(pattern, text, re.IGNORECASE)
    valid_prices = []
    for p in found:
        val = int(p.replace(',', ''))
        if low <= val <= high:
            valid_prices.append(val)
    return valid_prices

def fetch_market_data(query):
    if not API_KEY:
        return None
    
    url = "https://google.serper.dev/search"
    payload = {
        "q": f"{query} price in India official store amazon flipkart",
        "gl": "in",
        "num": 10
    }
    headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except:
        return None

# --- MAIN INTERFACE ---
st.title("🌎 Market Intelligence Scout")
st.markdown(f"Analysis Range: **₹{min_p:,} — ₹{max_p:,}**")

query = st.text_input("Enter tech product for analysis:", placeholder="e.g. PlayStation 5 Slim")

if st.button("Generate Market Analysis"):
    if not API_KEY:
        st.warning("⚠️ API Key missing in Control Panel.")
    elif not query:
        st.warning("⚠️ Please enter a product name.")
    else:
        with st.spinner(f"Scanning online retailers for '{query}'..."):
            data = fetch_market_data(query)
            
            results = []
            prices_list = []

            if data and 'organic' in data:
                for item in data['organic']:
                    content = f"{item.get('title', '')} {item.get('snippet', '')}"
                    found_prices = extract_prices(content, min_p, max_p)
                    
                    price = min(found_prices) if found_prices else None
                    
                    if price:
                        prices_list.append(price)
                        results.append({
                            "Retailer": item.get('title')[:60] + "...",
                            "Price": f"₹{price:,}",
                            "Action": item.get('link'),
                            "sort_val": price
                        })

                if prices_list:
                    m1, m2, m3 = st.columns(3)
                    avg_price = sum(prices_list) // len(prices_list)
                    
                    m1.metric("Lowest Found", f"₹{min(prices_list):,}")
                    m2.metric("Market Average", f"₹{avg_price:,}")
                    m3.metric("Data Points", len(prices_list))

                    st.markdown("---")
                    df = pd.DataFrame(results)
                    
                    st.subheader("📊 Price Distribution Graph")
                    st.bar_chart(df.set_index("Retailer")["sort_val"])

                    st.subheader("📋 Comparative Data Table")
                    st.dataframe(
                        df.drop(columns=["sort_val"]), 
                        use_container_width=True
                    )
                else:
                    st.error("No valid prices found within your selected range.")
            else:
                st.error("Unable to fetch data. Check your API Key or connection.")

# CUSTOM FOOTER
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8b949e; font-size: 0.8rem;'>"
    "© 2026 LAPZER ANALYTICS | Proprietary Intelligence Tool"
    "</div>", 
    unsafe_allow_html=True
)
