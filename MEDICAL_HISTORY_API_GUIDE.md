# Medical History Analysis API - Usage Guide

## Overview
The Medical History Analysis endpoint analyzes a patient's medical history and identifies related conditions, symptom overlaps, and provides AI-driven insights about potential comorbidities and health concerns.

## Endpoint

### POST `/api/ai/medical-history/analyze`

Analyzes a medical history entry and returns AI-generated analysis with related conditions and symptom overlaps.

## Request Schema

```json
{
  "medical_history": {
    "condition_name": "string",      // Name of the condition (e.g., "PCOS")
    "start": "YYYY-MM",              // Start date in YYYY-MM format (e.g., "2022-01")
    "category": "string",             // Category (e.g., "Hormonal", "Metabolic", "Mental")
    "date_diagnosed": "YYYY-MM-DD",  // Diagnosis date in YYYY-MM-DD format
    "notes": "string"                 // Additional clinical notes
  },
  "user_id": "string (optional)"     // Optional user identifier for tracking
}
```

## Example Request

```bash
curl -X POST "http://localhost:8000/api/ai/medical-history/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "medical_history": {
      "condition_name": "PCOS",
      "start": "2022-01",
      "category": "Hormonal",
      "date_diagnosed": "2022-03-15",
      "notes": "Irregular periods, weight gain, hirsutism"
    }
  }'
```

## Response Schema

```json
{
  "analysis": {
    "title": "string",                    // Professional analysis title
    "description": "string",              // Explanation of findings
    "symptom_overlap": {
      "Hormonal": integer,                // Percentage overlap (0-100)
      "Mental": integer,                  // Percentage overlap (0-100)
      "PCOS": integer,                    // Percentage overlap (0-100)
      "Metabolic": integer,               // Percentage overlap (0-100)
      "Fatigue": integer,                 // Percentage overlap (0-100)
      "Immune": integer                   // Percentage overlap (0-100)
    },
    "conditions": [
      {
        "name": "string",                 // Condition name
        "match_percentage": integer,      // Match percentage (0-100)
        "severity": "low|medium|high",    // Severity level
        "color": "string",                // UI color code (red, orange, yellow, etc.)
        "shared_symptoms": ["string"]     // List of shared symptoms
      }
    ]
  }
}
```

## Example Response

```json
{
  "analysis": {
    "title": "Conditions That Matter: Understanding PCOS and Related Concerns",
    "description": "These symptoms/conditions possibly overlap with PCOS and may require integrated management.",
    "symptom_overlap": {
      "Hormonal": 88,
      "Mental": 62,
      "PCOS": 100,
      "Metabolic": 85,
      "Fatigue": 70,
      "Immune": 58
    },
    "conditions": [
      {
        "name": "Insulin Resistance / Pre-Diabetes",
        "match_percentage": 83,
        "severity": "high",
        "color": "red",
        "shared_symptoms": ["Weight gain", "Irregular periods", "Increased thirst"]
      },
      {
        "name": "Adrenal Fatigue / Cortisol Imbalance",
        "match_percentage": 74,
        "severity": "high",
        "color": "orange",
        "shared_symptoms": ["Fatigue", "Mood changes", "Weight gain"]
      },
      {
        "name": "Depression / Anxiety Disorder",
        "match_percentage": 65,
        "severity": "medium",
        "color": "pink",
        "shared_symptoms": ["Mood changes", "Brain fog", "Fatigue"]
      },
      {
        "name": "Thyroid Disorders",
        "match_percentage": 71,
        "severity": "medium",
        "color": "blue",
        "shared_symptoms": ["Fatigue", "Weight gain", "Irregular periods"]
      },
      {
        "name": "Autoimmune Conditions",
        "match_percentage": 62,
        "severity": "medium",
        "color": "purple",
        "shared_symptoms": ["Fatigue", "Weight changes", "Inflammation"]
      },
      {
        "name": "Sleep Disorders",
        "match_percentage": 68,
        "severity": "high",
        "color": "indigo",
        "shared_symptoms": ["Fatigue", "Mood changes", "Metabolic issues"]
      }
    ]
  }
}
```

## AI Analysis Features

### 1. **Symptom Overlap Analysis**
The AI analyzes the provided condition against multiple health categories:
- **Hormonal**: Hormone-related symptoms and conditions
- **Mental**: Psychological and mental health overlaps
- **Metabolic**: Metabolism and metabolic disorder connections
- **Fatigue**: Energy-related symptoms
- **Immune**: Immune system-related conditions
- **Category-specific**: The specific category of the input condition

### 2. **Related Conditions Identification**
Identifies 5-6 conditions that commonly present with overlapping symptoms:
- **Match Percentage**: How likely the condition overlaps (0-100%)
- **Severity**: Low (<30%), Medium (31-70%), High (>70%)
- **Color Coding**: Visual indicators for UI display
- **Shared Symptoms**: Specific symptoms in common with the input condition

### 3. **Evidence-Based Analysis**
The AI uses:
- Evidence-based medical knowledge
- Contemporary medical literature
- Women's health expertise
- Hormonal and metabolic pathways understanding

## Error Handling

### 400 Bad Request
```json
{
  "detail": "Invalid medical history data: Missing required field 'condition_name'"
}
```

### 500 Internal Server Error
```json
{
  "detail": "AI analysis failed. Please try again later."
}
```

### 503 Service Unavailable
```json
{
  "detail": "Backend service temporarily unavailable."
}
```

## Best Practices

1. **Accurate Data Entry**: Ensure all medical history data is accurate
2. **Detailed Notes**: Provide comprehensive notes for better AI analysis
3. **Standard Formats**: Use specified date formats (YYYY-MM for start, YYYY-MM-DD for diagnosis)
4. **Category Selection**: Choose appropriate health categories from available options
5. **User Tracking**: Include user_id for analytics and tracking purposes

## Supported Categories

- Hormonal
- Metabolic
- Mental
- Autoimmune
- Endocrine
- Cardiovascular
- Gastrointestinal
- Neurological
- Respiratory
- Other

## Integration Example

### Python (using requests)
```python
import requests
import json

url = "http://localhost:8000/api/ai/medical-history/analyze"
payload = {
    "medical_history": {
        "condition_name": "PCOS",
        "start": "2022-01",
        "category": "Hormonal",
        "date_diagnosed": "2022-03-15",
        "notes": "Irregular periods, weight gain"
    },
    "user_id": "user123"
}

response = requests.post(url, json=payload)
result = response.json()
print(json.dumps(result, indent=2))
```

### JavaScript (using fetch)
```javascript
const payload = {
    medical_history: {
        condition_name: "PCOS",
        start: "2022-01",
        category: "Hormonal",
        date_diagnosed: "2022-03-15",
        notes: "Irregular periods, weight gain"
    },
    user_id: "user123"
};

fetch('http://localhost:8000/api/ai/medical-history/analyze', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => console.log(JSON.stringify(data, null, 2)))
.catch(error => console.error('Error:', error));
```

## Performance Notes

- Response time: 2-5 seconds (depends on LLM API latency)
- No caching applied (fresh analysis for each request)
- Recommended max 100 concurrent requests
- Uses OpenAI GPT-4/3.5-turbo model

## Security & Privacy

- All requests are logged for audit purposes
- CORS enabled for authorized origins
- Input validation performed on all fields
- AI responses are not stored in database by default
- HIPAA-compliant data handling (when deployed)
