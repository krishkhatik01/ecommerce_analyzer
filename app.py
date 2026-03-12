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
    page_icon="💻",
    layout="wide"
)

# --- CUSTOM PROFESSIONAL CSS ---
st.markdown("""
    <style>
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
    
    /* Header & Title Styling */
    h1, h2, h3 {
        color: #f0f6fc !important;
        font-family: 'Inter', sans-serif;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input {
        background-color: #0d1117;
        color: white;
        border: 1px solid #30363d;
    }

    /* Button Styling */
    div.stButton > button {
        background-color: #238636;
        color: white;
        border-radius: 6px;
        border: 1px solid rgba(240,246,252,0.1);
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #2ea043;
        border-color: #8b949e;
    }

    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-family: 'SF Mono', 'Roboto Mono', monospace;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")
    
    # API Key Management
    manual_key = st.text_input("Serper API Key", type="password", help="Get your key at serper.dev")
    API_KEY = manual_key if manual_key else os.getenv("SERPER_API_KEY")
    
    st.markdown("---")
    st.subheader("🎯 Price Filters")
    st.write("Exclude accessories and installments by setting a realistic range.")
    
    col_min, col_max = st.columns(2)
    with col_min:
        min_p = st.number_input("Min (₹)", value=1000, step=500)
    with col_max:
        max_p = st.number_input("Max (₹)", value=200000, step=5000)
    
    st.markdown("---")
    st.info("💡 **Pro-Tip:** For small tech items like mice or cables, set the Min Price to ₹500.")

# --- LOGIC FUNCTIONS ---
def extract_prices(text, low, high):
    """
    Uses Regex to find currency-formatted numbers and filters 
    them based on the user-defined price range.
    """
    # Pattern looks for ₹ or Rs followed by numbers with commas
    pattern = r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{2,3})+)'
    found = re.findall(pattern, text, re.IGNORECASE)
    
    valid_prices = []
    for p in found:
        # Convert string "54,990" to integer 54990
        val = int(p.replace(',', ''))
        if low <= val <= high:
            valid_prices.append(val)
    return valid_prices

def fetch_market_data(query):
    """Fetches real-time search results via Serper API."""
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
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- MAIN INTERFACE ---
st.title("💻 Lapzer Price Scout")
st.markdown(f"**Market Intelligence Engine** | Range: ₹{min_p:,} — ₹{max_p:,}")

# Search Bar
query = st.text_input("Enter product name:", placeholder="e.g. PlayStation 5 Slim")

if st.button("Scan Market Data"):
    if not API_KEY:
        st.warning("⚠️ API Key missing. Please provide a Serper.dev key in the sidebar.")
    elif not query:
        st.warning("⚠️ Please enter a product name to search.")
    else:
        with st.spinner(f"Analyzing listings for '{query}'..."):
            data = fetch_market_data(query)
            
            results = []
            prices_list = []

            if data and 'organic' in data:
                for item in data['organic']:
                    # Combine title and snippet for better extraction
                    content = f"{item.get('title', '')} {item.get('snippet', '')}"
                    found_prices = extract_prices(content, min_p, max_p)
                    
                    # Use the lowest price found in that specific listing
                    price = min(found_prices) if found_prices else None
                    
                    if price:
                        prices_list.append(price)
                        results.append({
                            "Retailer/Source": item.get('title')[:70] + "...",
                            "Price": f"₹{price:,}",
                            "Action": item.get('link'),
                            "sort_val": price
                        })

                if prices_list:
                    # Metrics Display
                    m1, m2, m3 = st.columns(3)
                    avg_price = sum(prices_list) // len(prices_list)
                    
                    m1.metric("Lowest Found", f"₹{min(prices_list):,}")
                    m2.metric("Average Price", f"₹{avg_price:,}")
                    m3.metric("Verified Sources", len(prices_list))

                    # Visual Data
                    st.markdown("---")
                    df = pd.DataFrame(results)
                    
                    st.subheader("📊 Market Price Distribution")
                    st.bar_chart(df.set_index("Retailer/Source")["sort_val"])

                    st.subheader("📋 Comparison Table")
                    st.dataframe(
                        df.drop(columns=["sort_val"]), 
                        use_container_width=True,
                        column_config={
                            "Action": st.column_config.LinkColumn("View Deal")
                        }
                    )
                else:
                    st.error("No valid prices found. Try broadening your Price Range in the sidebar.")
            else:
                st.error("No data returned. Check your API Key or search term.")

# Footer
st.markdown("---")
st.caption("Developed by Krish Khatik | Built for Tech Market Analysis")
