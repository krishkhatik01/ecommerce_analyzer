import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- PAGE CONFIG ---
load_dotenv()

# Dual Logo Paths (Transparent PNGs)
TAB_ICON = "assets/logo.png"     # Only icon
SIDEBAR_LOGO = "assets/logo1.png" # Icon + Text

st.set_page_config(
    page_title="Lapzer | Market Scout",
    # Agar logo.png transparent hai toh ye browser tab mein chamkega
    page_icon=TAB_ICON if os.path.exists(TAB_ICON) else "🟢",
    layout="wide"
)

# --- MODERN DARK CSS ---
st.markdown("""
    <style>
    /* Hide Default Headers */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Background */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0d12;
        border-right: 1px solid #30363d;
    }

    /* Padding for Transparent Logo */
    [data-testid="stSidebarNav"] {
        padding-top: 1.5rem;
    }

    /* Scouting Button (Neon Green Feel) */
    div.stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border-radius: 8px;
        font-weight: 700;
        border: none;
        height: 3em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.2);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 160, 67, 0.4);
        color: white;
    }

    /* Metric Visuals */
    [data-testid="stMetricValue"] {
        color: #3fb950 !important;
        font-family: 'SF Mono', monospace;
    }

    /* Input Field Customization */
    .stTextInput input {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR BRANDING ---
with st.sidebar:
    # Sidebar Logo display
    if os.path.exists(SIDEBAR_LOGO):
        st.image(SIDEBAR_LOGO, use_container_width=True)
    else:
        st.title("🟢 LAPZER")
        
    st.markdown("---")
    
    # API Key Handling
    manual_key = st.text_input("Serper API Key", type="password", placeholder="Enter your key...")
    API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")
    
    st.markdown("---")
    st.subheader("🎯 Price Filters")
    col1, col2 = st.columns(2)
    with col1:
        min_p = st.number_input("Min (₹)", value=1000, step=500)
    with col2:
        max_p = st.number_input("Max (₹)", value=200000, step=5000)

# --- ENGINE FUNCTIONS ---
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

# --- MAIN UI ---
st.title("🌎 Market Intelligence Scout")
st.markdown(f"**Scanning Range:** ₹{min_p:,} — ₹{max_p:,}")

query = st.text_input("Search product for real-time market data:", placeholder="e.g. SONY PlayStation 5")

if st.button("Start Market Analysis"):
    if not API_KEY:
        st.warning("⚠️ Please provide an API Key in the sidebar.")
    elif not query:
        st.warning("⚠️ Enter a product name.")
    else:
        with st.spinner(f"Scouting retailers for '{query}'..."):
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
                    # Summary Stats
                    m1, m2, m3 = st.columns(3)
                    avg_price = sum(prices_list) // len(prices_list)
                    m1.metric("Lowest Found", f"₹{min(prices_list):,}")
                    m2.metric("Market Average", f"₹{avg_price:,}")
                    m3.metric("Data Points", len(prices_list))

                    st.markdown("---")
                    df = pd.DataFrame(results)
                    
                    # Visualization
                    st.subheader("📊 Price Distribution Graph")
                    st.bar_chart(df.set_index("Retailer")["sort_val"])

                    # Table
                    st.subheader("📋 Detailed Comparison")
                    st.dataframe(df.drop(columns=["sort_val"]), use_container_width=True)
                else:
                    st.error("No valid prices detected. Adjust your filters and try again.")
            else:
                st.error("Scan failed. Verify your Serper API Key.")

# FOOTER
st.markdown("---")
st.markdown("<div style='text-align: center; color: #8b949e; font-size: 0.8rem;'>© 2026 LAPZER ANALYTICS | Intelligence Scout Interface</div>", unsafe_allow_html=True)
