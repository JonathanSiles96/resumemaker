"""
AI-Powered Content Generator using DeepSeek API
Generates contextually relevant resume content based on job descriptions
"""
from openai import OpenAI
from typing import List, Dict, Any
import os
import json
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class AIContentGenerator:
    """Uses DeepSeek API to generate highly relevant resume content"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', 'sk-7169c5b77a904b539902f117a55abf01')
        # DeepSeek API is OpenAI-compatible, just needs a different base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"
        )
    
    def _clean_preamble(self, text: str) -> str:
        """Remove conversational preamble from AI responses"""
        # Common phrases to remove
        preamble_patterns = [
            "Of course. ",
            "Of course! ",
            "Sure. ",
            "Sure! ",
            "Here is ",
            "Here's ",
            "Here is a ",
            "Here's a ",
            "The ",
            "This is ",
            "Below is ",
        ]
        
        # Remove leading conversational text
        for pattern in preamble_patterns:
            if text.startswith(pattern):
                text = text[len(pattern):]
        
        # Remove patterns like "Here is a professional summary:" or "Professional Summary:"
        text = re.sub(r'^[^:]+:\s*\*?\*?\*?\s*', '', text, flags=re.IGNORECASE)
        
        # Remove leading/trailing quotes and asterisks
        text = text.strip('"\'*').strip()
        
        # If there's a clear break (double newline or ***), take only the content after it
        if '***' in text:
            parts = text.split('***')
            # Find the longest part (usually the actual content)
            text = max(parts, key=len).strip()
        
        # Remove any remaining leading labels like "Professional Summary:" 
        text = re.sub(r'^\*?\*?Professional (Title|Summary|Description):\*?\*?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\*?\*?Job (Title|Description):\*?\*?\s*', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_skills_from_jd(self, job_description: str) -> List[str]:
        """
        Use AI to intelligently extract comprehensive list of technical skills from job description
        
        Args:
            job_description: The job description text
            
        Returns:
            List of 100+ clean technical skills
        """
        prompt = f"""Analyze this job description and generate a COMPREHENSIVE list of 100-150 technical skills that would be relevant for this role.

Job Description:
{job_description}

CRITICAL INSTRUCTIONS:
1. Extract ALL skills explicitly mentioned in the JD
2. Add all RELATED skills in the same technology ecosystem (e.g., if "React" is mentioned, include "Redux", "React Router", "JSX", "Hooks", etc.)
3. Include related tools, frameworks, libraries, databases, cloud services, methodologies
4. Include both specific technologies AND general concepts (e.g., "AWS Lambda" AND "Serverless Architecture")
5. Target 100-150 total skills for optimal ATS matching

INCLUDE:
- Programming languages & their ecosystems
- Frameworks, libraries, tools
- Databases (SQL & NoSQL)
- Cloud platforms & services
- DevOps tools, CI/CD
- Testing frameworks
- Architecture patterns
- Methodologies (Agile, Scrum, etc.)
- Security concepts
- Related soft skills (Leadership, Mentoring, Code Review, etc.)

DO NOT INCLUDE:
- Job titles, company names, locations
- Words like "strong", "able", "comfortable", "how", "send", "two"
- Salary, benefits, application instructions
- Generic verbs without technical context

EXAMPLES:
If JD mentions "React":
Include: React, Redux, React Router, React Hooks, JSX, Component Lifecycle, Virtual DOM, Context API, React Testing Library, Jest

If JD mentions "AWS":
Include: AWS, EC2, S3, Lambda, RDS, DynamoDB, CloudFront, API Gateway, CloudFormation, Terraform, IAC

If JD mentions "Node.js":
Include: Node.js, Express.js, npm, JavaScript, TypeScript, REST API, GraphQL, Microservices, Event-Driven Architecture

IMPORTANT LIMITS:
- Maximum 200 skills total
- Only include skills that are RELEVANT to this job description
- Focus on quality over quantity
- Prioritize skills explicitly mentioned in the JD
- Add closely related/complementary skills only if they make sense for this role

Format: Return ONLY a comma-separated list (no explanations, no introductions)

