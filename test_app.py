"""
Test script for ATS Resume Generator
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.data_service import DataService
from services.ats_matcher import ATSMatcher
from services.pdf_generator import PDFGenerator

def test_ats_resume_generator():
    """Test the resume generator with sample data"""
    
    print("=" * 60)
    print("Testing ATS Resume Generator")
    print("=" * 60)
    print()
    
    # Sample job description
    job_description = """
    We are looking for a Senior Full Stack Developer with expertise in Angular and .NET.
    
    Requirements:
    - 5+ years of experience with Angular (v14+) and TypeScript
    - Strong backend development skills with .NET Core and C#
    - Experience with ASP.NET Web API and Entity Framework
    - Proficiency in SQL Server and database design
    - Experience with Azure cloud services
    - Knowledge of Docker and Kubernetes
    - Strong understanding of microservices architecture
    - Experience with CI/CD pipelines (Azure DevOps, GitHub Actions)
    - Excellent problem-solving and communication skills
    
    Nice to have:
    - Experience with React or Vue.js
    - Knowledge of AWS or Google Cloud Platform
    - Experience with Redis caching
    - Familiarity with SignalR for real-time applications
    """
    
    # Sample user data (based on the provided example)
    user_data = {
        'personal_info': {
            'name': 'Adrian Kowalewski',
            'title': 'Senior Full Stack Developer | Angular Frontend & .NET Backend | Scalable Architecture | Responsive Design | Microservice Architecture | API & UI Engineering | Performance Optimization',
            'address': '134 Albert Road, Plymouth, UK',
            'email': 'kowalewskiadrian0502@gmail.com',
            'phone': '+44 7868 332982',
            'linkedin': 'https://linkedin.com/in/adriankowalewski'
        },
        'professional_summary': 'Full Stack Developer with over 14+ years of experience building responsive, high-performance web applications using Angular and .NET (C#). Skilled in designing accessible user interfaces, scalable backend APIs, and clean, maintainable architectures. Strong background in system design and cross-team collaboration, with a track record of delivering cloud-ready solutions across gaming, healthcare, finance, and enterprise platforms used by millions of users.',
        'skills': [
            'C#', '.NET Core', '.NET Framework', 'ASP.NET MVC', 'ASP.NET Web API', 
            'Entity Framework', 'Angular', 'TypeScript', 'JavaScript'
        ],
        'work_experience': [
            {
                'title': 'Lead Full Stack Engineer',
                'company': 'Symetra',
                'location': 'Bellevue, WA',
                'start_date': 'January 2022',
                'end_date': 'Present',
                'description': 'At Symetra, I led teams modernizing insurance platforms and customer-facing portals used by thousands of clients and internal stakeholders. I architected and delivered large-scale Angular applications using TypeScript, SCSS, and NgRx, implementing micro-frontend architecture, reusable components, and shared design systems to ensure consistency and maintainability across multiple products. On the backend, I developed secure, scalable microservices and APIs using .NET Core and Entity Framework, integrated into AWS using CDK for infrastructure as code. I designed event-driven workflows with Kafka, SQS, and AWS Lambda to support real-time operations and automated claims processing. I also applied replication, sharding, and monitoring strategies across SQL Server and NoSQL systems to maintain performance and reliability. Collaborating with AI/ML teams, I helped embed predictive models and NLP services into Angular dashboards and backend pipelines to enable intelligent document classification and fraud detection. I enforced WCAG accessibility standards, implemented OAuth2 and JWT authentication, and improved observability using Prometheus, ELK Stack, CloudWatch, and Lighthouse.'
            },
            {
                'title': 'Senior Full Stack Engineer',
                'company': 'Amazon',
                'location': 'Seattle, WA',
                'start_date': 'January 2018',
                'end_date': 'December 2021',
                'description': 'At Amazon, I worked on large-scale systems powering global e-commerce operations, building high-performance single-page applications and backend services that supported order flows, payments, and fulfillment logistics across millions of daily transactions. On the frontend, I delivered Angular applications with TypeScript, optimizing performance through modular design, lazy loading, and advanced caching strategies to maintain responsiveness during massive traffic spikes like Prime Day. On the backend, I developed distributed microservices using ASP.NET Core and C#, applying load balancing, database sharding, Redis caching, and asynchronous pipelines with Kafka and SQS to ensure reliability and scalability. I built real-time dashboards and customer-facing features using SignalR and WebSockets, and collaborated with ML teams to integrate recommendation, ranking, and fraud detection models into production systems, exposing them through secure APIs.'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'Circle Health Group',
                'location': 'London, UK',
                'start_date': 'January 2015',
                'end_date': 'December 2017',
                'description': 'Developed and optimized Angular portals for real-time appointment scheduling and secure clinical data access. Built RESTful APIs using ASP.NET Web API and Entity Framework.'
            }
        ],
        'projects': [
            {
                'name': 'Healthcare Management System',
                'description': 'Built comprehensive patient management system with Angular frontend and .NET backend',
                'technologies': 'Angular, .NET Core, SQL Server, Azure',
                'url': 'https://github.com/example/project'
            }
        ],
        'certifications': [
            {
                'name': 'Microsoft Certified: Azure Developer Associate (AZ-204)',
                'issuer': 'Microsoft',
                'date': 'August 2024'
            },
            {
                'name': 'Angular – The Complete Guide (Udemy)',
                'issuer': 'Udemy',
                'date': 'May 2023'
            }
        ],
        'education': [
            {
                'institution': 'UNIVERSITY COLLEGE LONDON, London, England',
                'degree': 'Master of Science',
                'field': 'Computer Science / Information System',
                'start_date': '2015',
                'end_date': '2018',
                'gpa': 'Merit (GPA: 3.7/4.0)',
                'description': 'Focus on Web Application Development, Scalable Architectures, and Cloud-Based Systems'
            },
            {
                'institution': 'UNIVERSITY OF OXFORD, Oxford, England',
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'start_date': '2006',
                'end_date': '2009',
                'gpa': 'First-Class Honours (GPA: 3.8/4.0)',
                'description': 'Focus on Software Engineering, Distributed Systems, and Security'
            }
        ]
    }
    
    # Test 1: ATS Matcher
    print("Test 1: Testing ATS Keyword Matcher")
    print("-" * 60)
    ats_matcher = ATSMatcher()
    
    keywords = ats_matcher.extract_keywords(job_description)
    print(f"[OK] Extracted {len(keywords)} keywords from job description")
    print(f"  Sample keywords: {', '.join(keywords[:10])}")
    print()
    
    relevant_skills = ats_matcher.get_relevant_skills(job_description)
    print(f"[OK] Generated {len(relevant_skills)} relevant skills")
    print(f"  Sample skills: {', '.join(relevant_skills[:15])}")
    print()
    
    # Test 2: Content Optimization
    print("Test 2: Testing Resume Content Optimization")
    print("-" * 60)
    optimized_data = ats_matcher.optimize_resume_content(user_data, job_description)
    print(f"[OK] Optimized resume data")
    print(f"[OK] Total skills in optimized resume: {len(optimized_data['skills'])}")
    print(f"[OK] Work experience entries: {len(optimized_data['work_experience'])}")
    print()
    
    # Test 3: Data Service
    print("Test 3: Testing Data Persistence")
    print("-" * 60)
    data_service = DataService('data/test_user_data.json')
    
    data_service.save_user_data(user_data)
    print("[OK] Successfully saved user data")
    
    loaded_data = data_service.load_user_data()
    print("[OK] Successfully loaded user data")
    print(f"[OK] Loaded user: {loaded_data['personal_info']['name']}")
    print()
    
    # Test 4: PDF Generation
    print("Test 4: Testing PDF Generation")
    print("-" * 60)
    pdf_generator = PDFGenerator()
    
    pdf_path = pdf_generator.generate_pdf(optimized_data)
    print(f"[OK] Successfully generated PDF resume")
    print(f"[OK] PDF saved to: {pdf_path}")
    
    # Check if file exists and has content
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"[OK] PDF file size: {file_size:,} bytes")
    else:
        print("[FAIL] PDF file was not created")
        return False
    
    print()
    print("=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Your ATS Resume Generator is working correctly!")
    print()
    print("To use the application:")
    print("1. Run 'python backend/app.py' to start the backend server")
    print("2. Open 'frontend/index.html' in your web browser")
    print("3. Fill in your information and job description")
    print("4. Click 'Generate Resume PDF' to create your resume")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_ats_resume_generator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

