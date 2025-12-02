"""
Professional Content Generator for ATS-Optimized Resumes
Auto-generates professional summaries, job descriptions, and other content
"""
import re
from typing import List, Dict, Any
from datetime import datetime
from services.ai_content_generator import AIContentGenerator

class ContentGenerator:
    """Generates professional resume content based on job description and user inputs"""
    
    def __init__(self, ats_matcher, use_ai=True):
        self.ats_matcher = ats_matcher
        self.use_ai = use_ai
        if use_ai:
            self.ai_generator = AIContentGenerator()
        
    def calculate_years_experience(self, work_history: List[Dict]) -> int:
        """Calculate total years of experience from work history"""
        total_years = 0
        for exp in work_history:
            start = exp.get('start_date', '')
            end = exp.get('end_date', '')
            
            # Simple estimation based on year difference
            start_year = self._extract_year(start)
            end_year = self._extract_year(end) if end.lower() != 'present' else datetime.now().year
            
            if start_year and end_year:
                total_years += (end_year - start_year)
        
        return max(total_years, 10)  # Minimum 10 years for senior positions
    
    def _extract_year(self, date_str: str) -> int:
        """Extract year from date string"""
        match = re.search(r'\d{4}', date_str)
        return int(match.group()) if match else None
    
    def generate_professional_title(self, job_description: str, years_exp: int = 14) -> str:
        """Generate professional title based on job description"""
        if self.use_ai:
            try:
                return self.ai_generator.generate_professional_title(job_description, years_exp)
            except Exception as e:
                print(f"AI failed, using fallback: {e}")
        
        # Enhanced fallback - detect role from job description
        job_desc_lower = job_description.lower()
        seniority = "Senior"
        
        # Detect role type
        if any(word in job_desc_lower for word in ['liquidity', 'treasury', 'cash management']):
            role = "Liquidity Manager"
            specs = "Treasury & Risk Management | FX & Crypto Trading"
        elif any(word in job_desc_lower for word in ['data scien', 'machine learning', 'ml engineer']):
            role = "Data Scientist"
            specs = "Machine Learning | Analytics | AI"
        elif any(word in job_desc_lower for word in ['product manager', 'product owner']):
            role = "Product Manager"
            specs = "Strategy | Roadmap | Stakeholder Management"
        elif 'full stack' in job_desc_lower:
            role = "Full Stack Developer"
            specs = "Frontend & Backend | Cloud Architecture"
        else:
            role = "Professional"
            specs = "Leadership | Strategy | Operations"
        
        return f"{seniority} {role} | {specs}"
    
    def generate_professional_summary(self, job_description: str, work_history: List[Dict]) -> str:
        """Generate comprehensive professional summary"""
        years_exp = self.calculate_years_experience(work_history)
        
        if self.use_ai:
            return self.ai_generator.generate_professional_summary(job_description, years_exp, work_history)
        
        # Fallback
        keywords = self.ats_matcher.extract_keywords(job_description)
        job_desc_lower = job_description.lower()
        
        # Detect key technologies
        tech_stack = []
        if 'angular' in job_desc_lower:
            tech_stack.append("Angular")
        if '.net' in job_desc_lower or 'c#' in job_desc_lower:
            tech_stack.append(".NET (C#)")
        if 'react' in job_desc_lower:
            tech_stack.append("React")
        if 'node' in job_desc_lower:
            tech_stack.append("Node.js")
        
        tech_text = " and ".join(tech_stack) if tech_stack else "modern technologies"
        
        # Detect industries from job description
        industries = []
        if any(word in job_desc_lower for word in ['insurance', 'financial', 'finance', 'banking']):
            industries.extend(["finance", "insurance"])
        if any(word in job_desc_lower for word in ['healthcare', 'health', 'medical']):
            industries.append("healthcare")
        if any(word in job_desc_lower for word in ['ecommerce', 'e-commerce', 'retail']):
            industries.append("e-commerce")
        if any(word in job_desc_lower for word in ['gaming', 'game']):
            industries.append("gaming")
        
        if not industries:
            industries = ["finance", "healthcare", "gaming", "enterprise"]
        
        industries_text = ", ".join(industries[:4])
        
        # Detect key focus areas
        focus_areas = []
        if 'responsive' in job_desc_lower or 'ui' in job_desc_lower:
            focus_areas.append("responsive, high-performance web applications")
        if 'accessible' in job_desc_lower or 'accessibility' in job_desc_lower:
            focus_areas.append("accessible user interfaces")
        if 'scalable' in job_desc_lower or 'api' in job_desc_lower:
            focus_areas.append("scalable backend APIs")
        if 'architecture' in job_desc_lower or 'design' in job_desc_lower:
            focus_areas.append("clean, maintainable architectures")
        
        focus_text = ", ".join(focus_areas) if focus_areas else "responsive, high-performance web applications"
        
        # Detect cloud platform
        cloud_text = ""
        if 'aws' in job_desc_lower or 'amazon web services' in job_desc_lower:
            cloud_text = "cloud-ready solutions on AWS"
        elif 'azure' in job_desc_lower:
            cloud_text = "cloud-ready solutions on Azure"
        elif 'gcp' in job_desc_lower or 'google cloud' in job_desc_lower:
            cloud_text = "cloud-ready solutions on Google Cloud"
        else:
            cloud_text = "cloud-ready solutions"
        
        summary = (
            f"Full Stack Developer with over {years_exp}+ years of experience building {focus_text} "
            f"using {tech_text}. Skilled in designing {focus_text}, "
            f"and clean, maintainable architectures. Strong background in system design and cross-team collaboration, "
            f"with a track record of delivering {cloud_text} across {industries_text} platforms "
            f"used by millions of users."
        )
        
        return summary
    
    def generate_job_title(self, company_index: int, job_description: str, company_name: str, 
                           start_date: str = "", end_date: str = "") -> str:
        """Generate appropriate job title based on position in career"""
        if self.use_ai:
            years_at_company = 3  # Default estimate
            if start_date and end_date:
                start_year = self._extract_year(start_date)
                end_year = self._extract_year(end_date) if end_date.lower() != 'present' else datetime.now().year
                if start_year and end_year:
                    years_at_company = end_year - start_year
            
            return self.ai_generator.generate_job_title_for_position(
                job_description, company_name, company_index, years_at_company
            )
        
        # Fallback
        if company_index == 0:
            return "Senior Professional"
        elif company_index == 1:
            return "Senior Professional"
        elif company_index == 2:
            return "Professional"
        else:
            return "Associate Professional"
    
    def generate_job_description(self, company_index: int, company_name: str, 
                                 job_description: str, start_date: str, end_date: str, job_title: str = "") -> str:
        """Generate detailed, accomplishment-focused job description"""
        if self.use_ai:
            return self.ai_generator.generate_job_description(
                job_description, company_name, job_title, start_date, end_date, company_index
            )
        
        # Fallback
        job_desc_lower = job_description.lower()
        keywords = self.ats_matcher.extract_keywords(job_description)
        
        # Detect key technologies
        frontend_tech = []
        backend_tech = []
        cloud_tech = []
        other_tech = []
        
        if 'angular' in job_desc_lower:
            frontend_tech.extend(["Angular", "TypeScript", "SCSS", "NgRx"])
        if 'react' in job_desc_lower:
            frontend_tech.extend(["React", "Redux"])
        if '.net' in job_desc_lower or 'c#' in job_desc_lower:
            backend_tech.extend([".NET Core", "C#", "Entity Framework"])
        if 'node' in job_desc_lower:
            backend_tech.extend(["Node.js", "Express"])
        if 'aws' in job_desc_lower:
            cloud_tech.extend(["AWS", "Lambda", "S3", "CloudWatch"])
        if 'azure' in job_desc_lower:
            cloud_tech.extend(["Azure", "Azure Functions", "Application Insights"])
        if 'docker' in job_desc_lower or 'kubernetes' in job_desc_lower:
            other_tech.extend(["Docker", "Kubernetes"])
        if 'kafka' in job_desc_lower or 'messaging' in job_desc_lower:
            other_tech.extend(["Kafka", "SQS"])
        
        # Generate description based on company position
        descriptions = {
            0: self._generate_lead_description(company_name, frontend_tech, backend_tech, cloud_tech, other_tech, job_desc_lower),
            1: self._generate_senior_description(company_name, frontend_tech, backend_tech, cloud_tech, other_tech, job_desc_lower),
            2: self._generate_mid_description(company_name, frontend_tech, backend_tech, cloud_tech, other_tech, job_desc_lower),
            3: self._generate_developer_description(company_name, frontend_tech, backend_tech, cloud_tech, other_tech, job_desc_lower)
        }
        
        return descriptions.get(company_index, descriptions[3])
    
    def _generate_lead_description(self, company: str, frontend: List, backend: List, 
                                   cloud: List, other: List, job_desc: str) -> str:
        """Generate lead/senior engineer description"""
        frontend_str = ", ".join(frontend) if frontend else "Angular, TypeScript, SCSS, NgRx"
        backend_str = ", ".join(backend) if backend else ".NET Core, Entity Framework"
        cloud_str = ", ".join(cloud) if cloud else "AWS"
        
        industry_context = self._get_industry_context(company, job_desc)
        
        return (
            f"At {company}, {industry_context}. I architected and delivered large-scale Angular applications "
            f"using {frontend_str}, implementing micro-frontend architecture, reusable components, "
            f"and shared design systems to ensure consistency and maintainability across multiple products. "
            f"On the backend, I developed secure, scalable microservices and APIs using {backend_str}, "
            f"integrated into {cloud_str} using infrastructure as code. I designed event-driven workflows "
            f"with Kafka, SQS, and Lambda to support real-time operations and automated processing. "
            f"I also applied replication, sharding, and monitoring strategies across SQL Server and NoSQL systems "
            f"to maintain performance and reliability. Collaborating with AI/ML teams, I helped embed predictive models "
            f"and NLP services into dashboards and backend pipelines. I enforced WCAG accessibility standards, "
            f"implemented OAuth2 and JWT authentication, and improved observability using Prometheus, ELK Stack, "
            f"CloudWatch, and Lighthouse. I enhanced CI/CD pipelines with automated testing (Jest, Cypress, Playwright), "
            f"integrated into Jenkins, GitHub Actions, and {cloud_str} pipelines. In addition to technical leadership, "
            f"I defined architectural roadmaps, mentored engineers, and led reviews that ensured our platforms "
            f"remained secure, scalable, and user-centered."
        )
    
    def _generate_senior_description(self, company: str, frontend: List, backend: List,
                                     cloud: List, other: List, job_desc: str) -> str:
        """Generate senior engineer description"""
        frontend_str = ", ".join(frontend) if frontend else "Angular, TypeScript"
        backend_str = ", ".join(backend) if backend else "ASP.NET Core, C#"
        cloud_str = ", ".join(cloud) if cloud else "AWS"
        
        industry_context = self._get_industry_context(company, job_desc)
        
        return (
            f"At {company}, {industry_context}. On the frontend, I delivered Angular applications with TypeScript, "
            f"optimizing performance through modular design, lazy loading, and advanced caching strategies to maintain "
            f"responsiveness during high traffic. On the backend, I developed distributed microservices using {backend_str}, "
            f"applying load balancing, database sharding, Redis caching, and asynchronous pipelines with Kafka and SQS "
            f"to ensure reliability and scalability. I built real-time dashboards and customer-facing features using "
            f"SignalR and WebSockets, and collaborated with ML teams to integrate recommendation and detection models "
            f"into production systems, exposing them through secure APIs. To support reliability, I monitored system "
            f"performance with Prometheus, CloudWatch, and ELK. I enhanced deployment automation with CI/CD pipelines "
            f"using {cloud_str} and Jenkins, introduced automated rollback strategies, and contributed to architectural "
            f"roadmaps. In my senior role, I led design reviews, mentored engineers, and established best practices "
            f"that helped deliver secure, resilient, and user-focused experiences at scale."
        )
    
    def _generate_mid_description(self, company: str, frontend: List, backend: List,
                                  cloud: List, other: List, job_desc: str) -> str:
        """Generate mid-level developer description"""
        frontend_str = ", ".join(frontend) if frontend else "Angular"
        backend_str = ", ".join(backend) if backend else "ASP.NET Web API, Entity Framework"
        
        industry_context = self._get_industry_context(company, job_desc)
        
        return (
            f"At {company}, {industry_context}. I developed and optimized Angular portals for real-time data access "
            f"and secure operations, while also building and maintaining RESTful APIs using {backend_str} to connect "
            f"these portals to backend systems. To ensure compliance and security, I implemented secure authentication "
            f"with OAuth2 and JWT, strengthened data validation, and applied accessibility standards for inclusive design. "
            f"I enhanced performance with lazy loading, responsive layouts, and modular architecture, and created reporting "
            f"dashboards with D3.js and Chart.js to visualize data. I also contributed to refactoring legacy systems, "
            f"migrating applications to modern frameworks, and introducing automated testing practices with Jasmine and Karma. "
            f"To streamline operations, I supported CI/CD pipelines using Jenkins and Docker, which improved release reliability. "
            f"This role allowed me to apply advanced full stack engineering practices, balancing performance, security, and compliance."
        )
    
    def _generate_developer_description(self, company: str, frontend: List, backend: List,
                                       cloud: List, other: List, job_desc: str) -> str:
        """Generate developer/early career description"""
        frontend_str = ", ".join(frontend) if frontend else "Angular, TypeScript, HTML5, SCSS"
        backend_str = ", ".join(backend) if backend else "ASP.NET MVC, Web API"
        
        return (
            f"Transitioned from intern to full-time developer at {company}, taking on full stack responsibilities "
            f"with a strong focus on Angular for the frontend and .NET (C#) for backend development. Built responsive "
            f"and accessible web applications using {frontend_str}, and developed backend APIs and services using {backend_str}. "
            f"Designed reusable UI components, implemented state management, and optimized frontend performance through "
            f"lazy loading and module bundling. On the backend, contributed to SQL Server database design, query optimization, "
            f"and integration of business logic via Entity Framework. Helped modernize legacy systems, introduced unit testing "
            f"with NUnit and Jasmine, and supported CI/CD pipelines using Jenkins, Git, and Docker. Actively participated "
            f"in code reviews and cross-team knowledge sharing, contributing to consistent code quality and reliable deployments."
        )
    
    def _get_industry_context(self, company: str, job_desc: str) -> str:
        """Get industry-specific context"""
        company_lower = company.lower()
        
        if 'amazon' in company_lower:
            return "I worked on large-scale systems powering global e-commerce operations, building high-performance applications that supported order flows, payments, and fulfillment logistics across millions of daily transactions"
        elif any(word in company_lower for word in ['insurance', 'financial', 'symetra']):
            return "I led teams modernizing insurance platforms and customer-facing portals used by thousands of clients and internal stakeholders"
        elif any(word in company_lower for word in ['health', 'hospital', 'medical', 'circle']):
            return "I worked on applications that supported patient booking, billing, and electronic health records across a nationwide network of facilities"
        elif any(word in job_desc for word in ['gaming', 'game']):
            return "I contributed to gaming platforms and real-time multiplayer experiences"
        else:
            return "I worked on enterprise applications serving thousands of users across multiple business units"
    
    def generate_certifications(self, job_description: str) -> List[Dict]:
        """Generate relevant certifications"""
        job_desc_lower = job_description.lower()
        certs = []
        
        current_year = datetime.now().year
        
        if 'azure' in job_desc_lower or 'microsoft' in job_desc_lower:
            certs.append({
                "name": "Microsoft Certified: Azure Developer Associate (AZ-204)",
                "date": f"August, {current_year - 1}"
            })
        elif 'aws' in job_desc_lower:
            certs.append({
                "name": "AWS Certified Solutions Architect – Professional",
                "date": f"September, {current_year - 1}"
            })
        
        if 'angular' in job_desc_lower:
            certs.append({
                "name": "Angular – The Complete Guide (Udemy)",
                "date": f"May {current_year - 2}"
            })
        
        # Default certifications
        if not certs:
            certs = [
                {
                    "name": "Microsoft Certified: Azure Developer Associate (AZ-204)",
                    "date": f"August, {current_year - 1}"
                },
                {
                    "name": "Angular – The Complete Guide (Udemy)",
                    "date": f"May {current_year - 2}"
                }
            ]
        
        return certs
    
    def generate_education_details(self, education_data: List[Dict]) -> List[Dict]:
        """Enhance education data with professional details"""
        enhanced = []
        
        for edu in education_data:
            enhanced_edu = {
                'degree': edu.get('degree', ''),
                'school': edu.get('school', ''),
                'location': edu.get('location', ''),
                'year': edu.get('year', ''),
                'level': edu.get('level', '')
            }
            
            if edu.get('level') == 'masters':
                enhanced_edu['honors'] = "Merit (GPA: 3.7/4.0)"
                enhanced_edu['focus'] = "Focus on Web Application Development, Scalable Architectures, and Cloud-Based Systems"
            elif edu.get('level') == 'bachelors':
                enhanced_edu['honors'] = "First-Class Honours (GPA: 3.8/4.0)"
                enhanced_edu['focus'] = "Focus on Software Engineering, Distributed Systems, and Security"
            
            enhanced.append(enhanced_edu)
        
        return enhanced
    
    def generate_full_resume_data(self, user_data: Dict, job_description: str) -> Dict:
        """Generate complete resume with all auto-generated content"""
        work_experience = user_data.get('work_experience', [])
        
        # Calculate years of experience
        years_exp = self.calculate_years_experience(work_experience)
        
        # Generate skills using AI for better extraction
        if self.use_ai:
            print("[AI] Extracting skills using AI...")
            suggested_skills = self.ai_generator.extract_skills_from_jd(job_description)
            # Add user's existing skills that might not be in JD
            user_skills = user_data.get('skills', [])
            for skill in user_skills:
                if skill not in suggested_skills:
                    suggested_skills.append(skill)
        else:
            # Fallback to regex-based extraction
            suggested_skills = self.ats_matcher.get_relevant_skills(job_description)
        
        # ⚡ FASTEST: Use PARALLEL API calls (all at once, much faster!)
        if self.use_ai:
            print(f"⚡ PARALLEL MODE: Generating ALL content with simultaneous API calls...")
            ai_content = self.ai_generator.generate_complete_resume_content_parallel(
                job_description, 
                years_exp, 
                work_experience
            )
            
            if ai_content:
                # Successfully generated everything with parallel calls!
                print(f"✅ SUCCESS: Generated resume using PARALLEL method!")
                
                # Build work experience from AI response
                detailed_experience = []
                for idx, ai_exp in enumerate(ai_content.get('work_experiences', [])):
                    if idx < len(work_experience):
                        detailed_experience.append({
                            'title': ai_exp.get('job_title', ''),
                            'company': work_experience[idx].get('company', ''),
                            'location': work_experience[idx].get('location', ''),
                            'start_date': work_experience[idx].get('start_date', ''),
                            'end_date': work_experience[idx].get('end_date', ''),
                            'description': ai_exp.get('description', '')
                        })
                
                professional_title = ai_content.get('professional_title', '')
                professional_summary = ai_content.get('professional_summary', '')
            else:
                # Fallback to sequential calls if parallel method fails
                print(f"⚠️ Parallel method failed, using fallback (sequential API calls)...")
                professional_title = self.generate_professional_title(job_description, years_exp)
                professional_summary = self.generate_professional_summary(job_description, work_experience)
                
                # Generate detailed work experience
                detailed_experience = []
                for idx, exp in enumerate(work_experience):
                    job_title = self.generate_job_title(
                        idx, 
                        job_description, 
                        exp.get('company', ''),
                        exp.get('start_date', ''),
                        exp.get('end_date', '')
                    )
                    description = self.generate_job_description(
                        idx, 
                        exp.get('company', ''),
                        job_description,
                        exp.get('start_date', ''),
                        exp.get('end_date', ''),
                        job_title
                    )
                    
                    detailed_experience.append({
                        'title': job_title,
                        'company': exp.get('company', ''),
                        'location': exp.get('location', ''),
                        'start_date': exp.get('start_date', ''),
                        'end_date': exp.get('end_date', ''),
                        'description': description
                    })
        else:
            # Non-AI fallback
            professional_title = self.generate_professional_title(job_description, years_exp)
            professional_summary = self.generate_professional_summary(job_description, work_experience)
            
            detailed_experience = []
            for idx, exp in enumerate(work_experience):
                job_title = self.generate_job_title(
                    idx, 
                    job_description, 
                    exp.get('company', ''),
                    exp.get('start_date', ''),
                    exp.get('end_date', '')
                )
                description = self.generate_job_description(
                    idx, 
                    exp.get('company', ''),
                    job_description,
                    exp.get('start_date', ''),
                    exp.get('end_date', ''),
                    job_title
                )
                
                detailed_experience.append({
                    'title': job_title,
                    'company': exp.get('company', ''),
                    'location': exp.get('location', ''),
                    'start_date': exp.get('start_date', ''),
                    'end_date': exp.get('end_date', ''),
                    'description': description
                })
        
        # Generate certifications
        certifications = self.generate_certifications(job_description)
        
        # Enhance education
        education = self.generate_education_details(user_data.get('education', []))
        
        # Default languages
        languages = user_data.get('languages', ['English (Professional)'])
        
        # Build complete resume data
        resume_data = {
            'personal_info': {
                **user_data.get('personal_info', {}),
                'title': professional_title
            },
            'professional_summary': professional_summary,
            'skills': suggested_skills,
            'work_experience': detailed_experience,
            'certifications': certifications,
            'education': education,
            'languages': languages,
            'projects': []  # Empty for now, can be added later
        }
        
        return resume_data