Return the comma-separated list of up to 200 skills:"""

        try:
            print("[AI] Extracting skills list from JD (targeting ~200 skills max)...")
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,  # Enough for up to 200 skills
                temperature=0.4  # Lower temperature for more focused matching
            )
            
            skills_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            skills_text = self._clean_preamble(skills_text)
            
            # Parse comma-separated list
            skills = [s.strip() for s in skills_text.split(',') if s.strip()]
            
            # Filter out any remaining garbage (extra safety)
            garbage_words = {'strong', 'able', 'comfortable', 'bonus', 'how', 'send', 'two', 'the', 
                           'you', 'they', 'what', 'who', 'when', 'where', 'why', 'this', 'that',
                           'location', 'remote', 'salary', 'interview', 'process', 'details',
                           'start', 'date', 'asap', 'industry', 'work', 'expect', 'applying'}
            
            skills = [s for s in skills if s.lower() not in garbage_words and len(s) > 1]
            
            # CAP at 200 skills maximum as requested by user
            if len(skills) > 200:
                print(f"[INFO] AI extracted {len(skills)} skills, capping at 200 most relevant")
                skills = skills[:200]
            
            print(f"[SUCCESS] AI extracted {len(skills)} clean skills matching JD")
            print(f"   First 10: {', '.join(skills[:10])}...")
            
            # Only add common skills if we have very few (less than 50)
            if len(skills) < 50:
                print(f"[INFO] Only {len(skills)} skills extracted, adding some common related skills...")
                common_skills = self._get_common_tech_skills()
                for skill in common_skills:
                    if skill not in skills and len(skills) < 200:
                        skills.append(skill)
                print(f"[INFO] Extended to {len(skills)} skills")
            
            return skills
            
        except Exception as e:
            print(f"[ERROR] Error extracting skills with AI: {e}")
            # Fallback to common skills (capped at 200)
            return self._get_common_tech_skills()[:200]
    
    def _get_common_tech_skills(self) -> List[str]:
        """Return a comprehensive list of common technical skills"""
        return [
            # Core Programming Languages
            'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'Go', 'Rust', 'Ruby', 'PHP',
            'Swift', 'Kotlin', 'Scala', 'R', 'SQL', 'HTML5', 'CSS3', 'SCSS', 'SASS',
            
            # Frontend Frameworks & Libraries
            'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte', 'Redux', 'MobX', 'Vuex',
            'React Router', 'React Hooks', 'Context API', 'JSX', 'Webpack', 'Vite', 'Babel',
            'Tailwind CSS', 'Bootstrap', 'Material UI', 'Styled Components', 'jQuery',
            
            # Backend Frameworks
            'Node.js', 'Express.js', 'Nest.js', 'Django', 'Flask', 'FastAPI', 'Spring Boot',
            'ASP.NET Core', '.NET Framework', 'Entity Framework', 'Ruby on Rails', 'Laravel',
            
            # Databases
            'PostgreSQL', 'MySQL', 'SQL Server', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB',
            'Cassandra', 'Oracle', 'SQLite', 'Firebase', 'Neo4j', 'CouchDB',
            
            # Cloud Platforms
            'AWS', 'Azure', 'Google Cloud Platform', 'GCP', 'Heroku', 'Vercel', 'Netlify',
            'EC2', 'S3', 'Lambda', 'RDS', 'CloudFront', 'API Gateway', 'CloudFormation',
            'Azure Functions', 'Azure DevOps', 'Cloud Functions', 'BigQuery',
            
            # DevOps & CI/CD
            'Docker', 'Kubernetes', 'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'Helm', 'Docker Compose',
            
            # Version Control & Collaboration
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial',
            
            # APIs & Architecture
            'REST API', 'RESTful Services', 'GraphQL', 'gRPC', 'SOAP', 'WebSockets',
            'Microservices', 'Serverless Architecture', 'Event-Driven Architecture',
            'Domain-Driven Design', 'Clean Architecture', 'MVC', 'MVVM',
            
            # Testing
            'Jest', 'Mocha', 'Chai', 'Jasmine', 'Cypress', 'Selenium', 'Playwright',
            'JUnit', 'TestNG', 'PyTest', 'Unit Testing', 'Integration Testing', 'E2E Testing',
            'Test-Driven Development', 'TDD', 'Behavior-Driven Development', 'BDD',
            
            # Monitoring & Logging
            'Prometheus', 'Grafana', 'ELK Stack', 'Elasticsearch', 'Logstash', 'Kibana',
            'CloudWatch', 'Application Insights', 'New Relic', 'DataDog', 'Sentry',
            
            # Security
            'OAuth', 'OAuth2', 'JWT', 'SAML', 'SSL/TLS', 'HTTPS', 'Encryption',
            'Authentication', 'Authorization', 'RBAC', 'OWASP', 'Security Best Practices',
            
            # Methodologies
            'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD', 'Continuous Integration',
            'Continuous Deployment', 'Code Review', 'Pair Programming', 'TDD',
            
            # Soft Skills & Leadership
            'Team Leadership', 'Mentoring', 'Cross-Functional Collaboration',
            'Technical Documentation', 'Problem Solving', 'System Design',
            'Performance Optimization', 'Code Quality', 'Best Practices',
            
            # Additional Tools
            'npm', 'yarn', 'pip', 'Maven', 'Gradle', 'Postman', 'Swagger', 'Jira',
            'Confluence', 'Slack', 'VS Code', 'IntelliJ IDEA', 'Visual Studio'
        ]
    
    def generate_professional_title(self, job_description: str, years_experience: int) -> str:
        """Generate professional title matching the job description"""
        prompt = f"""Generate a professional resume title for this job description. The candidate has {years_experience}+ years of experience.

