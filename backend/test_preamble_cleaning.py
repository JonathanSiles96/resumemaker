"""
Test Preamble Cleaning - Verify AI responses are clean
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.ai_content_generator import AIContentGenerator

# Test the cleaning function
ai_gen = AIContentGenerator()

print("=" * 80)
print("🧹 PREAMBLE CLEANING TEST")
print("=" * 80)
print()

# Test cases
test_cases = [
    {
        "name": "Professional Summary with preamble",
        "input": "Of course. Here is a professional summary tailored to the job description: Senior developer with 10 years experience.",
        "expected": "Senior developer with 10 years experience."
    },
    {
        "name": "Job Description with asterisks",
        "input": "Of course. Here is a professional job summary written for your position at Bananagun, meticulously tailored to mirror the language: *** At Bananagun, I led the development team.",
        "expected": "At Bananagun, I led the development team."
    },
    {
        "name": "Title with quotes",
        "input": '"Senior Full Stack Developer | React & Node.js"',
        "expected": "Senior Full Stack Developer | React & Node.js"
    },
    {
        "name": "Text with Professional Summary label",
        "input": "**Professional Summary:** Experienced engineer with strong background.",
        "expected": "Experienced engineer with strong background."
    },
    {
        "name": "Clean text (no preamble)",
        "input": "At Microsoft, I developed scalable applications.",
        "expected": "At Microsoft, I developed scalable applications."
    }
]

# Run tests
passed = 0
failed = 0

for test in test_cases:
    result = ai_gen._clean_preamble(test["input"])
    is_pass = result == test["expected"]
    
    if is_pass:
        passed += 1
        print(f"✅ PASS: {test['name']}")
    else:
        failed += 1
        print(f"❌ FAIL: {test['name']}")
        print(f"   Input:    {test['input'][:80]}")
        print(f"   Expected: {test['expected'][:80]}")
        print(f"   Got:      {result[:80]}")
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)

# Test with actual API call
print()
print("🔄 Testing with REAL API call...")
print("-" * 80)

job_desc = """
We are seeking a Senior Full Stack Developer with 8+ years of experience.
Requirements: React, Node.js, TypeScript, AWS
"""

print("Generating professional title...")
title = ai_gen.generate_professional_title(job_desc, 10)
print(f"\n✅ Generated Title:")
print(f"   {title}")
print()

# Check if title is clean (no preamble)
if title.startswith("Of course") or title.startswith("Here is") or ":" in title[:40]:
    print("❌ WARNING: Title may still contain preamble!")
else:
    print("✅ Title is clean (no preamble detected)")

print()
print("=" * 80)

