"""Test ALL model families to find what actually works on this account."""
import boto3, json
from ai.config import settings

client = boto3.client(
    "bedrock-runtime",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

# Test Amazon Titan models (usually pre-approved)
TITAN_MODELS = [
    ("amazon.titan-text-premier-v1:0", "titan"),
    ("amazon.titan-text-express-v1", "titan"),
    ("amazon.titan-text-lite-v1", "titan"),
]

# Test Meta Llama models
LLAMA_MODELS = [
    ("us.meta.llama3-8b-instruct-v1:0", "llama"),
    ("meta.llama3-8b-instruct-v1:0", "llama"),
    ("us.meta.llama3-70b-instruct-v1:0", "llama"),
    ("meta.llama3-70b-instruct-v1:0", "llama"),
]

# Test Mistral
MISTRAL_MODELS = [
    ("mistral.mistral-7b-instruct-v0:2", "mistral"),
    ("mistral.mistral-large-2402-v1:0", "mistral"),
]

def invoke_titan(client, model_id, prompt):
    body = json.dumps({"inputText": prompt, "textGenerationConfig": {"maxTokenCount": 30}})
    resp = client.invoke_model(modelId=model_id, body=body)
    result = json.loads(resp["body"].read())
    return result["results"][0]["outputText"]

def invoke_llama(client, model_id, prompt):
    body = json.dumps({"prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>", "max_gen_len": 30})
    resp = client.invoke_model(modelId=model_id, body=body)
    result = json.loads(resp["body"].read())
    return result["generation"]

def invoke_mistral(client, model_id, prompt):
    body = json.dumps({"prompt": f"<s>[INST] {prompt} [/INST]", "max_tokens": 30})
    resp = client.invoke_model(modelId=model_id, body=body)
    result = json.loads(resp["body"].read())
    return result["outputs"][0]["text"]

print("Testing all model families...\n")
first_working = None

all_tests = [
    (TITAN_MODELS, invoke_titan),
    (LLAMA_MODELS, invoke_llama),
    (MISTRAL_MODELS, invoke_mistral),
]

for model_list, invoke_fn in all_tests:
    for model_id, family in model_list:
        try:
            text = invoke_fn(client, model_id, "Say the word WORKS and nothing else.")
            clean = text.strip().encode("ascii", errors="replace").decode()
            print(f"WORKS: {model_id} -> '{clean[:60]}'")
            if first_working is None:
                first_working = (model_id, family)
        except Exception as e:
            short = str(e)[:100].encode("ascii", errors="replace").decode()
            print(f"FAIL:  {model_id} -> {short}")

print()
if first_working:
    print(f"BEST AVAILABLE MODEL: {first_working[0]} (family: {first_working[1]})")
else:
    print("NO models work. Bedrock access must be enabled in the AWS console.")
    print("Go to: AWS Console -> Bedrock -> Model access -> Enable models")