Job Description:
{job_description}

CRITICAL INSTRUCTIONS:
- Return ONLY the professional title itself, nothing else
- No explanations, no introductions, no "Here is..." or "Of course..."
- Maximum 120 characters
- Format: "Senior [Role] | [Key Skills] | [Specializations]"
- Example format: "Senior Liquidity Manager | Treasury & Risk Management | FX & Crypto Trading"

Return the title directly:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            title = response.choices[0].message.content.strip().strip('"')
            
            # Clean up any conversational preamble
            title = self._clean_preamble(title)
            
            print(f"AI Generated Title (DeepSeek): {title}")  # Debug
            return title
        except Exception as e:
            print(f"Error generating title with DeepSeek: {e}")
            return f"Senior Professional with {years_experience}+ Years Experience"
    
    def generate_professional_summary(self, job_description: str, years_experience: int, 
                                     company_history: List[Dict]) -> str:
        """Generate professional summary matching the job description"""
        companies = ", ".join([c.get('company', '') for c in company_history[:4] if c.get('company')])
        
        prompt = f"""Generate a professional summary for this job description. The candidate has {years_experience}+ years of experience and previously worked at: {companies}

Job Description:
{job_description}

CRITICAL INSTRUCTIONS:
- Return ONLY the professional summary itself, nothing else
- No explanations, no introductions, no "Here is...", no "Of course...", no "Professional Summary:" label
- Write 3-4 sentences showing the candidate is perfect for THIS specific job
- Focus on skills and experience mentioned in the job description
- Start directly with the summary content

Return the summary directly:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.7
            )
            summary = response.choices[0].message.content.strip()
            
            # Clean up any conversational preamble
            summary = self._clean_preamble(summary)
            
            print(f"AI Generated Summary (DeepSeek): {summary[:100]}...")  # Debug
            return summary
        except Exception as e:
            print(f"Error generating summary with DeepSeek: {e}")
            return f"Experienced professional with {years_experience}+ years in the industry, bringing expertise across various domains and technologies."
    
    def generate_job_description(self, job_posting: str, company_name: str, job_title: str,
                                 start_date: str, end_date: str, position_index: int) -> str:
        """Generate detailed job description that matches the target role"""
        
        word_count = "600-800 words" if position_index < 2 else "400-600 words"
        
        prompt = f"""Generate a professional job summary for this company position that matches the target job description.

TARGET JOB DESCRIPTION:
{job_posting}

MY POSITION:
Company: {company_name}
Job Title: {job_title}
Dates: {start_date} - {end_date}

CRITICAL INSTRUCTIONS:
- Return ONLY the job description itself, nothing else
- No explanations, no introductions, no "Here is...", no "Of course...", no asterisks (***), no labels
- Write {word_count} showing relevant experience for the TARGET JOB
- Start DIRECTLY with "At {company_name}," (no preamble before this)
- Write as one flowing paragraph in first person past tense (I managed, I developed, etc.)
- Use skills and terminology from the job description
- NO bullet points

