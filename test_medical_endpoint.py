#!/usr/bin/env python
"""Test script for medical history endpoint."""
import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_endpoint():
    """Test the medical history analysis endpoint."""
    url = "http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze"
    
    payload = {
        "medical_history": {
            "condition_name": "PCOS",
            "category": "Hormonal",
            "start": "2020-01-15",
            "date_diagnosed": "2020-06-20",
            "notes": "Diagnosed with irregular periods and elevated testosterone levels"
        }
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response:\n{response.text}")
            print("-" * 80)
            
            if response.status_code != 200:
                print(f"ERROR: Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw Error Response: {response.text}")
    except Exception as e:
        logger.exception(f"Request failed: {e}")
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
