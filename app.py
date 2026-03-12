import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- PAGE CONFIG ---
load_dotenv()

# Dual Logo Paths
TAB_ICON = "assets/logo.png"     # Only icon for browser tab
SIDEBAR_LOGO = "assets/logo1.png" # Icon + Text for sidebar

st.set_page_config(
    page_title="Lapzer | Market Scout",
    page_icon=TAB_ICON if os.path.exists(TAB_ICON) else "💻",
    layout="wide"
)

# --- PREMIUM GHOST CSS ---
st.markdown("""
    <style>
    /* Hide Streamlit Header (GitHub Icon & Menu) */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Global Background & Text */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Sidebar Modern Look */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Padding for Sidebar Logo */
    [data-testid="stSidebarNav"] {
        padding-top: 1.5rem;
    }

    /* Green Scouting Button */
    div.stButton > button {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
        border: none;
        padding: 10px;
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #2ea043;
        box-shadow: 0px 4px 15px rgba(46, 160, 67, 0.3);
    }

    /* Metric Visuals */
    [data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-family: 'SF Mono', monospace;
    }

    /* Input Field Styling */
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR BRANDING ---
with st.sidebar:
    # Sidebar mein Icon + Text wala logo
    if os.path.exists(SIDEBAR_LOGO):
        st.image(SIDEBAR_LOGO, use_container_width=True)
    else:
        st.title("🛡️ LAPZER")
        
    st.markdown("---")
    
    # Secure API Input
    manual_key = st.text_input("Serper API Key", type="password", placeholder="Paste secret key...")
    API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")
    
    st.markdown("---")
    st.subheader("🎯 Price Filters")
    col_min, col_max = st.columns(2)
    with col_min:
        min_p = st.number_input("Min (₹)", value=1000, step=500)
    with col_max:
        max_p = st.number_input("Max (₹)", value=200000, step=5000)

# --- ANALYSIS LOGIC ---
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
    if not API_KEY: return None
    url = "https://google.serper.dev/search"
    payload = {"q": f"{query} price in India official store amazon flipkart", "gl": "in"}
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except: return None

# --- MAIN INTERFACE ---
st.title("🌎 Market Intelligence Scout")
st.markdown(f"**Scanning Range:** ₹{min_p:,} — ₹{max_p:,}")

query = st.text_input("Enter product name for real-time analysis:", placeholder="e.g. MacBook Air M3")

if st.button("Start Market Analysis"):
    if not API_KEY:
        st.warning("⚠️ API Key is missing in the control panel.")
    elif not query:
        st.warning("⚠️ Enter a product name to begin.")
    else:
        with st.spinner(f"Scanning retailers for '{query}'..."):
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
                    # Metrics Display
                    m1, m2, m3 = st.columns(3)
                    avg_price = sum(prices_list) // len(prices_list)
                    m1.metric("Lowest Found", f"₹{min(prices_list):,}")
                    m2.metric("Market Average", f"₹{avg_price:,}")
                    m3.metric("Data Points", len(prices_list))

                    st.markdown("---")
                    df = pd.DataFrame(results)
                    
                    # Analysis Graph
                    st.subheader("📊 Price Distribution")
                    st.bar_chart(df.set_index("Retailer")["sort_val"])

                    # Comparative Table
                    st.subheader("📋 Comparative Analysis")
                    st.dataframe(df.drop(columns=["sort_val"]), use_container_width=True)
                else:
                    st.error("No valid prices detected in this range.")
            else:
                st.error("Market scan failed. Check API Key.")

# CUSTOM FOOTER
st.markdown("---")
st.markdown("<div style='text-align: center; color: #8b949e; font-size: 0.8rem;'>© 2026 LAPZER ANALYTICS | Proprietary Scout Interface</div>", unsafe_allow_html=True)
