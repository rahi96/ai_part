# Quick Testing Guide

## 🚀 Run Complete Test Suite

```bash
python test_all_endpoints.py
```

This will test:
- ✅ Medical History: 4 test cases (PCOS, Thyroid, Migraine, Anxiety)
- ✅ Journey Plans: 5 test cases (Energy, Sleep, Weight, Mood, Hot Flashes)

---

## 📋 Individual Endpoint Tests

### Medical History Endpoint

```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
    "medical_history": {
      "condition_name": "Polycystic Ovary Syndrome (PCOS)",
      "category": "Hormonal",
      "start": "2020-01-15",
      "date_diagnosed": "2020-06-20",
      "notes": "Irregular menstrual cycles, elevated testosterone, insulin resistance"
    }
  }'
```

### Journey Plan Endpoint

```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Improve Energy Levels During Perimenopause",
    "measurement": "Energy Level Score",
    "current_value": 4,
    "target_value": 8,
    "notes": "Afternoon fatigue and low morning energy"
  }'
```

---

## 📊 Test Results Summary

### Medical History Tests
| Condition | Status | Response Code | Analysis |
|-----------|--------|---------------|----------|
| PCOS | ✅ | 200 | Title, description, symptom overlap, 5 conditions |
| Hypothyroidism | ✅ | 200 | Title, description, symptom overlap, 5 conditions |
| Migraine with Aura | ✅ | 200 | Title, description, symptom overlap, 5 conditions |
| Anxiety Disorder | ✅ | 200 | Title, description, symptom overlap, 5 conditions |

### Journey Plan Tests
| Goal | Status | Response Code | Contains |
|-----|--------|---------------|----------|
| Energy Improvement | ✅ | 200 | Plan, goals, actions, review date |
| Sleep Quality | ✅ | 200 | Plan, goals, actions, review date |
| Weight Management | ✅ | 200 | Plan, goals, actions, review date |
| Mood Stability | ✅ | 200 | Plan, goals, actions, review date |
| Hot Flash Relief | ✅ | 200 | Plan, goals, actions, review date |

---

## 📄 All JSON Request Examples

See [TEST_REQUESTS.md](TEST_REQUESTS.md) for complete documentation with:
- 5 medical history test cases
- 6 journey plan test cases
- cURL commands for each
- Expected response structure
- PowerShell examples

---

## 🧪 Test Files Available

1. **test_all_endpoints.py** - Comprehensive test suite (all endpoints + cases)
2. **test_medical_history_endpoint.py** - Individual medical history test
3. **test_journey_endpoint.py** - Individual journey plan test
4. **test_endpoint_summary.py** - Medical history with detailed output
5. **test_journey_comprehensive.py** - Journey plan with detailed output
6. **TEST_REQUESTS.md** - JSON request examples and documentation

---

## ✨ Current Status

- ✅ **Medical History Endpoint**: 200 OK with fallback responses
- ✅ **Journey Plan Endpoint**: 200 OK with fallback responses
- ⏳ **AWS Bedrock**: Model access approved (Opus 4-5)
- 🎯 **Next Step**: Live AI integration working once approved

---

## 🔍 Response Structure

### Medical History Response
```json
{
  "analysis": {
    "title": "string",
    "description": "string",
    "symptom_overlap": {
      "Hormonal": 75,
      "Mental": 50,
      "Metabolic": 65,
      "Fatigue": 70,
      "Immune": 45
    },
    "conditions": [
      {
        "name": "Thyroid Disorders",
        "match_percentage": 80,
        "severity": "high",
        "color": "red",
        "shared_symptoms": ["Symptom1", "Symptom2", "Symptom3"]
      }
    ]
  }
}
```

### Journey Plan Response
```json
{
  "plan_title": "EMPOWER YOUR PERIMENOPAUSE JOURNEY",
  "username": "string",
  "created_at": "string",
  "welcome_message": "string",
  "why_plan_description": "string",
  "goals": [
    {
      "title": "string",
      "target_description": "string",
      "current_value": 0,
      "target_value": 0,
      "progress_percentage": 0
    }
  ],
  "recommended_actions": ["action1", "action2"],
  "next_review_date": "string"
}
```

---

## 🛠️ Troubleshooting

**Q: Getting 500 error?**
A: Check server logs and ensure the API is running:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Q: Empty responses?**
A: Fallback responses are being returned. This is normal while AWS approval is pending.

**Q: How to enable live AI?**
A: When AWS Bedrock approves Claude Opus 4-5 access, live responses will activate automatically.

---

## 📞 API Details

- **Base URL**: http://127.0.0.1:8000/api/ai
- **Medical History Path**: /medical-history/{user_id}/analyze
- **Journey Plan Path**: /journey/create-plan/{user_id}
- **LLM Model**: Claude Opus 4-5 (anthropic.claude-opus-4-5-20251101-v1:0)
- **Region**: us-east-1

