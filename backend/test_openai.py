"""
Test DeepSeek API Connection
"""
from openai import OpenAI

API_KEY = 'sk-967e5a68e75f428583289da0603d1e65'

print("=" * 60)
print("Testing DeepSeek API Connection")
print("=" * 60)
print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print()

try:
    # DeepSeek API is OpenAI-compatible, just needs a different base URL
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    print("[OK] DeepSeek client created successfully")
    
    print("\n[TEST] Testing API call...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "Say 'Hello, DeepSeek is working!' in exactly those words."}
        ],
        max_tokens=20
    )
    
    result = response.choices[0].message.content
    print(f"[SUCCESS] DeepSeek API is working!")
    print(f"Response: {result}")
    print()
    
    # Test resume title generation
    print("[TEST] Testing resume title generation...")
    job_desc = "We are looking for a Liquidity Manager to manage treasury operations and FX trading"
    response2 = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": f"Make the resume title for this job description: {job_desc}"}
        ],
        max_tokens=50
    )
    
    title = response2.choices[0].message.content
    print(f"[SUCCESS] Generated Title: {title}")
    print()
    print("=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - DeepSeek API is working!")
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] DeepSeek API is NOT working")
    print(f"Error: {str(e)}")
    print()
    print("Possible reasons:")
    print("1. Invalid or expired API key")
    print("2. No billing/credits set up on DeepSeek account")
    print("3. API key doesn't have proper permissions")
    print("4. Network/firewall issues")
    print()
    print("Solutions:")
    print("- Go to https://platform.deepseek.com/")
    print("- Check your API key")
    print("- Make sure billing is set up and you have credits")
    print("=" * 60)

