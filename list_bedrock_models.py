#!/usr/bin/env python
"""List available Bedrock models."""
import sys
sys.path.insert(0, '.')

from ai.config import settings
import boto3

client = boto3.client(
    'bedrock',
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)

try:
    print("Listing available Bedrock models...")
    print("=" * 80)
    
    response = client.list_foundation_models()
    
    models = response.get('modelSummaries', [])
    print(f"Found {len(models)} available models\n")
    
    # Filter for Anthropic/Claude models
    claude_models = [m for m in models if 'claude' in m.get('modelId', '').lower()]
    
    print("Available Claude models:")
    print("-" * 80)
    for model in claude_models:
        print(f"Model ID: {model['modelId']}")
        print(f"  Name: {model.get('modelName', 'N/A')}")
        print(f"  Provider: {model.get('provider', 'N/A')}")
        print()
    
    if claude_models:
        print("=" * 80)
        print(f"RECOMMENDATION: Use model ID: {claude_models[0]['modelId']}")
    else:
        print("\nNo Claude models found. Available models:")
        for model in models:
            print(f"  - {model['modelId']}")
            
except Exception as e:
    print(f"Error listing models: {str(e)}")
    import traceback
    traceback.print_exc()
