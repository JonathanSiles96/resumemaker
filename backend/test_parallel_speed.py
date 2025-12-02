"""
Test Parallel Speed Optimization
"""
import time
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.ai_content_generator import AIContentGenerator

# Test data
job_description = """
We are seeking a Senior Full Stack Developer to join our team. 

Requirements:
- 8+ years of experience in software development
- Strong proficiency in React, Node.js, and TypeScript
- Experience with cloud platforms (AWS, Azure)
- Strong understanding of microservices architecture
- Experience with CI/CD pipelines
- Excellent problem-solving skills

Responsibilities:
- Design and develop scalable web applications
- Lead technical architecture decisions
- Mentor junior developers
- Collaborate with cross-functional teams
"""

work_history = [
    {
        'company': 'Amazon Web Services',
        'location': 'Seattle, WA',
        'start_date': 'January 2020',
        'end_date': 'Present'
    },
    {
        'company': 'Microsoft Corporation',
        'location': 'Redmond, WA',
        'start_date': 'March 2017',
        'end_date': 'December 2019'
    },
    {
        'company': 'Google Inc.',
        'location': 'Mountain View, CA',
        'start_date': 'June 2014',
        'end_date': 'February 2017'
    },
    {
        'company': 'Startup XYZ',
        'location': 'San Francisco, CA',
        'start_date': 'January 2012',
        'end_date': 'May 2014'
    }
]

years_experience = 14

print("=" * 80)
print("⚡ PARALLEL SPEED TEST - DeepSeek AI")
print("=" * 80)
print()

# Initialize AI generator
ai_gen = AIContentGenerator()

# Test the PARALLEL method
print("⚡ Testing PARALLEL method (Multiple simultaneous API calls)...")
print("-" * 80)

result = ai_gen.generate_complete_resume_content_parallel(
    job_description=job_description,
    years_experience=years_experience,
    work_history=work_history
)

print()
print("=" * 80)

if result:
    print("✅ CONTENT GENERATED:")
    print(f"\n📌 Professional Title:")
    print(f"   {result.get('professional_title', '')}")
    print(f"\n📝 Professional Summary:")
    summary = result.get('professional_summary', '')
    print(f"   {summary[:150]}...")
    print(f"\n💼 Work Experiences Generated: {len(result.get('work_experiences', []))}")
    for i, exp in enumerate(result.get('work_experiences', [])):
        print(f"   {i+1}. {exp.get('job_title', '')} at {exp.get('company', '')}")
        print(f"      Description length: {len(exp.get('description', ''))} characters")
else:
    print("❌ Failed to generate content")

print()
print("=" * 80)
print("🎯 EXPECTED RESULTS")
print("=" * 80)
print("Sequential Method: ~20-30 seconds (10-12 API calls one after another)")
print("Single Call Method: ~40-60 seconds (1 big API call with 4000 tokens)")
print("Parallel Method:    ~5-10 seconds (10-12 API calls happening simultaneously)")
print()
print("💡 The parallel method makes the same calls as sequential, but")
print("   all at the same time, so it's as fast as the slowest single call!")
print("=" * 80)

