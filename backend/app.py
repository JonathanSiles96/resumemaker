"""
Main Flask application for ATS Resume Generator
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from services.data_service import DataService
from services.ats_matcher import ATSMatcher
from services.pdf_generator import PDFGenerator
from services.content_generator import ContentGenerator
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize services
data_service = DataService()
ats_matcher = ATSMatcher()
pdf_generator = PDFGenerator()
content_generator = ContentGenerator(ats_matcher, use_ai=True)

print("=" * 60)
print("🤖 AI-POWERED RESUME GENERATOR")
print("=" * 60)
print("✓ DeepSeek AI integration enabled")
print("✓ Content will be generated based on job descriptions")
print("=" * 60)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Resume Generator API is running'})

@app.route('/api/save-data', methods=['POST'])
def save_data():
    """Save user resume data"""
    try:
        data = request.json
        data_service.save_user_data(data)
        return jsonify({'success': True, 'message': 'Data saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load-data', methods=['GET'])
def load_data():
    """Load saved user resume data"""
    try:
        data = data_service.load_user_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze-job', methods=['POST'])
def analyze_job():
    """Analyze job description and extract keywords"""
    try:
        data = request.json
        job_description = data.get('job_description', '')
        
        # Extract keywords and skills from job description
        keywords = ats_matcher.extract_keywords(job_description)
        suggested_skills = ats_matcher.get_relevant_skills(job_description)
        
        return jsonify({
            'success': True,
            'keywords': keywords,
            'suggested_skills': suggested_skills
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/all-keywords', methods=['GET'])
def get_all_keywords():
    """Get all available keywords/skills in the database"""
    try:
        all_keywords = sorted(list(ats_matcher.tech_skills_database))
        return jsonify({
            'success': True,
            'keywords': all_keywords,
            'total': len(all_keywords)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    """Generate ATS-optimized PDF resume with auto-generated content"""
    try:
        data = request.json
        job_description = data.get('job_description', '')
        user_data = data.get('user_data', {})
        
        print("\n" + "=" * 60)
        print("🔄 GENERATING RESUME WITH AI")
        print("=" * 60)
        print(f"Job Description Length: {len(job_description)} characters")
        print(f"Job Description Preview: {job_description[:200]}...")
        print(f"Companies: {[exp.get('company') for exp in user_data.get('work_experience', [])]}")
        
        # Auto-generate all professional content
        print("\n🤖 Calling AI to generate content...")
        complete_resume_data = content_generator.generate_full_resume_data(user_data, job_description)
        
        print(f"\n✅ AI Generated:")
        print(f"   Title: {complete_resume_data['personal_info'].get('title', '')[:80]}...")
        print(f"   Summary: {complete_resume_data.get('professional_summary', '')[:80]}...")
        print(f"   Work Experiences: {len(complete_resume_data.get('work_experience', []))}")
        for i, exp in enumerate(complete_resume_data.get('work_experience', [])):
            print(f"     {i+1}. {exp.get('title')} at {exp.get('company')}")
        
        # Generate PDF
        print("\n📄 Generating PDF...")
        pdf_path = pdf_generator.generate_pdf(complete_resume_data)
        print(f"✅ PDF created: {pdf_path}")
        print("=" * 60 + "\n")
        
        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Resume_{complete_resume_data['personal_info']['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    # use_reloader=False to fix Windows socket issue
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

