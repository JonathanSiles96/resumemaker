"""
Simple OpenAI API Key Checker
Run this to see if your API key works
"""
import requests

API_KEY = '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'

print("\n" + "="*70)
print(" "*15 + "OPENAI API KEY CHECKER")
print("="*70)

# Test the API
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say: API is working!"}],
    "max_tokens": 10
}

print("\n[1/3] Testing API connection...")
response = requests.post(url, headers=headers, json=data, timeout=10)

print(f"[2/3] Response Status: {response.status_code}")

if response.status_code == 200:
    print("[3/3] Parsing response...")
    result = response.json()
    ai_message = result['choices'][0]['message']['content']
    
    print("\n" + "="*70)
    print(" [SUCCESS] YOUR API KEY IS WORKING! ".center(70, "="))
    print("="*70)
    print(f"\nAI Response: {ai_message}")
    print("\nYour resume generator will use AI to create custom content!")
    print("="*70 + "\n")
    
elif response.status_code == 401:
    print("[3/3] Authentication failed")
    print("\n" + "="*70)
    print(" [FAILED] API KEY NOT WORKING ".center(70, "="))
    print("="*70)
    print("\n ERROR: Invalid API Key (401 - Authentication Error)")
    print("\n This means one of:")
    print("   1. No billing set up on your OpenAI account")
    print("   2. API key is incorrect or expired")
    print("   3. API key doesn't have proper permissions")
    print("\n HOW TO FIX:")
    print("   Step 1: Go to https://platform.openai.com/settings/organization/billing")
    print("   Step 2: Add a payment method (credit card)")
    print("   Step 3: Add at least $5 in credits")
    print("   Step 4: Go to https://platform.openai.com/api-keys")
    print("   Step 5: Create a NEW API key")
    print("   Step 6: Replace the key in the code")
    print("\n IMPORTANT: ChatGPT Plus subscription is different from API access!")
    print("             You need separate billing for API usage.")
    print("="*70 + "\n")
    
elif response.status_code == 429:
    print("[3/3] Rate limit exceeded")
    print("\n" + "="*70)
    print(" [FAILED] QUOTA EXCEEDED ".center(70, "="))
    print("="*70)
    print("\n ERROR: Out of credits or rate limit hit")
    print("\n HOW TO FIX:")
    print("   Go to https://platform.openai.com/settings/organization/billing")
    print("   Add more credits or enable auto-recharge")
    print("="*70 + "\n")
    
else:
    print(f"[3/3] Unexpected error")
    print("\n" + "="*70)
    print(f" [FAILED] ERROR {response.status_code} ".center(70, "="))
    print("="*70)
    print(f"\n Response: {response.text}")
    print("="*70 + "\n")


