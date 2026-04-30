#!/usr/bin/env python
"""Test the endpoint with mock LLM response."""
import sys
import json
sys.path.insert(0, '.')

# Mock the bedrock_llm to test the endpoint
import ai.utils.aws_bedrock_llm as bedrock_module

class MockBedrockLLM:
    """Mock Bedrock LLM for testing."""
    
    def get_client(self):
        return self
    
    def get_model(self):
        return "mock-model"
    
    def invoke_model(self, **kwargs):
        """Return a mock response."""
        # Create a mock response that matches Bedrock's response format
        mock_response = {
            "content": [
                {
                    "text": json.dumps({
                        "analysis": {
                            "title": "Understanding PCOS: Hormonal and Metabolic Insights",
                            "description": "PCOS is a complex endocrine disorder affecting reproductive-age women, characterized by hormonal imbalances and metabolic dysfunction.",
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
                                },
                                {
                                    "name": "Insulin Resistance",
                                    "match_percentage": 90,
                                    "severity": "high",
                                    "color": "red",
                                    "shared_symptoms": ["Weight gain", "Dark skin patches", "Acne"]
                                },
                                {
                                    "name": "Metabolic Syndrome",
                                    "match_percentage": 80,
                                    "severity": "high",
                                    "color": "orange",
                                    "shared_symptoms": ["High blood pressure", "Elevated cholesterol", "Weight gain"]
                                },
                                {
                                    "name": "Depression and Anxiety",
                                    "match_percentage": 65,
                                    "severity": "medium",
                                    "color": "yellow",
                                    "shared_symptoms": ["Mood swings", "Sleep disturbance", "Low energy"]
                                },
                                {
                                    "name": "Sleep Apnea",
                                    "match_percentage": 55,
                                    "severity": "medium",
                                    "color": "yellow",
                                    "shared_symptoms": ["Fatigue", "Sleep disturbance", "Irregular breathing"]
                                },
                                {
                                    "name": "Autoimmune Thyroiditis",
                                    "match_percentage": 50,
                                    "severity": "medium",
                                    "color": "pink",
                                    "shared_symptoms": ["Irregular periods", "Fatigue", "Weight changes"]
                                }
                            ]
                        }
                    })
                }
            ]
        }
        
        # Return mock response object with body
        class MockResponse:
            def __init__(self, data):
                self.data = data
            
            def __getitem__(self, key):
                if key == 'body':
                    class MockBody:
                        def __init__(self, data):
                            self.data = data
                        def read(self):
                            return json.dumps(self.data).encode()
                    return MockBody(self.data)
        
        return MockResponse(mock_response)

# Patch the module
bedrock_module.bedrock_llm = MockBedrockLLM()

# Now import the services that use it
from ai.services.medical_history_service import MedicalHistoryService
from ai.models.schemas import MedicalHistoryAnalysisRequest, MedicalHistoryEntry
import asyncio

async def test_endpoint():
    """Test the medical history service with mock LLM."""
    
    print("=" * 80)
    print("MEDICAL HISTORY ENDPOINT TEST (WITH MOCK LLM)")
    print("=" * 80)
    
    # Create request
    med_hist = MedicalHistoryEntry(
        condition_name="Polycystic Ovary Syndrome (PCOS)",
        category="Hormonal",
        start="2020-01-15",
        date_diagnosed="2020-06-20",
        notes="Diagnosed with irregular menstrual cycles, elevated testosterone levels, and insulin resistance"
    )
    
    request = MedicalHistoryAnalysisRequest(medical_history=med_hist)
    
    print(f"\nRequest:")
    print(json.dumps({
        "condition_name": med_hist.condition_name,
        "category": med_hist.category,
        "start": med_hist.start,
        "date_diagnosed": med_hist.date_diagnosed,
        "notes": med_hist.notes
    }, indent=2))
    
    print("\n" + "-" * 80)
    print("Processing medical history analysis...")
    print("-" * 80 + "\n")
    
    try:
        service = MedicalHistoryService()
        response = await service.analyze_medical_history(request)
        
        print("SUCCESS! Response received:")
        print(json.dumps(response.model_dump(), indent=2))
        
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY:")
        print("=" * 80)
        print(f"Title: {response.analysis.title}")
        print(f"Description: {response.analysis.description}")
        print(f"\nSymptom Overlap Percentages:")
        for category, percentage in response.analysis.symptom_overlap.items():
            print(f"  {category}: {percentage}%")
        
        print(f"\nRelated Conditions Found: {len(response.analysis.conditions)}")
        for i, condition in enumerate(response.analysis.conditions, 1):
            print(f"\n  {i}. {condition.name}")
            print(f"     Match: {condition.match_percentage}% | Severity: {condition.severity} | Color: {condition.color}")
            print(f"     Shared symptoms: {', '.join(condition.shared_symptoms)}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