Return the description directly, starting with "At {company_name},":"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.7
            )
            description = response.choices[0].message.content.strip()
            
            # Clean up any conversational preamble
            description = self._clean_preamble(description)
            
            # Clean up any unwanted formatting
            description = description.replace('\n\n', ' ').replace('\n', ' ')
            
            # Remove any asterisks or markdown
            description = description.replace('***', '').replace('**', '').strip()
            
            print(f"AI Generated Job Desc (DeepSeek) for {company_name}: {description[:100]}...")  # Debug
            return description
        except Exception as e:
            print(f"Error generating job description with DeepSeek for {company_name}: {e}")
            return f"At {company_name}, I contributed to various projects and initiatives, applying technical and professional skills to deliver results."
    
    def generate_job_title_for_position(self, job_posting: str, company_name: str, 
                                       position_index: int, years_at_company: int) -> str:
        """Generate appropriate job title for this position"""
        
        # IMPORTANT: Earlier positions (higher index) should be MORE JUNIOR
        # position_index 0 = Most Recent (Current) = Senior
        # position_index 1, 2 = Mid-career = Mid-level  
        # position_index 3+ = Earliest/Oldest = Junior (entry level)
        
        if position_index == 0:
            seniority = "Senior"
            seniority_instruction = "This is the MOST RECENT position. Use SENIOR level title (Senior, Lead, Principal, Staff)"
        elif position_index == 1:
            seniority = "Mid-level"
            seniority_instruction = "This is a MID-CAREER position. Use MID-LEVEL title (no Senior prefix, no Junior prefix)"
        elif position_index == 2:
            seniority = "Mid-level"
            seniority_instruction = "This is a MID-CAREER position. Use MID-LEVEL title (no Senior prefix, no Junior prefix)"
        else:
            seniority = "Junior"
            seniority_instruction = "This is the EARLIEST/OLDEST position (career start). MUST use JUNIOR level title (Junior, Associate, Software Engineer I/II, or just the role without Senior/Lead)"
        
        recency = "most recent position" if position_index == 0 else f"position {position_index + 1} (older/earlier role)"
        
        prompt = f"""Generate a job title for this position that matches this job description.

Target Job Description:
{job_posting}

Position Details:
- Company: {company_name}
- Career Stage: {recency}
- Duration: {years_at_company} years
- Position Number: {position_index + 1}

CRITICAL SENIORITY REQUIREMENT:
{seniority_instruction}

CRITICAL INSTRUCTIONS:
- Return ONLY the job title itself, nothing else
- No explanations, no introductions, no "Here is...", no "Of course..."
- One line only
- Make the role match the industry/field in the job description
- STRICTLY follow the seniority level requirement above
- For Junior positions: Use "Junior", "Associate", or plain role name WITHOUT "Senior"
- For Mid-level: Use plain role name WITHOUT "Senior" or "Junior"
- For Senior positions: Use "Senior", "Lead", "Principal", or "Staff"

Return the job title directly:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            title = response.choices[0].message.content.strip().strip('"\'')
            
            # Clean up any conversational preamble
            title = self._clean_preamble(title)
            
            print(f"AI Generated Job Title (DeepSeek) for {company_name}: {title}")  # Debug
            return title
        except Exception as e:
            print(f"Error generating job title with DeepSeek for {company_name}: {e}")
            return f"{seniority} Professional"
    
    def generate_complete_resume_content(self, job_description: str, years_experience: int, 
                                         work_history: List[Dict]) -> Dict[str, Any]:
        """
        🚀 OPTIMIZED: Generate ALL resume content in ONE API call (2-3 seconds instead of 20-30 seconds)
        Returns: {
            'professional_title': str,
            'professional_summary': str,
            'work_experiences': [
                {'job_title': str, 'company': str, 'description': str},
                ...
            ]
        }
        """
        companies = ", ".join([exp.get('company', '') for exp in work_history if exp.get('company')])
        
        # Build work history details for the prompt
        work_history_details = []
        for idx, exp in enumerate(work_history):
            company = exp.get('company', f'Company {idx+1}')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', 'Present')
            location = exp.get('location', '')
            seniority = "Senior" if idx == 0 else ("Mid-level" if idx < 3 else "Junior")
            recency = "most recent" if idx == 0 else f"position #{idx + 1}"
            word_count = "600-800 words" if idx < 2 else "400-600 words"
            
            work_history_details.append(f"""
