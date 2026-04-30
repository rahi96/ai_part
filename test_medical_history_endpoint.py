#!/usr/bin/env python
"""Test medical history analysis endpoint."""
import asyncio
import httpx
import json

async def test_medical_history_endpoint():
    """Test POST /api/ai/medical-history/{user_id}/analyze"""
    
    user_id = "69dbaf38ab5bc30344949b08"
    url = f"http://127.0.0.1:8000/api/ai/medical-history/{user_id}/analyze"
    
    payload = {
        "medical_history": {
            "condition_name": "Polycystic Ovary Syndrome (PCOS)",
            "category": "Hormonal",
            "start": "2020-01-15",
            "date_diagnosed": "2020-06-20",
            "notes": "Diagnosed with irregular menstrual cycles, elevated testosterone levels, and insulin resistance"
        }
    }
    
    print("=" * 80)
    print("MEDICAL HISTORY ANALYSIS TEST")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"\nRequest Body:")
    print(json.dumps(payload, indent=2))
    print("\n" + "-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            print("Sending POST request...")
            response = await client.post(url, json=payload)
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"\nResponse Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            print(f"\nResponse Body:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except:
                print(response.text)
            
            print("\n" + "=" * 80)
            if response.status_code == 200:
                print("SUCCESS: Endpoint returned 200 OK")
            else:
                print(f"ERROR: Endpoint returned {response.status_code}")
                print("This is likely due to AWS Bedrock access not being approved yet.")
                print("\nTo fix:")
                print("1. Go to AWS Bedrock Console")
                print("2. Navigate to Model Access")
                print("3. Request access for Anthropic Claude 3 Sonnet")
                print("4. Fill out the Anthropic use case details form")
                print("5. Wait for approval (15 minutes to several hours)")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_medical_history_endpoint())
