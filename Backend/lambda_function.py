import json
import boto3
import time

# 1. DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('CodeGuardianSessions')

# 2. Bedrock Setup (Keys redacted for public repository security)
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1', 
    aws_access_key_id='YOUR_AWS_ACCESS_KEY_ID', 
    aws_secret_access_key='YOUR_AWS_SECRET_ACCESS_KEY' 
)

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        code = body.get('code', '')
        explanation = body.get('explanation', '')
        language = body.get('language', 'python')
        is_eli5 = body.get('eli5', False)
        
        # 3. Prompt Logic
        if is_eli5:
            prompt = f"""Act as a friendly coding mentor. Explain this {language} code to a complete beginner. 
            Use a simple real-world analogy. Keep it under 3 sentences. No technical jargon. Ask one simple question at the end.
            Code: {code}
            Respond ONLY with valid JSON: {{"eli5_explanation": "your analogy", "verify_question": "your question"}}"""
        else:
            prompt = f"""Grade this explanation of {language} code on understanding (0-100 score).
            Code: {code}
            Explanation: {explanation}
            Output ONLY valid JSON, no markdown formatting: {{"score": 85, "overallcomment": "brief feedback", "issues": ["issue1"]}}"""
        
        # ==========================================
        # 4. ENTERPRISE FALLBACK SYSTEM
        # ==========================================
        try:
            # PLAN A: Primary Model (Nova Pro)
            response = bedrock.converse(
                modelId='amazon.nova-pro-v1:0',
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"temperature": 0.2}
            )
            raw_text = response['output']['message']['content'][0]['text']
            
        except Exception as primary_error:
            print(f"WARNING: Nova Pro Failed ({str(primary_error)}). Triggering Fallback to Nova Micro...")
            
            # PLAN B: Fallback Model (Nova Micro)
            response = bedrock.converse(
                modelId='amazon.nova-micro-v1:0', 
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"temperature": 0.2}
            )
            raw_text = response['output']['message']['content'][0]['text']
        # ==========================================
            
        # Clean up Markdown JSON blocks
        clean_text = raw_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        result = json.loads(clean_text)
        
        # 5. Save to DynamoDB
        session_id = context.aws_request_id
        table.put_item(Item={
            'sessionId': session_id,
            'score': result.get('score', 0),
            'comment': result.get('overallcomment', ''),
            'issues': json.dumps(result.get('issues', [])),
            'eli5': is_eli5,
            'timestamp': str(int(time.time()))
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"CRITICAL ERROR: Both models failed. {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "AI processing failed. Please try again."})
        }
