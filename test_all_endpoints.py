#!/usr/bin/env python
"""Comprehensive test suite for all API endpoints."""
import asyncio
import httpx
import json
from typing import Dict, Any

USER_ID = "69dbaf38ab5bc30344949b08"
BASE_URL = "http://127.0.0.1:8000/api/ai"

# Medical history test cases
MEDICAL_HISTORY_TESTS = [
    {
        "name": "PCOS Analysis",
        "data": {
            "medical_history": {
                "condition_name": "Polycystic Ovary Syndrome (PCOS)",
                "category": "Hormonal",
                "start": "2020-01-15",
                "date_diagnosed": "2020-06-20",
                "notes": "Irregular menstrual cycles, elevated testosterone, insulin resistance"
            }
        }
    },
    {
        "name": "Hypothyroidism Analysis",
        "data": {
            "medical_history": {
                "condition_name": "Hypothyroidism",
                "category": "Endocrine",
                "start": "2019-03-10",
                "date_diagnosed": "2019-05-15",
                "notes": "Low TSH levels, fatigue, weight gain. On levothyroxine 75mcg"
            }
        }
    },
    {
        "name": "Migraine with Aura Analysis",
        "data": {
            "medical_history": {
                "condition_name": "Migraine with Aura",
                "category": "Neurological",
                "start": "2018-06-20",
                "date_diagnosed": "2018-08-10",
                "notes": "Monthly migraines triggered by hormonal changes, visual aura"
            }
        }
    },
    {
        "name": "Anxiety Disorder Analysis",
        "data": {
            "medical_history": {
                "condition_name": "Generalized Anxiety Disorder",
                "category": "Mental Health",
                "start": "2021-02-01",
                "date_diagnosed": "2021-04-15",
                "notes": "Persistent worry, sleep disturbances. On sertraline 50mg daily"
            }
        }
    },
]

# Journey plan test cases
JOURNEY_PLAN_TESTS = [
    {
        "name": "Energy Improvement Goal",
        "data": {
            "goal_title": "Improve Energy Levels During Perimenopause",
            "measurement": "Energy Level Score",
            "current_value": 4,
            "target_value": 8,
            "notes": "Afternoon fatigue and low morning energy"
        }
    },
    {
        "name": "Sleep Quality Goal",
        "data": {
            "goal_title": "Enhance Sleep Quality and Consistency",
            "measurement": "Sleep Quality Rating",
            "current_value": 3,
            "target_value": 9,
            "notes": "Night sweats and insomnia, waking 2-3 times per night"
        }
    },
    {
        "name": "Weight Management Goal",
        "data": {
            "goal_title": "Achieve Healthy Weight and Body Composition",
            "measurement": "Weight (kg)",
            "current_value": 78,
            "target_value": 65,
            "notes": "Gained 13kg during perimenopause, metabolism slowed"
        }
    },
    {
        "name": "Mood Stability Goal",
        "data": {
            "goal_title": "Stabilize Mood and Emotional Well-being",
            "measurement": "Mood Stability Score",
            "current_value": 4,
            "target_value": 8,
            "notes": "Experiencing mood swings and irritability, 2-3 episodes per week"
        }
    },
    {
        "name": "Hot Flash Relief Goal",
        "data": {
            "goal_title": "Reduce Hot Flashes and Night Sweats",
            "measurement": "Hot Flash Frequency (per day)",
            "current_value": 8,
            "target_value": 1,
            "notes": "Having 8-10 hot flashes daily, affecting sleep"
        }
    },
]

