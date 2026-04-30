#!/usr/bin/env python
"""Test AWS Bedrock directly."""
import json
import sys
sys.path.insert(0, '.')

from ai.config import settings
from ai.utils.aws_bedrock_llm import bedrock_llm

print("Testing AWS Bedrock Direct Connection")
print("=" * 80)

if bedrock_llm is None:
    print("ERROR: bedrock_llm is None!")
    print("This means the AWS Bedrock client failed to initialize during import.")
    sys.exit(1)

try:
    print(f"Bedrock LLM Instance: {bedrock_llm}")
    print(f"Model ID: {bedrock_llm.get_model()}")
    print(f"Region: {settings.aws_region}")
    print(f"Credentials: Access Key ID present: {'Yes' if settings.aws_access_key_id else 'No'}")
    print()
    
    client = bedrock_llm.get_client()
    print(f"Bedrock Client: {client}")
    print()
    
    # Try a simple invoke call
    print("Attempting to invoke Bedrock model...")
    messages = [
        {"role": "user", "content": "Say 'Hello, AWS Bedrock!' and nothing else."}
    ]
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-06-01",
        "max_tokens": 100,
        "temperature": 0.7,
        "messages": messages
    })
    
    print(f"Request body: {body}")
    print()
    
    response = client.invoke_model(
        modelId=bedrock_llm.get_model(),
        body=body
    )
    
    print("Response received!")
    response_body = json.loads(response['body'].read())
    print(f"Response: {json.dumps(response_body, indent=2)}")
    
    if 'content' in response_body:
        content = response_body['content'][0].get('text', '')
        print(f"\nExtracted text: {content}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
