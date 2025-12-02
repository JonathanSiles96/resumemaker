"""
ATS Keyword Matching and Resume Optimization Service
"""
import re
from typing import List, Dict, Set, Any
from collections import Counter

class ATSMatcher:
    """Handles ATS keyword matching and resume optimization"""
    
    def __init__(self):
        self.tech_skills_database = self._load_tech_skills()
    
    def _load_tech_skills(self) -> Set[str]:
        """Load comprehensive list of technical skills"""
        return {
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C#', 'C++', 'C', 'Go', 'Rust', 'Ruby', 
            'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell',
            
            # Frontend Technologies
            'React', 'Angular', 'Vue.js', 'Vue', 'Next.js', 'Nuxt.js', 'Svelte', 'Ember.js',
            'HTML5', 'HTML', 'CSS3', 'CSS', 'SCSS', 'SASS', 'LESS', 'Tailwind CSS', 'Bootstrap',
            'Material UI', 'Material Design', 'Chakra UI', 'Ant Design', 'Semantic UI',
            'jQuery', 'Redux', 'MobX', 'NgRx', 'RxJS', 'Webpack', 'Vite', 'Rollup', 'Parcel',
            'Babel', 'ESLint', 'Prettier', 'Styled Components', 'Emotion', 'CSS Modules',
            'Responsive Design', 'Mobile-First Design', 'Progressive Web Apps', 'PWA',
            'Single Page Applications', 'SPA', 'Server-Side Rendering', 'SSR', 'Static Site Generation',
            'Web Components', 'Shadow DOM', 'Web Accessibility', 'WCAG', 'ARIA', 'SEO',
            'Cross-Browser Compatibility', 'Browser DevTools', 'Lighthouse',
            
            # Backend Technologies
            '.NET', '.NET Core', '.NET Framework', 'ASP.NET', 'ASP.NET Core', 'ASP.NET MVC',
            'ASP.NET Web API', 'Entity Framework', 'Entity Framework Core', 'ADO.NET', 'LINQ',
            'Node.js', 'Express.js', 'Nest.js', 'Koa', 'Fastify', 'Hapi',
            'Django', 'Flask', 'FastAPI', 'Pyramid', 'Tornado',
            'Spring', 'Spring Boot', 'Spring MVC', 'Hibernate', 'JPA',
            'Ruby on Rails', 'Sinatra', 'Laravel', 'Symfony', 'CodeIgniter',
            'GraphQL', 'Apollo', 'gRPC', 'REST', 'RESTful API', 'SOAP', 'WebSockets',
            'SignalR', 'Socket.io', 'Microservices', 'Monolithic Architecture',
            'Serverless', 'Lambda Functions', 'Event-Driven Architecture',
            'Message Queues', 'RabbitMQ', 'Kafka', 'Redis', 'Celery',
            'API Gateway', 'API Design', 'OpenAPI', 'Swagger', 'Postman',
            
            # Databases
            'SQL', 'SQL Server', 'MySQL', 'PostgreSQL', 'Oracle', 'SQLite', 'MariaDB',
            'MongoDB', 'Cassandra', 'Redis', 'Elasticsearch', 'DynamoDB', 'CosmosDB',
            'Firebase', 'Firestore', 'Realm', 'Neo4j', 'CouchDB', 'InfluxDB',
            'Database Design', 'Database Optimization', 'Query Optimization', 'Indexing',
            'Stored Procedures', 'Triggers', 'Views', 'Transactions', 'ACID', 'CAP Theorem',
            'NoSQL', 'Document Databases', 'Key-Value Stores', 'Column Stores', 'Graph Databases',
            'Data Modeling', 'Schema Design', 'Normalization', 'Denormalization',
            'Database Migration', 'Data Warehousing', 'ETL', 'Data Pipeline',
            
            # Cloud Platforms
            'AWS', 'Amazon Web Services', 'Azure', 'Microsoft Azure', 'Google Cloud Platform', 'GCP',
            'EC2', 'S3', 'Lambda', 'RDS', 'DynamoDB', 'CloudFront', 'Route 53', 'ECS', 'EKS',
            'Azure Functions', 'Azure App Services', 'Azure DevOps', 'Azure SQL Database',
            'Azure Blob Storage', 'Azure Kubernetes Service', 'AKS', 'Application Insights',
            'Cloud Functions', 'Cloud Run', 'BigQuery', 'Cloud Storage', 'Cloud SQL',
            'Heroku', 'DigitalOcean', 'Linode', 'Vercel', 'Netlify', 'Railway',
            'Cloud Architecture', 'Cloud Security', 'Cloud Migration', 'Multi-Cloud',
            'Infrastructure as Code', 'IaC', 'Terraform', 'CloudFormation', 'ARM Templates',
            'Serverless Framework', 'SAM', 'CDK', 'Pulumi',
            
            # DevOps & CI/CD
            'Docker', 'Kubernetes', 'Helm', 'Docker Compose', 'Container Orchestration',
            'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI', 'Travis CI', 'Bitbucket Pipelines',
            'Azure Pipelines', 'TeamCity', 'Bamboo', 'Octopus Deploy',
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Version Control', 'Source Control',
            'CI/CD', 'Continuous Integration', 'Continuous Deployment', 'Continuous Delivery',
            'Automation', 'Build Automation', 'Deployment Automation', 'Release Management',
            'Infrastructure Monitoring', 'Application Monitoring', 'Log Management',
            'Prometheus', 'Grafana', 'ELK Stack', 'Elasticsearch', 'Logstash', 'Kibana',
            'Splunk', 'DataDog', 'New Relic', 'CloudWatch', 'Application Insights',
            'Sentry', 'Rollbar', 'PagerDuty', 'Nagios', 'Zabbix',
            
            # Testing
            'Unit Testing', 'Integration Testing', 'End-to-End Testing', 'E2E Testing',
            'Test-Driven Development', 'TDD', 'Behavior-Driven Development', 'BDD',
            'Jest', 'Mocha', 'Chai', 'Jasmine', 'Karma', 'Cypress', 'Playwright', 'Selenium',
            'Puppeteer', 'TestCafe', 'WebdriverIO', 'JUnit', 'TestNG', 'Mockito', 'JMock',
            'xUnit', 'NUnit', 'MSTest', 'PyTest', 'unittest', 'RSpec', 'PHPUnit',
            'Test Automation', 'API Testing', 'Performance Testing', 'Load Testing',
            'Stress Testing', 'Security Testing', 'Penetration Testing', 'Vulnerability Assessment',
            'JMeter', 'Gatling', 'Locust', 'K6', 'Artillery',
            
            # Security
            'OAuth', 'OAuth2', 'OpenID Connect', 'SAML', 'JWT', 'JSON Web Tokens',
            'Authentication', 'Authorization', 'RBAC', 'Identity Management', 'SSO',
            'Encryption', 'SSL/TLS', 'HTTPS', 'Certificate Management', 'PKI',
            'Web Security', 'Application Security', 'Network Security', 'Cloud Security',
            'OWASP', 'XSS', 'CSRF', 'SQL Injection', 'Security Best Practices',
            'Content Security Policy', 'CSP', 'CORS', 'Same-Origin Policy',
            'Secure Coding', 'Code Security', 'Security Audits', 'Compliance',
            'GDPR', 'HIPAA', 'PCI DSS', 'SOC 2', 'ISO 27001',
            
            # Architecture & Design
            'Microservices Architecture', 'Service-Oriented Architecture', 'SOA',
            'Event-Driven Architecture', 'Domain-Driven Design', 'DDD', 'CQRS',
            'Event Sourcing', 'Hexagonal Architecture', 'Clean Architecture', 'Onion Architecture',
            'MVC', 'MVVM', 'MVP', 'Design Patterns', 'Gang of Four', 'SOLID Principles',
            'Scalable Architecture', 'Distributed Systems', 'System Design', 'High Availability',
            'Load Balancing', 'Caching', 'CDN', 'Performance Optimization', 'Code Optimization',
            'Refactoring', 'Code Review', 'Technical Debt', 'Legacy System Modernization',
            'API Design', 'REST', 'RESTful', 'HATEOAS', 'API Versioning',
            
            # Methodologies & Practices
            'Agile', 'Scrum', 'Kanban', 'Lean', 'Waterfall', 'XP', 'Extreme Programming',
            'SAFe', 'DevOps', 'GitOps', 'Pair Programming', 'Code Review', 'Sprint Planning',
            'Daily Standup', 'Retrospective', 'Sprint Review', 'Backlog Grooming',
            'User Stories', 'Acceptance Criteria', 'Definition of Done', 'Story Points',
            'Estimation', 'Velocity', 'Burndown Chart', 'Burnup Chart',
            
            # Tools & Platforms
            'Jira', 'Confluence', 'Trello', 'Asana', 'Monday.com', 'ClickUp', 'Linear',
            'Slack', 'Microsoft Teams', 'Zoom', 'Google Workspace', 'Microsoft 365',
            'VS Code', 'Visual Studio', 'IntelliJ IDEA', 'PyCharm', 'WebStorm',
            'Eclipse', 'NetBeans', 'Sublime Text', 'Atom', 'Vim', 'Emacs',
            'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator',
            'npm', 'yarn', 'pnpm', 'Maven', 'Gradle', 'pip', 'NuGet', 'Composer',
            
            # Data & Analytics
            'Data Analysis', 'Data Science', 'Machine Learning', 'Deep Learning', 'AI',
            'Artificial Intelligence', 'Neural Networks', 'TensorFlow', 'PyTorch', 'Keras',
            'scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Plotly',
            'Data Visualization', 'Business Intelligence', 'BI', 'Tableau', 'Power BI',
            'Looker', 'Metabase', 'Google Analytics', 'Adobe Analytics', 'Mixpanel',
            'Segment', 'Amplitude', 'Heap', 'Hotjar',
            
            # Mobile Development
            'React Native', 'Flutter', 'Ionic', 'Xamarin', 'Cordova', 'PhoneGap',
            'iOS Development', 'Android Development', 'Swift', 'SwiftUI', 'Objective-C',
            'Kotlin', 'Java', 'Mobile UI/UX', 'Mobile Performance', 'App Store Optimization',
            'Push Notifications', 'In-App Purchases', 'Mobile Analytics',
            
            # Other Technologies
            'WebRTC', 'WebGL', 'Three.js', 'D3.js', 'Chart.js', 'Highcharts', 'ApexCharts',
            'Storybook', 'Chromatic', 'Design Systems', 'Component Libraries',
            'Internationalization', 'i18n', 'Localization', 'l10n', 'Translation',
            'Accessibility', 'A11y', 'Screen Readers', 'Keyboard Navigation',
            'Performance Monitoring', 'Error Tracking', 'Feature Flags', 'A/B Testing',
            'Analytics', 'Metrics', 'KPI', 'Dashboards', 'Reporting',
            'Documentation', 'Technical Writing', 'API Documentation', 'Markdown',
            'Confluence', 'Wiki', 'Knowledge Base', 'Runbooks',
            
            # Soft Skills & Concepts
            'Problem Solving', 'Critical Thinking', 'Communication', 'Team Collaboration',
            'Leadership', 'Mentoring', 'Code Review', 'Technical Leadership',
            'Cross-Functional Collaboration', 'Stakeholder Management', 'Project Management',
            'Time Management', 'Prioritization', 'Decision Making', 'Conflict Resolution'
        }
    
    def extract_keywords(self, job_description: str) -> List[str]:
        """
        Extract important keywords from job description
        
        Args:
            job_description: The job description text
            
        Returns:
            List of extracted keywords
        """
        # Convert to lowercase for matching
        text_lower = job_description.lower()
        
        # Find matching skills
        found_skills = []
        for skill in self.tech_skills_database:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Extract additional keywords (capitalized words, acronyms)
        words = re.findall(r'\b[A-Z][A-Za-z0-9+#\.]*(?:\s+[A-Z][a-z]*)*\b', job_description)
        
        # Combine and deduplicate
        all_keywords = list(set(found_skills + words))
        
        return sorted(all_keywords)[:50]  # Return top 50 keywords
    
    def get_relevant_skills(self, job_description: str) -> List[str]:
        """
        Get comprehensive list of relevant skills based on job description
        
        Args:
            job_description: The job description text
            
        Returns:
            List of all relevant skills from JD plus related ones
        """
        text_lower = job_description.lower()
        
        # Find exact matches from JD (from our skills database)
        exact_matches = []
        for skill in self.tech_skills_database:
            if skill.lower() in text_lower:
                exact_matches.append(skill)
        
        # Extract additional technical keywords from JD (capitalized words, acronyms)
        # Only include words that look like technical terms
        additional_keywords = re.findall(r'\b[A-Z][A-Za-z0-9+#\.]*(?:\s+[A-Z][a-z]*)*\b', job_description)
        
        # Filter to only real technical keywords (not common words)
        stop_words = {'The', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Who', 'Why', 'How',
                     'Are', 'Were', 'Was', 'Is', 'Be', 'Been', 'Being', 'Have', 'Has', 'Had', 'Do', 'Does',
                     'Did', 'Will', 'Would', 'Should', 'Could', 'May', 'Might', 'Must', 'Can', 'Our', 'Your',
                     'Their', 'His', 'Her', 'Its', 'We', 'You', 'They', 'He', 'She', 'It', 'Send', 'Get',
                     'Make', 'Take', 'Give', 'Find', 'Use', 'Work', 'Call', 'Try', 'Ask', 'Need', 'Feel',
                     'Want', 'Know', 'Put', 'Mean', 'Keep', 'Let', 'Begin', 'Start', 'Show', 'Turn', 'Follow',
                     'Play', 'Run', 'Move', 'Live', 'Believe', 'Hold', 'Bring', 'Write', 'Provide', 'Sit',
                     'Stand', 'Lose', 'Pay', 'Meet', 'Include', 'Continue', 'Set', 'Learn', 'Change', 'Lead',
                     'And', 'Or', 'But', 'If', 'Then', 'Because', 'As', 'Until', 'While', 'Of', 'At', 'By',
                     'For', 'With', 'About', 'Against', 'Between', 'Into', 'Through', 'During', 'Before', 'After',
                     'Above', 'Below', 'To', 'From', 'Up', 'Down', 'In', 'Out', 'On', 'Off', 'Over', 'Under'}
        
        additional_keywords = [k for k in additional_keywords if k not in stop_words and len(k) > 2]
        
        # Add related skills based on context (ecosystem skills)
        related_skills = self._get_related_skills(exact_matches, text_lower)
        
        # Combine all skills - prioritize JD skills first, then related
        all_skills = list(dict.fromkeys(exact_matches + additional_keywords + related_skills))
        
        return all_skills
    
    def _get_related_skills(self, found_skills: List[str], job_text: str) -> List[str]:
        """Get skills related to those found in job description"""
        related = []
        
        # Frontend ecosystems
        if any(s in found_skills for s in ['Angular', 'React', 'Vue.js', 'Vue']):
            related.extend([
                'TypeScript', 'JavaScript', 'HTML5', 'CSS3', 'SCSS', 'Webpack',
                'npm', 'Node.js', 'REST', 'API', 'Git', 'Responsive Design',
                'Component Architecture', 'State Management', 'RxJS', 'Redux',
                'Single Page Applications', 'SPA', 'Progressive Web Apps', 'PWA'
            ])
        
        # Backend ecosystems
        if any(s in found_skills for s in ['.NET', 'ASP.NET', 'C#']):
            related.extend([
                'C#', '.NET Core', '.NET Framework', 'ASP.NET Core', 'ASP.NET MVC',
                'Entity Framework', 'LINQ', 'SQL Server', 'Azure', 'REST',
                'Web API', 'Microservices', 'Docker', 'Kubernetes'
            ])
        
        if any(s in found_skills for s in ['Node.js', 'Express', 'JavaScript']):
            related.extend([
                'Node.js', 'Express.js', 'JavaScript', 'TypeScript', 'MongoDB',
                'PostgreSQL', 'REST', 'GraphQL', 'Docker', 'AWS', 'Microservices'
            ])
        
        # Cloud platforms
        if 'AWS' in found_skills or 'aws' in job_text:
            related.extend([
                'AWS', 'EC2', 'S3', 'Lambda', 'RDS', 'CloudFront', 'API Gateway',
                'CloudFormation', 'Terraform', 'Docker', 'Kubernetes', 'DevOps'
            ])
        
        if 'Azure' in found_skills or 'azure' in job_text:
            related.extend([
                'Azure', 'Azure DevOps', 'Azure Functions', 'Azure App Services',
                'Azure SQL Database', 'Application Insights', 'ARM Templates', 'Docker'
            ])
        
        # DevOps
        if any(s in found_skills for s in ['Docker', 'Kubernetes', 'CI/CD']):
            related.extend([
                'Docker', 'Kubernetes', 'Jenkins', 'GitHub Actions', 'GitLab CI',
                'Terraform', 'Ansible', 'Monitoring', 'Logging', 'Infrastructure as Code'
            ])
        
        return related
    
    def _get_common_skills(self) -> List[str]:
        """Return commonly required skills across many job postings"""
        return [
            'Git', 'Agile', 'Scrum', 'REST', 'API', 'JSON', 'SQL', 'HTML5', 'CSS3',
            'JavaScript', 'TypeScript', 'Problem Solving', 'Code Review', 'CI/CD',
            'Docker', 'Testing', 'Debugging', 'Communication', 'Team Collaboration',
            'Documentation', 'Performance Optimization', 'Security', 'Authentication'
        ]
    
    def optimize_resume_content(self, user_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Optimize resume content to match job description
        
        Args:
            user_data: User's resume data
            job_description: Target job description
            
        Returns:
            Optimized resume data
        """
        optimized = user_data.copy()
        
        # Get relevant skills from JD
        relevant_skills = self.get_relevant_skills(job_description)
        
        # Merge user skills with job-relevant skills (prioritize JD-matching skills first)
        user_skills = set(user_data.get('skills', []))
        
        # Prioritize: JD skills that user has, then all other JD skills, then remaining user skills
        jd_skills_user_has = [s for s in relevant_skills if s in user_skills]
        jd_skills_user_lacks = [s for s in relevant_skills if s not in user_skills]
        remaining_user_skills = [s for s in user_skills if s not in relevant_skills]
        
        all_skills = jd_skills_user_has + jd_skills_user_lacks + remaining_user_skills
        
        # Keep all relevant skills (no arbitrary limit - ATS needs to see all JD keywords)
        optimized['skills'] = all_skills
        
        # Ensure professional summary exists
        if not optimized.get('professional_summary'):
            optimized['professional_summary'] = self._generate_summary(user_data, job_description)
        
        return optimized
    
    def _generate_summary(self, user_data: Dict[str, Any], job_description: str) -> str:
        """Generate a simple professional summary if not provided"""
        work_exp = user_data.get('work_experience', [])
        if not work_exp:
            return "Experienced professional with a strong background in software development."
        
        # Calculate years of experience
        years = len(work_exp) * 2  # Rough estimate
        
        # Extract key skills from job description
        keywords = self.extract_keywords(job_description)[:5]
        skills_text = ', '.join(keywords) if keywords else 'modern technologies'
        
        return f"Professional with {years}+ years of experience in software development, specializing in {skills_text}. Proven track record of delivering high-quality solutions and collaborating effectively with cross-functional teams."