async def test_medical_history():
    """Test all medical history analysis cases."""
    print("\n" + "="*100)
    print("🏥 MEDICAL HISTORY ENDPOINT TESTS")
    print("="*100)
    
    async with httpx.AsyncClient(timeout=120) as client:
        for i, test_case in enumerate(MEDICAL_HISTORY_TESTS, 1):
            print(f"\n{'─'*100}")
            print(f"Test {i}/{len(MEDICAL_HISTORY_TESTS)}: {test_case['name']}")
            print(f"{'─'*100}")
            
            url = f"{BASE_URL}/medical-history/{USER_ID}/analyze"
            
            try:
                response = await client.post(url, json=test_case["data"])
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data.get("analysis", {})
                    
                    print(f"✅ Status: {response.status_code} OK")
                    print(f"\n📋 Title: {analysis.get('title', 'N/A')}")
                    print(f"\n📝 Description: {analysis.get('description', 'N/A')[:150]}...")
                    
                    overlap = analysis.get("symptom_overlap", {})
                    print(f"\n📊 Symptom Overlap:")
                    for category, percentage in overlap.items():
                        bar = "█" * (percentage // 10) + "░" * (10 - percentage // 10)
                        print(f"   {category:15} {bar} {percentage}%")
                    
                    conditions = analysis.get("conditions", [])
                    print(f"\n🔗 Related Conditions ({len(conditions)}):")
                    for j, condition in enumerate(conditions[:3], 1):
                        print(f"   {j}. {condition['name']} ({condition['match_percentage']}% match) - {condition['severity'].upper()}")
                        print(f"      Symptoms: {', '.join(condition['shared_symptoms'][:2])}")
                    
                else:
                    print(f"❌ Status: {response.status_code}")
                    print(f"Response: {response.text[:300]}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def test_journey_plans():
    """Test all journey plan creation cases."""
    print("\n\n" + "="*100)
    print("🎯 JOURNEY PLAN ENDPOINT TESTS")
    print("="*100)
    
    async with httpx.AsyncClient(timeout=120) as client:
        for i, test_case in enumerate(JOURNEY_PLAN_TESTS, 1):
            print(f"\n{'─'*100}")
            print(f"Test {i}/{len(JOURNEY_PLAN_TESTS)}: {test_case['name']}")
            print(f"{'─'*100}")
            
            url = f"{BASE_URL}/journey/create-plan/{USER_ID}"
            
            try:
                response = await client.post(url, json=test_case["data"])
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✅ Status: {response.status_code} OK")
                    print(f"\n📋 Plan Title: {data.get('plan_title', 'N/A')}")
                    print(f"👤 User: {data.get('username', 'N/A')}")
                    print(f"📅 Created: {data.get('created_at', 'N/A')}")
                    
                    print(f"\n💬 Welcome Message: {data.get('welcome_message', 'N/A')[:150]}...")
                    
                    goals = data.get("goals", [])
                    print(f"\n🎯 Health Goals ({len(goals)}):")
                    for j, goal in enumerate(goals, 1):
                        print(f"   {j}. {goal['title']}")
                        print(f"      {goal['current_value']} → {goal['target_value']} ({goal['target_description']})")
                    
                    actions = data.get("recommended_actions", [])
                    print(f"\n✨ Recommended Actions ({len(actions)}):")
                    for j, action in enumerate(actions[:3], 1):
                        print(f"   {j}. {action}")
                    if len(actions) > 3:
                        print(f"   ... and {len(actions) - 3} more actions")
                    
                    print(f"\n📅 Next Review: {data.get('next_review_date', 'N/A')}")
                    
                else:
                    print(f"❌ Status: {response.status_code}")
                    print(f"Response: {response.text[:300]}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def test_summary():
    """Print test summary."""
    print("\n\n" + "="*100)
    print("📊 TEST SUMMARY")
    print("="*100)
    print(f"\n✅ Medical History Tests: {len(MEDICAL_HISTORY_TESTS)} cases")
    print(f"✅ Journey Plan Tests: {len(JOURNEY_PLAN_TESTS)} cases")
    print(f"📍 User ID: {USER_ID}")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🔧 Model: Claude Opus 4-5 (anthropic.claude-opus-4-5-20251101-v1:0)")
    print("\n" + "="*100)

async def main():
    """Run all tests."""
    print("\n" + "="*100)
    print("🚀 COMPLETE API ENDPOINT TEST SUITE")
    print("="*100)
    print("\nStarting comprehensive endpoint tests...")
    print("Note: Tests use mock/template responses while AWS approval is pending")
    
    await test_medical_history()
    await test_journey_plans()
    await test_summary()
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
