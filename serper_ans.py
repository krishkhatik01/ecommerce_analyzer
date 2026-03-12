import requests
import json

def search_internet(query):
    print(f"🕵️ Analyzing live market data for: {query}...")
    
    url = "https://google.serper.dev/search"
    
    payload = json.dumps({
        "q": query + " price in India",
        "gl": "in", # Target India
        "hl": "en"  # English results
    })
    
    headers = {
        'X-API-KEY': '2e696cc73991ea8c0dfbae39d06ea11e0c69ed79', # <--- PASTE YOUR KEY HERE
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()

    if 'organic' in data:
        print("\n" + "="*50)
        print(f"📊 LIVE GOOGLE DATA FOR: {query.upper()}")
        print("="*50)

        for i, result in enumerate(data['organic'][:5]):
            title = result.get('title', 'No Title')
            snippet = result.get('snippet', 'No Snippet')
            link = result.get('link', '#')
            
            print(f"[{i+1}] ✅ Verified Source")
            print(f"    Source: {title}")
            print(f"    Snippet: {snippet[:120]}...")
            print(f"    Link: {link}\n")
        print("="*50)
    else:
        print("❌ No data found. Check your API key!")

if __name__ == "__main__":
    user_query = input("Enter laptop/product: ")
    search_internet(user_query)
