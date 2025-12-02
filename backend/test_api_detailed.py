import requests
import json

API_KEY = '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'

print("="*60)
print("DETAILED OpenAI API TEST")
print("="*60)
print(f"API Key Length: {len(API_KEY)}")
print(f"API Key Starts: {API_KEY[:15]}")
print(f"API Key Ends: {API_KEY[-15:]}")
print()

# Test with direct HTTP request
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
}

print("Sending request to OpenAI API...")
response = requests.post(url, headers=headers, json=data)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text[:500]}")
print()

if response.status_code == 200:
    print("="*60)
    print("SUCCESS! API KEY IS WORKING!")
    print("="*60)
    result = response.json()
    print(f"AI Response: {result['choices'][0]['message']['content']}")
else:
    print("="*60)
    print("FAILED! API KEY IS NOT WORKING!")
    print("="*60)
    if response.status_code == 401:
        print("Error 401: Invalid Authentication")
        print("\nThis means:")
        print("1. The API key is incorrect or expired")
        print("2. Billing is not set up on your OpenAI account")
        print("3. The API key doesn't have API access permissions")
        print("\nPlease:")
        print("- Go to https://platform.openai.com/settings/organization/billing")
        print("- Add a payment method")
        print("- Then create a NEW API key at https://platform.openai.com/api-keys")
    elif response.status_code == 429:
        print("Error 429: Rate limit or quota exceeded")

