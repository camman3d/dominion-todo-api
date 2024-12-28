from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def invoke(prompt: str, model='claude-3-sonnet-20240229', max_tokens=1000) -> str:
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": prompt,
        }]
    )
    response = message.content[0].text
    return clean_response(response)

def clean_response(response: str) -> str:
    if response.startswith('```markdown\n') and response.endswith('```'):
        response = response[12:-3].strip()
    return response