Position {idx + 1} ({recency}):
- Company: {company}
- Location: {location}
- Dates: {start_date} - {end_date}
- Seniority: {seniority}
- Description length: {word_count}
""")
        
        work_history_text = "\n".join(work_history_details)
        
        prompt = f"""You are a professional resume writer. Generate a complete, ATS-optimized resume content based on the target job description below.

TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
- Years of Experience: {years_experience}+ years
- Companies worked at: {companies}

WORK HISTORY TO GENERATE CONTENT FOR:
{work_history_text}

Generate the following in VALID JSON format:
{{
  "professional_title": "A compelling professional title (120 chars max). Format: 'Senior [Role] | [Key Skills] | [Specializations]'",
  "professional_summary": "A 3-4 sentence professional summary highlighting how the candidate is perfect for the target job. Focus on skills and technologies mentioned in the job description.",
  "work_experiences": [
    {{
      "job_title": "Job title for position 1 that matches the target job field/industry",
      "company": "{work_history[0].get('company', '')}",
      "description": "For position 1 (most recent): Write 600-800 words. Start with 'At [company],' and write a flowing paragraph in first person past tense showing how this experience demonstrates the candidate is perfect for the target job. Use terminology and skills from the job description. NO bullet points."
    }},
    ... (continue for all positions in work history)
  ]
}}

IMPORTANT: 
- Return ONLY valid JSON, no markdown, no explanations
- Match job titles and descriptions to the TARGET JOB field/industry
- Use skills and terminology from the TARGET JOB DESCRIPTION
- Make the candidate look perfect for the TARGET JOB
- Recent positions get 600-800 words, older ones get 400-600 words
- All descriptions must be flowing paragraphs in first person past tense, NO bullet points

JSON:"""

        try:
            print(f"🚀 Generating ALL content in one API call...")
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,  # Increased for all content
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            print(f"✅ Generated ALL content in ONE call!")
            print(f"   Title: {result.get('professional_title', '')[:80]}...")
            print(f"   Summary: {result.get('professional_summary', '')[:80]}...")
            print(f"   Work Experiences: {len(result.get('work_experiences', []))}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            # Fall back to individual calls
            return None
        except Exception as e:
            print(f"❌ Error generating complete content: {e}")
            return None
    
    def generate_complete_resume_content_parallel(self, job_description: str, years_experience: int, 
                                                   work_history: List[Dict]) -> Dict[str, Any]:
        """
        🚀 FASTEST: Generate ALL resume content using PARALLEL API calls (3-5 seconds)
        Makes multiple API calls simultaneously instead of sequentially
        """
        print(f"⚡ PARALLEL MODE: Making all API calls simultaneously...")
        start_time = time.time()
        
        companies = ", ".join([exp.get('company', '') for exp in work_history if exp.get('company')])
        
        # Prepare all the API call functions
        def call_title():
            return self.generate_professional_title(job_description, years_experience)
        
        def call_summary():
            return self.generate_professional_summary(job_description, years_experience, work_history)
        
        def call_job_content(idx, exp):
            company = exp.get('company', '')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            # Generate title and description together
            years_at_company = 3
            try:
                start_year = int(start_date.split()[-1]) if start_date else 2020
                end_year = int(end_date.split()[-1]) if end_date and end_date.lower() != 'present' else 2024
                years_at_company = max(1, end_year - start_year)
            except:
                pass
            
            job_title = self.generate_job_title_for_position(job_description, company, idx, years_at_company)
            description = self.generate_job_description(job_description, company, job_title, 
                                                        start_date, end_date, idx)
            return {
                'job_title': job_title,
                'company': company,
                'description': description
            }
        
        # Execute all calls in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all tasks
            future_title = executor.submit(call_title)
            future_summary = executor.submit(call_summary)
            
            # Submit all work experience tasks
            future_jobs = []
            for idx, exp in enumerate(work_history):
                future_jobs.append(executor.submit(call_job_content, idx, exp))
            
            # Collect results
            professional_title = future_title.result()
            professional_summary = future_summary.result()
            
            work_experiences = []
            for future in future_jobs:
                work_experiences.append(future.result())
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"⚡ PARALLEL MODE completed in {elapsed:.2f} seconds!")
        print(f"   Generated: Title + Summary + {len(work_experiences)} work experiences")
        
        return {
            'professional_title': professional_title,
            'professional_summary': professional_summary,
            'work_experiences': work_experiences
        }

