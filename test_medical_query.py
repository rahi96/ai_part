"""Test medical query to verify RAG sources are populated"""
import requests
import json

print("\n" + "="*60)
print("TESTING MEDICAL QUERY ON AWS DEPLOYMENT")
print("="*60 + "\n")

url = "http://13.50.107.124:8000/api/ai/chat/message"
payload = {
    "user_id": "test123",
    "message": "I have terrible hot flashes at night that wake me up sweating"
}

print(f"🔍 Sending query: '{payload['message']}'")
print(f"📡 URL: {url}\n")

try:
    response = requests.post(url, json=payload, timeout=30)
    data = response.json()
    
    print(f"✅ Status Code: {response.status_code}\n")
    
    print("📊 RESPONSE ANALYSIS:")
    print("-" * 60)
    print(f"Intent:          {data.get('intent', 'N/A')}")
    print(f"Response Source: {data.get('response_source', 'N/A')}")
    print(f"AI Model:        {data.get('ai_model', 'N/A')}")
    print(f"Confidence:      {data.get('confidence', 'N/A')}")
    
    sources = data.get('sources', [])
    print(f"\n🎯 SOURCES ({len(sources)} found):")
    print("-" * 60)
    if sources:
        for i, source in enumerate(sources, 1):
            # Check if source is a dict (new format with URLs) or string (old format)
            if isinstance(source, dict):
                print(f"  {i}. {source.get('topic', 'Unknown')}")
                print(f"     🏥 {source.get('source_name', 'N/A')}")
                print(f"     🔗 {source.get('url', 'N/A')}")
            else:
                print(f"  {i}. {source}")
    else:
        print("  ❌ NO SOURCES FOUND!")
        print("  ⚠️  This means RAG is NOT working properly.")
    
    print(f"\n💬 RESPONSE (first 300 chars):")
    print("-" * 60)
    print(data.get('response', 'N/A')[:300] + "...")
    
    print("\n" + "="*60)
    
    # Save full response for inspection
    with open("test_response.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Full response saved to: test_response.json")
    
except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
    print("⚠️  Server might be taking too long to respond")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
