import streamlit as st
import requests
import re
import pandas as pd
import os
from dotenv import load_dotenv

# --- PAGE CONFIG ---
load_dotenv()
TAB_ICON = "assets/logo.png"
SIDEBAR_LOGO = "assets/logo1.png"

st.set_page_config(
    page_title="Lapzer | Market Scout",
    page_icon=TAB_ICON if os.path.exists(TAB_ICON) else "💻",
    layout="wide"
)

# --- ADVANCED UI CSS ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* LOGO CONTRAST FIX: Putting logo inside a subtle glowing container */
    .logo-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(46, 160, 67, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Scouting Button Glow */
    div.stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border-radius: 8px;
        font-weight: 700;
        border: none;
        height: 3em;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 160, 67, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR BRANDING ---
with st.sidebar:
    # Sidebar Logo with the new Container
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    if os.path.exists(SIDEBAR_LOGO):
        st.image(SIDEBAR_LOGO, use_container_width=True)
    else:
        st.title("🛡️ LAPZER")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    manual_key = st.text_input("Serper API Key", type="password", placeholder="Enter key...")
    API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")
    
    st.markdown("---")
    st.subheader("🎯 Price Filters")
    min_p = st.number_input("Min (₹)", value=1000)
    max_p = st.number_input("Max (₹)", value=200000)

# --- LOGIC ---
def extract_prices(text, low, high):
    pattern = r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{2,3})+)'
    found = re.findall(pattern, text, re.IGNORECASE)
    valid_prices = [int(p.replace(',', '')) for p in found if low <= int(p.replace(',', '')) <= high]
    return valid_prices

def fetch_market_data(query):
    if not API_KEY: return None
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json={"q": f"{query} price in India amazon flipkart", "gl": "in"})
        return response.json()
    except: return None

# --- UI ---
st.title("🌎 Market Intelligence Scout")
query = st.text_input("Product Analysis:", placeholder="e.g. iPhone 15")

if st.button("Start Scouting"):
    if not API_KEY: st.warning("Add API Key")
    else:
        with st.spinner("Scouting..."):
            data = fetch_market_data(query)
            if data and 'organic' in data:
                prices = []
                results = []
                for item in data['organic']:
                    p_list = extract_prices(f"{item.get('title')} {item.get('snippet')}", min_p, max_p)
                    if p_list:
                        price = min(p_list)
                        prices.append(price)
                        results.append({"Retailer": item.get('title')[:50], "Price": f"₹{price:,}", "val": price})
                
                if prices:
                    col1, col2 = st.columns(2)
                    col1.metric("Lowest", f"₹{min(prices):,}")
                    col2.metric("Avg", f"₹{sum(prices)//len(prices):,}")
                    st.bar_chart(pd.DataFrame(results).set_index("Retailer")["val"])
                else: st.error("No prices found.")
