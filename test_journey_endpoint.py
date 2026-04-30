#!/usr/bin/env python
"""Test journey plan creation endpoint."""
import asyncio
import httpx
import json

async def test_journey_endpoint():
    """Test POST /api/ai/journey/create-plan/{user_id}"""
    
    user_id = "69dbaf38ab5bc30344949b08"
    url = f"http://127.0.0.1:8000/api/ai/journey/create-plan/{user_id}"
    
    payload = {
        "goal_title": "Improve Energy Levels During Perimenopause",
        "measurement": "Energy Level Score",
        "current_value": 4,
        "target_value": 8,
        "notes": "Currently experiencing afternoon fatigue and low morning energy. Want to feel more energized throughout the day."
    }
    
    print("=" * 90)
    print("JOURNEY PLAN CREATION TEST")
    print("=" * 90)
    print(f"\nURL: {url}")
    print(f"\nRequest Body:")
    print(json.dumps(payload, indent=2))
    print("\n" + "-" * 90)
    print("Sending POST request to create journey plan...")
    print("-" * 90 + "\n")
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload)
            
            print(f"Status Code: {response.status_code}")
            print(f"\nResponse Headers:")
            for key, value in response.headers.items():
                if key.lower().startswith('x-') or key.lower() in ['content-type', 'content-length', 'date']:
                    print(f"  {key}: {value}")
            
            print(f"\nResponse Body:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
                
                if response.status_code == 200:
                    print("\n" + "=" * 90)
                    print("✅ SUCCESS: Journey plan created!")
                    print("=" * 90)
                    print(f"\nPlan Title: {response_json.get('plan_title', 'N/A')}")
                    print(f"Created For: {response_json.get('username', 'N/A')}")
                    print(f"Created At: {response_json.get('created_at', 'N/A')}")
                    print(f"\nWelcome Message:\n  {response_json.get('welcome_message', 'N/A')}")
                    print(f"\nPlan Rationale:\n  {response_json.get('why_plan_description', 'N/A')}")
                    
                    goals = response_json.get('goals', [])
                    print(f"\nGoals ({len(goals)}):")
                    for i, goal in enumerate(goals, 1):
                        print(f"  {i}. {goal.get('title', 'N/A')}")
                        print(f"     Current: {goal.get('current_value')} | Target: {goal.get('target_value')}")
                        print(f"     Progress: {goal.get('progress_percentage', 0)}%")
                        print(f"     Description: {goal.get('target_description', 'N/A')}")
                    
                    actions = response_json.get('recommended_actions', [])
                    print(f"\nRecommended Actions ({len(actions)}):")
                    for i, action in enumerate(actions, 1):
                        print(f"  {i}. {action}")
                    
                    print(f"\nNext Review Date: {response_json.get('next_review_date', 'N/A')}")
                else:
                    print(f"\n❌ ERROR: Endpoint returned {response.status_code}")
                    
            except:
                print(response.text)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_journey_endpoint())
