import json
import boto3
import time
import urllib.request

# Keep DynamoDB exactly where it is!
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('CodeGuardianSessions')

# PASTE YOUR GEMINI API KEY HERE BEFORE DEPLOYING
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        code = body.get('code', '')
        explanation = body.get('explanation', '')
        language = body.get('language', 'python')
        is_eli5 = body.get('eli5', False)
        
        # The Updated ELI5 Prompt Logic
        if is_eli5:
            prompt = f"""Act as an extremely friendly and encouraging coding mentor. Explain this {language} code to a complete beginner. 
            Rules:
            1. Use a simple, relatable real-world analogy (like cooking, cars, or building blocks).
            2. ZERO technical jargon. Do not use words like 'function', 'variable', or 'iterate'.
            3. Keep the explanation under 3 sentences so they don't get overwhelmed.
            4. Ask ONE simple, interactive question at the end to check their understanding.
            
            Code to explain: {code}
            
            Respond ONLY with valid JSON, no markdown formatting: {{"eli5_explanation": "your analogy explanation", "verify_question": "your simple question?"}}"""
        else:
            prompt = f"""Grade this explanation of {language} code on understanding (0-100 score).
            Code: {code}
            Explanation: {explanation}
            Output ONLY valid JSON, no markdown formatting: {{"score": 85, "overallcomment": "brief feedback", "issues": ["bullet1", "bullet2"]}}"""
        
        # Call Google Gemini API directly
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2, # Low temperature for strict JSON output
                "responseMimeType": "application/json" # Forces Gemini to return clean JSON!
            }
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result_data = json.loads(response.read().decode('utf-8'))
            
        # Extract the text from Gemini's response
        raw_text = result_data['candidates'][0]['content']['parts'][0]['text']
        
        # Clean it up just in case
        clean_text = raw_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        result = json.loads(clean_text)
        
        # Store in AWS DynamoDB
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
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }