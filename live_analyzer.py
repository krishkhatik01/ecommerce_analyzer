import requests
from bs4 import BeautifulSoup
import time

def get_market_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Note: Different sites use different HTML tags for prices.
        # This example looks for common price classes.
        # You can right-click 'Inspect' on a website to find the exact class.
        price_element = soup.find("span", {"class": "a-price-whole"}) # Common for Amazon
        
        if price_element:
            # Clean the string (remove commas and whitespace)
            price_text = price_element.text.replace(',', '').strip()
            return int(price_text)
    except Exception as e:
        print(f"Error fetching price: {e}")
    return None

def analyze_deal(current_price, target_price):
    print(f"\n🔍 ANALYSIS")
    print(f"Current Market Price: ₹{current_price:,}")
    print(f"Your Target Price:  ₹{target_price:,}")

    if current_price <= target_price:
        print("✅ DEAL FOUND! This is cheaper than your AI predicted value.")
    else:
        diff = current_price - target_price
        print(f"❌ OVERPRICED. It is ₹{diff:,} more than the fair value.")

# --- EXECUTION ---
# For testing, you can use a specific laptop URL from an Indian retailer
test_url = "https://www.example-shop.com/acer-alg-gaming" 
my_ai_prediction = 57000  # Based on your previous project results

# Let's simulate a live check
print("🌐 Connecting to E-commerce platform...")
# Since we don't have a live URL to scrape right now, we simulate finding 55000
live_price = 55000 

analyze_deal(live_price, my_ai_prediction)
