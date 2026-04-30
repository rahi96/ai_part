# API Test Requests - JSON & cURL Examples

## 🏥 Endpoint 1: Medical History Analysis

### API Details
```
Method: POST
URL: http://127.0.0.1:8000/api/ai/medical-history/{user_id}/analyze
```

---

### Test Case 1: PCOS Analysis

#### JSON Request
```json
{
  "medical_history": {
    "condition_name": "Polycystic Ovary Syndrome (PCOS)",
    "category": "Hormonal",
    "start": "2020-01-15",
    "date_diagnosed": "2020-06-20",
    "notes": "Diagnosed with irregular menstrual cycles, elevated testosterone levels, and insulin resistance"
  }
}
```

#### cURL Command
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
      "notes": "Diagnosed with irregular menstrual cycles, elevated testosterone levels, and insulin resistance"
    }
  }'
```

---

### Test Case 2: Thyroid Disorder Analysis

#### JSON Request
```json
{
  "medical_history": {
    "condition_name": "Hypothyroidism",
    "category": "Endocrine",
    "start": "2019-03-10",
    "date_diagnosed": "2019-05-15",
    "notes": "Low TSH levels, fatigue, weight gain, and temperature sensitivity. Currently on levothyroxine 75mcg"
  }
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
    "medical_history": {
      "condition_name": "Hypothyroidism",
      "category": "Endocrine",
      "start": "2019-03-10",
      "date_diagnosed": "2019-05-15",
      "notes": "Low TSH levels, fatigue, weight gain, and temperature sensitivity. Currently on levothyroxine 75mcg"
    }
  }'
```

---

### Test Case 3: Migraine with Aura

#### JSON Request
```json
{
  "medical_history": {
    "condition_name": "Migraine with Aura",
    "category": "Neurological",
    "start": "2018-06-20",
    "date_diagnosed": "2018-08-10",
    "notes": "Monthly migraines triggered by hormonal changes, visual disturbances before onset, severe headache lasting 4-6 hours"
  }
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
    "medical_history": {
      "condition_name": "Migraine with Aura",
      "category": "Neurological",
      "start": "2018-06-20",
      "date_diagnosed": "2018-08-10",
      "notes": "Monthly migraines triggered by hormonal changes, visual disturbances before onset, severe headache lasting 4-6 hours"
    }
  }'
```

---

### Test Case 4: Anxiety Disorder

#### JSON Request
```json
{
  "medical_history": {
    "condition_name": "Generalized Anxiety Disorder",
    "category": "Mental Health",
    "start": "2021-02-01",
    "date_diagnosed": "2021-04-15",
    "notes": "Persistent worry, sleep disturbances, and tension. Symptoms worsen during perimenopause. Taking sertraline 50mg daily"
  }
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
    "medical_history": {
      "condition_name": "Generalized Anxiety Disorder",
      "category": "Mental Health",
      "start": "2021-02-01",
      "date_diagnosed": "2021-04-15",
      "notes": "Persistent worry, sleep disturbances, and tension. Symptoms worsen during perimenopause. Taking sertraline 50mg daily"
    }
  }'
```

---

### Test Case 5: Type 2 Diabetes

#### JSON Request
```json
{
  "medical_history": {
    "condition_name": "Type 2 Diabetes Mellitus",
    "category": "Metabolic",
    "start": "2017-11-01",
    "date_diagnosed": "2017-12-20",
    "notes": "HbA1c 7.2%, managed with metformin 1000mg twice daily. Family history of diabetes. Recently premenopausal"
  }
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
    "medical_history": {
      "condition_name": "Type 2 Diabetes Mellitus",
      "category": "Metabolic",
      "start": "2017-11-01",
      "date_diagnosed": "2017-12-20",
      "notes": "HbA1c 7.2%, managed with metformin 1000mg twice daily. Family history of diabetes. Recently premenopausal"
    }
  }'
```

---

## 🎯 Endpoint 2: Journey Plan Creation

### API Details
```
Method: POST
URL: http://127.0.0.1:8000/api/ai/journey/create-plan/{user_id}
```

---

### Test Case 1: Energy Improvement Goal

#### JSON Request
```json
{
  "goal_title": "Improve Energy Levels During Perimenopause",
  "measurement": "Energy Level Score",
  "current_value": 4,
  "target_value": 8,
  "notes": "Currently experiencing afternoon fatigue and low morning energy. Want to feel more energized throughout the day."
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Improve Energy Levels During Perimenopause",
    "measurement": "Energy Level Score",
    "current_value": 4,
    "target_value": 8,
    "notes": "Currently experiencing afternoon fatigue and low morning energy. Want to feel more energized throughout the day."
  }'
```

---

### Test Case 2: Sleep Quality Goal

#### JSON Request
```json
{
  "goal_title": "Enhance Sleep Quality and Consistency",
  "measurement": "Sleep Quality Rating",
  "current_value": 3,
  "target_value": 9,
  "notes": "Struggling with night sweats and insomnia. Wake up 2-3 times per night. Need 7-8 hours of uninterrupted sleep"
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Enhance Sleep Quality and Consistency",
    "measurement": "Sleep Quality Rating",
    "current_value": 3,
    "target_value": 9,
    "notes": "Struggling with night sweats and insomnia. Wake up 2-3 times per night. Need 7-8 hours of uninterrupted sleep"
  }'
