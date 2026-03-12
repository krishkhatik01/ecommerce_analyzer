import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- PAGE CONFIG ---
load_dotenv()

# Dual Logo Paths
TAB_ICON = "assets/logo.png"     
SIDEBAR_LOGO = "assets/logo1.png" 

st.set_page_config(
    page_title="Lapzer | Market Scout",
    page_icon="🟢", # High visibility neon dot for browser tab
    layout="wide"
    initial_sidebar_state="expanded"
)

# --- ELITE UI CUSTOMIZATION (CSS) ---
st.markdown("""
    <style>
    /* Hide Default Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Background & Text Color */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0d12;
        border-right: 1px solid #30363d;
    }

    /* Professional Header Styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#ffffff, #3fb950);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }

    /* Custom Button Look */
    div.stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white !important;
        border-radius: 6px;
        font-weight: 600;
        border: none;
        height: 3em;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(46, 160, 67, 0.4);
    }

    /* Metric Visualization */
    [data-testid="stMetricValue"] {
        color: #3fb950 !important;
        font-family: 'SF Mono', 'Roboto Mono', monospace;
    }

    /* Card-like Dataframe Styling */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR BRANDING ---
with st.sidebar:
    if os.path.exists(SIDEBAR_LOGO):
        st.image(SIDEBAR_LOGO, use_container_width=True)
    else:
        st.title("🟢 LAPZER")
        
    st.markdown("---")
    
    # API Key Input
    manual_key = st.text_input("Serper API Key", type="password", placeholder="Enter key...")
    API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")
    
    st.markdown("---")
    st.subheader("🎯 Intelligence Filters")
    c1, c2 = st.columns(2)
    with c1:
        min_p = st.number_input("Min (₹)", value=1000, step=500)
    with c2:
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

# --- MAIN INTERFACE ---
# Replacing cheap earth icon with Premium Typography
st.markdown('<h1 class="main-header">LAPZER MARKET SCOUT</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #8b949e; margin-top: -10px; font-size: 1.1rem;'>Strategic Retail Intelligence & Real-time Price Tracking</p>", unsafe_allow_html=True)

st.markdown(f"**Status:** `Operational` | **Range:** `₹{min_p:,}` — `₹{max_p:,}`")

query = st.text_input("Search product for cross-platform analysis:", placeholder="e.g. SONY PlayStation 5")

if st.button("Start Scouting"):
    if not API_KEY:
        st.warning("⚠️ Access Denied: Serper API Key required.")
    elif not query:
        st.warning("⚠️ Input Error: Enter a product name.")
    else:
        with st.spinner(f"Intercepting market data for '{query}'..."):
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
                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    avg_price = sum(prices_list) // len(prices_list)
                    m1.metric("Lowest Market Price", f"₹{min(prices_list):,}")
                    m2.metric("Market Average", f"₹{avg_price:,}")
                    m3.metric("Data Points", len(prices_list))

                    st.markdown("---")
                    df = pd.DataFrame(results)
                    
                    # Charting
                    st.subheader("📊 Price Distribution")
                    st.bar_chart(df.set_index("Retailer")["sort_val"])

                    # Data Table
                    st.subheader("📋 Comparative Analysis")
                    st.dataframe(df.drop(columns=["sort_val"]), use_container_width=True)
                else:
                    st.error("No valid data points found in this price range.")
            else:
                st.error("System Error: Market scan failed. Verify API configuration.")

# FOOTER
st.markdown("---")
st.markdown("<div style='text-align: center; color: #8b949e; font-size: 0.8rem;'>© 2026 LAPZER ANALYTICS | Intelligence Scout Interface v2.0</div>", unsafe_allow_html=True)
