import boto3
import json

# Initialize Bedrock Runtime client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Test prompt
prompt = "What is the current price of Apple stock?"

# Call the model
response = bedrock_runtime.invoke_model(
    modelId='amazon.nova-pro-v1:0',
    body=json.dumps({
        "prompt": f"Human: {prompt}\nAssistant:",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 100
    }),
    contentType='application/json'
)

# Parse the response
response_body = json.loads(response['body'].read())
print("Full response structure:")
print(json.dumps(response_body, indent=2))

# Try different ways to access the content
print("\nTrying different access methods:")
if 'completion' in response_body:
    print("response_body['completion']:", response_body['completion'])

if 'results' in response_body:
    print("response_body['results']:", response_body['results'])

if 'output' in response_body:
    print("response_body['output']:", response_body['output'])
    if isinstance(response_body['output'], dict) and 'content' in response_body['output']:
        print("response_body['output']['content']:", response_body['output']['content'])

print("\nFull response as string:", str(response_body))
