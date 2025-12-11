# DeepSeek AI Integration Documentation

## Overview
The Resume Generator application has been migrated from OpenAI (ChatGPT) to DeepSeek AI for content generation. DeepSeek provides a cost-effective and powerful alternative with OpenAI-compatible API.

## Migration Details

### Changed Files
1. **`backend/services/ai_content_generator.py`**
   - Updated to use DeepSeek API endpoint
   - Changed base URL to `https://api.deepseek.com/v1`
   - Changed model from `gpt-4o-mini` to `deepseek-chat`
   - Updated API key to DeepSeek key
   - Updated debug messages to indicate DeepSeek usage

2. **`backend/test_openai.py`** (renamed conceptually to test DeepSeek)
   - Updated to test DeepSeek API connection
   - Changed base URL and model
   - Updated test messages and error handling
   - Updated API key

3. **`backend/app.py`**
   - Updated startup messages to reflect DeepSeek integration
   - Changed "OpenAI integration enabled" to "DeepSeek AI integration enabled"

## Configuration

### API Key
The DeepSeek API key is configured in the `AIContentGenerator` class:
```python
self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', 'sk-7169c5b77a904b539902f117a55abf01')
```

### Client Configuration
```python
self.client = OpenAI(
    api_key=self.api_key,
    base_url="https://api.deepseek.com/v1"
)
```

### Model
All API calls use the `deepseek-chat` model instead of OpenAI's `gpt-4o-mini`.

## Features Powered by DeepSeek
The application uses DeepSeek AI to generate:
1. **Professional Title** - Generates job titles based on job description and experience
2. **Professional Summary** - Creates tailored 3-4 sentence summaries
3. **Job Descriptions** - Generates detailed work experience descriptions (600-800 words for recent positions, 400-600 for older ones)
4. **Job Titles for Each Position** - Creates appropriate titles for each work experience entry

## Testing

### Test Script
Run the test script to verify DeepSeek connectivity:
```bash
python backend/test_openai.py
```

### Expected Output
```
============================================================
Testing DeepSeek API Connection
============================================================
[OK] DeepSeek client created successfully
[TEST] Testing API call...
[SUCCESS] DeepSeek API is working!
Response: Hello, DeepSeek is working!
[TEST] Testing resume title generation...
[SUCCESS] Generated Title: [Generated Title]
============================================================
[SUCCESS] ALL TESTS PASSED - DeepSeek API is working!
============================================================
```

## API Compatibility
DeepSeek's API is OpenAI-compatible, which means:
- Uses the same OpenAI Python SDK
- Same request/response format
- Only requires changing the `base_url` parameter
- Minimal code changes required for migration

## Benefits of DeepSeek
1. **Cost-Effective** - Generally lower cost than OpenAI
2. **High Performance** - Comparable quality for content generation
3. **Easy Migration** - OpenAI-compatible API makes switching seamless
4. **No Code Refactoring** - Uses the same `openai` Python package

## Fallback Behavior
If DeepSeek API fails for any reason, the application has fallback content generation:
- Pre-defined professional titles based on job description keywords
- Template-based summaries
- Structured job descriptions with detected technologies

## Environment Variables
You can set the DeepSeek API key via environment variable:
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

Or it will use the default key configured in the code.

## Future Considerations
1. Consider adding retry logic for API failures
2. Monitor API usage and costs
3. Implement rate limiting if needed
4. Consider caching frequently generated content
5. Add configuration file for easy API key management

## Support
- DeepSeek Platform: https://platform.deepseek.com/
- API Documentation: https://platform.deepseek.com/docs/
- Check API credits and billing in your DeepSeek account dashboard

---
*Last Updated: November 3, 2025*