```

---

### Test Case 3: Weight Management Goal

#### JSON Request
```json
{
  "goal_title": "Achieve Healthy Weight and Body Composition",
  "measurement": "Weight (kg)",
  "current_value": 78,
  "target_value": 65,
  "notes": "Gained 13kg during perimenopause transition. Metabolism has slowed. Want to regain pre-perimenopausal weight through lifestyle changes"
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Achieve Healthy Weight and Body Composition",
    "measurement": "Weight (kg)",
    "current_value": 78,
    "target_value": 65,
    "notes": "Gained 13kg during perimenopause transition. Metabolism has slowed. Want to regain pre-perimenopausal weight through lifestyle changes"
  }'
```

---

### Test Case 4: Mood Stability Goal

#### JSON Request
```json
{
  "goal_title": "Stabilize Mood and Emotional Well-being",
  "measurement": "Mood Stability Score",
  "current_value": 4,
  "target_value": 8,
  "notes": "Experiencing mood swings and irritability. Have 2-3 emotional episodes per week. Want consistent, stable emotional state"
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Stabilize Mood and Emotional Well-being",
    "measurement": "Mood Stability Score",
    "current_value": 4,
    "target_value": 8,
    "notes": "Experiencing mood swings and irritability. Have 2-3 emotional episodes per week. Want consistent, stable emotional state"
  }'
```

---

### Test Case 5: Hot Flash Relief Goal

#### JSON Request
```json
{
  "goal_title": "Reduce Hot Flashes and Night Sweats",
  "measurement": "Hot Flash Frequency (per day)",
  "current_value": 8,
  "target_value": 1,
  "notes": "Having 8-10 hot flashes daily and night sweats affecting sleep. Using cooling strategies but need comprehensive management plan"
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Reduce Hot Flashes and Night Sweats",
    "measurement": "Hot Flash Frequency (per day)",
    "current_value": 8,
    "target_value": 1,
    "notes": "Having 8-10 hot flashes daily and night sweats affecting sleep. Using cooling strategies but need comprehensive management plan"
  }'
```

---

### Test Case 6: Brain Fog Management Goal

#### JSON Request
```json
{
  "goal_title": "Improve Mental Clarity and Cognitive Function",
  "measurement": "Cognitive Clarity Score",
  "current_value": 3,
  "target_value": 8,
  "notes": "Experiencing brain fog, difficulty concentrating, and memory lapses. Affecting work performance. Need lifestyle and nutritional interventions"
}
```

#### cURL Command
```bash
curl -X POST \
  'http://127.0.0.1:8000/api/ai/journey/create-plan/69dbaf38ab5bc30344949b08' \
  -H 'Content-Type: application/json' \
  -d '{
    "goal_title": "Improve Mental Clarity and Cognitive Function",
    "measurement": "Cognitive Clarity Score",
    "current_value": 3,
    "target_value": 8,
    "notes": "Experiencing brain fog, difficulty concentrating, and memory lapses. Affecting work performance. Need lifestyle and nutritional interventions"
  }'
```

---

## 🧪 PowerShell Testing Example

```powershell
# Test Medical History Endpoint
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    medical_history = @{
        condition_name = "Polycystic Ovary Syndrome (PCOS)"
        category = "Hormonal"
        start = "2020-01-15"
        date_diagnosed = "2020-06-20"
        notes = "Diagnosed with irregular menstrual cycles, elevated testosterone levels"
    }
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/ai/medical-history/69dbaf38ab5bc30344949b08/analyze" `
    -Method Post `
    -Headers $headers `
    -Body $body | ConvertTo-Json -Depth 10
```

---

## 📊 Expected Response Structure

### Medical History Response
```json
{
  "analysis": {
    "title": "Understanding PCOS: Hormonal and Metabolic Insights",
    "description": "PCOS is a complex endocrine disorder...",
    "symptom_overlap": {
      "Hormonal": 95,
      "Mental": 60,
      "Metabolic": 85,
      "Fatigue": 70,
      "Immune": 45
    },
    "conditions": [
      {
        "name": "Thyroid Disorders",
        "match_percentage": 85,
        "severity": "high",
        "color": "red",
        "shared_symptoms": ["Irregular periods", "Weight gain", "Fatigue"]
      }
    ]
  }
}
```

### Journey Plan Response
```json
{
  "plan_title": "EMPOWER YOUR PERIMENOPAUSE JOURNEY",
  "username": "webopo",
  "created_at": "April 29th, 2026",
  "welcome_message": "Welcome, webopo! We've created this plan...",
  "why_plan_description": "Your recent lab work shows...",
  "goals": [
    {
      "title": "Improve Energy Levels During Perimenopause",
      "target_description": "Target: 8.0 Energy Level Score",
      "current_value": 4.0,
      "target_value": 8.0,
      "progress_percentage": 0.0
    }
  ],
  "recommended_actions": [
    "Increase magnesium intake (400mg daily)",
    "Establish consistent sleep schedule"
  ],
  "next_review_date": "MAY 13TH, 2026"
}
```

---

## ✅ Quick Test Checklist

- [ ] Medical History PCOS test
- [ ] Medical History Thyroid test
- [ ] Medical History Migraine test
- [ ] Journey Plan Energy goal test
- [ ] Journey Plan Sleep goal test
- [ ] Journey Plan Weight goal test
- [ ] Verify response status code 200
- [ ] Verify response structure matches schema
- [ ] Check Claude Opus 4-5 analysis quality

---

## 🔧 Testing Tips

1. **Use user_id**: `69dbaf38ab5bc30344949b08` (existing test user)
2. **Content-Type**: Always use `application/json`
3. **Response Time**: Expect 1-5 seconds for processing
4. **Error Handling**: Check console logs for detailed error messages
5. **Validation**: Ensure all required fields are provided

