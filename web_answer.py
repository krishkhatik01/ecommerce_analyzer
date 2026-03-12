from duckduckgo_search import DDGS
import pandas as pd

def market_scout(query):
    print(f"🕵️ Scout is scanning the web for: {query}...")
    
    # We use the text search which is the most stable method
    with DDGS() as ddgs:
        # Adding 'price India' to the query forces commercial results
        results = list(ddgs.text(f"{query} price India", max_results=5))
    
    if not results:
        print("❌ No data found. The internet is blocking our scout!")
        return

    print("\n" + "="*50)
    print(f"📊 LIVE MARKET ANALYSIS FOR: {query.upper()}")
    print("="*50)

    for i, r in enumerate(results):
        title = r['title']
        snippet = r['body']
        link = r['href']
        
        # LOGIC: Check if the snippet contains a price (Numbers like 57,000)
        has_price = "₹" in snippet or "Rs" in snippet or any(char.isdigit() for char in snippet)
        
        status = "✅ PRICE DATA FOUND" if has_price else "🔗 INFO ONLY"
        
        print(f"[{i+1}] {status}")
        print(f"    Source: {title}")
        print(f"    Snippet: {snippet[:120]}...")
        print(f"    Link: {link}\n")

    print("="*50)
    print("💡 LOGICAL ACTION: Visit the top 2 links to confirm 'Current Lowest'.")

if __name__ == "__main__":
    user_query = input("Enter laptop/product name: ")
    market_scout(user_query)
