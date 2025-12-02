"""
PDF Generation Service for ATS-Optimized Resumes with Randomized Styles
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from typing import Dict, Any, List
import os
import random
from datetime import datetime

class PDFGenerator:
    """Generates clean, ATS-friendly PDF resumes with randomized professional styles"""
    
    def __init__(self):
        # Use backend/output directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(backend_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Select a random style template
        self.style_template = self._select_random_style_template()
        self.styles = self._create_styles(self.style_template)
        
        print(f"📄 PDF Style: {self.style_template['name']}")
    
    def _select_random_style_template(self) -> Dict[str, Any]:
        """Select a random style template from predefined ATS-friendly options"""
        templates = [
            {
                'name': 'Classic Professional - Center',
                'name_size': 18,
                'title_size': 11,
                'contact_size': 9,
                'section_size': 13,
                'job_title_size': 11,
                'body_size': 10,
                'margins': 0.75,
                'section_spacing': 14,
                'name_alignment': TA_CENTER,
                'title_alignment': TA_CENTER,
                'contact_alignment': TA_CENTER,
                'contact_position': 'header',  # header or below_title
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Modern Minimalist - Center',
                'name_size': 20,
                'title_size': 10,
                'contact_size': 9,
                'section_size': 12,
                'job_title_size': 10,
                'body_size': 10,
                'margins': 0.85,
                'section_spacing': 12,
                'name_alignment': TA_CENTER,
                'title_alignment': TA_CENTER,
                'contact_alignment': TA_CENTER,
                'contact_position': 'header',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Executive Bold - Left Aligned',
                'name_size': 22,
                'title_size': 12,
                'contact_size': 10,
                'section_size': 14,
                'job_title_size': 11,
                'body_size': 11,
                'margins': 0.65,
                'section_spacing': 16,
                'name_alignment': TA_LEFT,
                'title_alignment': TA_LEFT,
                'contact_alignment': TA_LEFT,
                'contact_position': 'below_title',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Compact Efficient - Dense',
                'name_size': 16,
                'title_size': 10,
                'contact_size': 9,
                'section_size': 11,
                'job_title_size': 10,
                'body_size': 9.5,
                'margins': 0.6,
                'section_spacing': 10,
                'name_alignment': TA_CENTER,
                'title_alignment': TA_CENTER,
                'contact_alignment': TA_CENTER,
                'contact_position': 'header',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Balanced Standard - Left Header',
                'name_size': 17,
                'title_size': 11,
                'contact_size': 9.5,
                'section_size': 12,
                'job_title_size': 10.5,
                'body_size': 10,
                'margins': 0.7,
                'section_spacing': 13,
                'name_alignment': TA_LEFT,
                'title_alignment': TA_LEFT,
                'contact_alignment': TA_LEFT,
                'contact_position': 'header',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Clean Contemporary - Center',
                'name_size': 19,
                'title_size': 11,
                'contact_size': 9,
                'section_size': 13,
                'job_title_size': 10.5,
                'body_size': 10.5,
                'margins': 0.8,
                'section_spacing': 15,
                'name_alignment': TA_CENTER,
                'title_alignment': TA_CENTER,
                'contact_alignment': TA_CENTER,
                'contact_position': 'below_title',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Professional Left - Bold',
                'name_size': 20,
                'title_size': 11,
                'contact_size': 9,
                'section_size': 13,
                'job_title_size': 11,
                'body_size': 10.5,
                'margins': 0.7,
                'section_spacing': 14,
                'name_alignment': TA_LEFT,
                'title_alignment': TA_LEFT,
                'contact_alignment': TA_LEFT,
                'contact_position': 'below_title',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Executive Center - Spacious',
                'name_size': 21,
                'title_size': 12,
                'contact_size': 9.5,
                'section_size': 13,
                'job_title_size': 11,
                'body_size': 10.5,
                'margins': 0.75,
                'section_spacing': 15,
                'name_alignment': TA_CENTER,
                'title_alignment': TA_CENTER,
                'contact_alignment': TA_CENTER,
                'contact_position': 'header',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Minimalist Left - Clean',
                'name_size': 18,
                'title_size': 10,
                'contact_size': 9,
                'section_size': 12,
                'job_title_size': 10,
                'body_size': 10,
                'margins': 0.8,
                'section_spacing': 13,
                'name_alignment': TA_LEFT,
                'title_alignment': TA_LEFT,
                'contact_alignment': TA_LEFT,
                'contact_position': 'header',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            },
            {
                'name': 'Compact Left - Efficient',
                'name_size': 17,
                'title_size': 10,
                'contact_size': 9,
                'section_size': 11,
                'job_title_size': 10,
                'body_size': 9.5,
                'margins': 0.65,
                'section_spacing': 11,
                'name_alignment': TA_LEFT,
                'title_alignment': TA_LEFT,
                'contact_alignment': TA_LEFT,
                'contact_position': 'below_title',
                'section_alignment': TA_LEFT,
                'font': 'Helvetica'
            }
        ]
        
        return random.choice(templates)
    
    def _create_styles(self, template: Dict[str, Any]):
        """Create custom styles for ATS-friendly formatting based on template"""
        styles = getSampleStyleSheet()
        
        # Name style
        styles.add(ParagraphStyle(
            name='ResumeName',
            parent=styles['Heading1'],
            fontSize=template['name_size'],
            textColor=colors.black,
            spaceAfter=6,
            alignment=template['name_alignment'],
            fontName=f"{template['font']}-Bold"
        ))
        
        # Professional Title style
        styles.add(ParagraphStyle(
            name='ProfessionalTitle',
            parent=styles['Normal'],
            fontSize=template['title_size'],
            textColor=colors.black,
            spaceAfter=12,
            alignment=template['title_alignment'],
            fontName=template['font']
        ))
        
        # Contact info style
        styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=styles['Normal'],
            fontSize=template['contact_size'],
            textColor=colors.black,
            spaceAfter=12 if template['contact_position'] == 'header' else 16,
            alignment=template['contact_alignment'],
            fontName=template['font']
        ))
        
        # Section heading style
        styles.add(ParagraphStyle(
            name='ResumeSection',
            parent=styles['Heading2'],
            fontSize=template['section_size'],
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=template['section_spacing'],
            fontName=f"{template['font']}-Bold"
        ))
        
        # Job title style
        styles.add(ParagraphStyle(
            name='ResumeJobTitle',
            parent=styles['Normal'],
            fontSize=template['job_title_size'],
            textColor=colors.black,
            spaceAfter=2,
            fontName=f"{template['font']}-Bold"
        ))
        
        # Company style
        styles.add(ParagraphStyle(
            name='ResumeCompany',
            parent=styles['Normal'],
            fontSize=template['body_size'],
            textColor=colors.black,
            spaceAfter=2,
            fontName=template['font']
        ))
        
        # Date style
        styles.add(ParagraphStyle(
            name='ResumeDate',
            parent=styles['Normal'],
            fontSize=template['contact_size'],
            textColor=colors.black,
            spaceAfter=6,
            fontName=template['font']
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=styles['Normal'],
            fontSize=template['body_size'],
            textColor=colors.black,
            spaceAfter=4,
            fontName=template['font'],
            leading=template['body_size'] + 4,
            alignment=TA_LEFT,
            wordWrap='LTR',
            allowWidows=1,
            allowOrphans=1
        ))
        
        # Skills style
        styles.add(ParagraphStyle(
            name='ResumeSkills',
            parent=styles['Normal'],
            fontSize=template['body_size'],
            textColor=colors.black,
            spaceAfter=6,
            fontName=template['font'],
            leading=template['body_size'] + 4
        ))
        
        return styles
    
    def generate_pdf(self, resume_data: Dict[str, Any]) -> str:
        """
        Generate ATS-optimized PDF resume
        
        Args:
            resume_data: Dictionary containing all resume information
            
        Returns:
            Path to generated PDF file
        """
        # Create datetime folder
        datetime_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(self.output_dir, datetime_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Create filename with just the full name
        name = resume_data.get('personal_info', {}).get('name', 'Resume')
        filename = f"{name.replace(' ', '_')}.pdf"
        filepath = os.path.join(folder_path, filename)
        
        # Create PDF document with randomized margins
        margin = self.style_template['margins'] * inch
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin
        )
        
        # Build content
        story = []
        
        # Add header
        story.extend(self._create_header(resume_data.get('personal_info', {})))
        
        # Add professional summary
        if resume_data.get('professional_summary'):
            story.extend(self._create_professional_summary(resume_data['professional_summary']))
        
        # Add skills
        if resume_data.get('skills'):
            story.extend(self._create_skills_section(resume_data['skills']))
        
        # Add work experience
        if resume_data.get('work_experience'):
            story.extend(self._create_work_experience(resume_data['work_experience']))
        
        # Add projects
        if resume_data.get('projects'):
            story.extend(self._create_projects_section(resume_data['projects']))
        
        # Add certifications
        if resume_data.get('certifications'):
            story.extend(self._create_certifications_section(resume_data['certifications']))
        
        # Add education
        if resume_data.get('education'):
            story.extend(self._create_education_section(resume_data['education']))
        
        # Add languages
        if resume_data.get('languages'):
            story.extend(self._create_languages_section(resume_data['languages']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _create_header(self, personal_info: Dict[str, Any]) -> List:
        """Create resume header with contact information"""
        elements = []
        
        # Name
        name = personal_info.get('name', '')
        if name:
            elements.append(Paragraph(name, self.styles['ResumeName']))
        
        # Title
        title = personal_info.get('title', '')
        if title:
            elements.append(Paragraph(title, self.styles['ProfessionalTitle']))
        
        # Contact information
        contact_parts = []
        if personal_info.get('address'):
            contact_parts.append(personal_info['address'])
        if personal_info.get('email'):
            contact_parts.append(personal_info['email'])
        if personal_info.get('phone'):
            contact_parts.append(personal_info['phone'])
        if personal_info.get('linkedin'):
            contact_parts.append(personal_info['linkedin'])
        
        if contact_parts:
            contact_text = ' • '.join(contact_parts)
            elements.append(Paragraph(contact_text, self.styles['ContactInfo']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_professional_summary(self, summary: str) -> List:
        """Create professional summary section"""
        elements = []
        
        elements.append(Paragraph('PROFESSIONAL SUMMARY', self.styles['ResumeSection']))
        elements.append(Paragraph(summary, self.styles['ResumeBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_skills_section(self, skills: List[str]) -> List:
        """Create skills section with keyword-rich content"""
        elements = []
        
        elements.append(Paragraph('SKILLS', self.styles['ResumeSection']))
        
        # Format skills as comma-separated text (better for ATS)
        skills_text = ', '.join(skills)
        elements.append(Paragraph(skills_text, self.styles['ResumeSkills']))
        elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_work_experience(self, experiences: List[Dict[str, Any]]) -> List:
        """Create work experience section"""
        elements = []
        
        elements.append(Paragraph('PROFESSIONAL EXPERIENCE', self.styles['ResumeSection']))
        
        for i, exp in enumerate(experiences):
            exp_elements = []
            
            # Job title
            if exp.get('title'):
                exp_elements.append(Paragraph(exp['title'], self.styles['ResumeJobTitle']))
            
            # Company and location
            company_parts = []
            if exp.get('company'):
                company_parts.append(exp['company'])
            if exp.get('location'):
                company_parts.append(exp['location'])
            
            if company_parts:
                exp_elements.append(Paragraph(', '.join(company_parts), self.styles['ResumeCompany']))
            
            # Dates
            if exp.get('start_date') or exp.get('end_date'):
                start = exp.get('start_date', '')
                end = exp.get('end_date', 'Present')
                date_text = f"{start} – {end}"
                exp_elements.append(Paragraph(date_text, self.styles['ResumeDate']))
            
            # Description/Responsibilities - Show full description for all positions
            if exp.get('description'):
                desc_text = exp['description']
                exp_elements.append(Paragraph(desc_text, self.styles['ResumeBody']))
            
            exp_elements.append(Spacer(1, 0.1*inch))
            
            # For longer descriptions, don't use KeepTogether to avoid page issues
            # Only use KeepTogether for shorter entries
            if exp.get('description') and len(exp['description']) > 800:
                elements.extend(exp_elements)
            else:
                # Keep shorter experiences together on same page if possible
                elements.append(KeepTogether(exp_elements))
        
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_projects_section(self, projects: List[Dict[str, Any]]) -> List:
        """Create projects & portfolio section"""
        elements = []
        
        if not projects:
            return elements
        
        elements.append(Paragraph('PROJECTS & PORTFOLIO', self.styles['ResumeSection']))
        
        for project in projects:
            proj_elements = []
            
            # Project name
            if project.get('name'):
                proj_elements.append(Paragraph(project['name'], self.styles['ResumeJobTitle']))
            
            # Description
            if project.get('description'):
                proj_elements.append(Paragraph(project['description'], self.styles['ResumeBody']))
            
            # Technologies
            if project.get('technologies'):
                tech_text = f"<b>Technologies:</b> {project['technologies']}"
                proj_elements.append(Paragraph(tech_text, self.styles['ResumeBody']))
            
            # URL
            if project.get('url'):
                proj_elements.append(Paragraph(f"<b>URL:</b> {project['url']}", self.styles['ResumeBody']))
            
            proj_elements.append(Spacer(1, 0.1*inch))
            elements.append(KeepTogether(proj_elements))
        
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_certifications_section(self, certifications: List[Dict[str, Any]]) -> List:
        """Create certifications section"""
        elements = []
        
        if not certifications:
            return elements
        
        elements.append(Paragraph('CERTIFICATIONS', self.styles['ResumeSection']))
        
        for cert in certifications:
            cert_elements = []
            
            # Certification name
            if cert.get('name'):
                cert_elements.append(Paragraph(cert['name'], self.styles['ResumeJobTitle']))
            
            # Issuer and date
            issuer_parts = []
            if cert.get('issuer'):
                issuer_parts.append(cert['issuer'])
            if cert.get('date'):
                issuer_parts.append(cert['date'])
            
            if issuer_parts:
                cert_elements.append(Paragraph(' – '.join(issuer_parts), self.styles['ResumeCompany']))
            
            cert_elements.append(Spacer(1, 0.05*inch))
            elements.extend(cert_elements)
        
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_education_section(self, education: List[Dict[str, Any]]) -> List:
        """Create education section"""
        elements = []
        
        if not education:
            return elements
        
        elements.append(Paragraph('EDUCATION', self.styles['ResumeSection']))
        
        for edu in education:
            edu_elements = []
            
            # Degree • School • Location (all in one line)
            degree_line = edu.get('degree', '')
            if edu.get('school'):
                degree_line += f" • {edu.get('school')}"
            if edu.get('location'):
                degree_line += f", {edu.get('location')}"
            
            if degree_line:
                edu_elements.append(Paragraph(degree_line, self.styles['ResumeJobTitle']))
            
            # Graduation Year
            if edu.get('year'):
                year_text = f"Graduation Year ({edu.get('year')})"
                edu_elements.append(Paragraph(year_text, self.styles['ResumeDate']))
            
            # Honors/GPA
            if edu.get('honors'):
                edu_elements.append(Paragraph(edu['honors'], self.styles['ResumeBody']))
            
            # Focus/Description
            if edu.get('focus'):
                edu_elements.append(Paragraph(edu['focus'], self.styles['ResumeBody']))
            
            edu_elements.append(Spacer(1, 0.1*inch))
            elements.extend(edu_elements)
        
        return elements
    
    def _create_languages_section(self, languages: List[str]) -> List:
        """Create languages section"""
        elements = []
        
        if not languages:
            return elements
        
        elements.append(Paragraph('LANGUAGES', self.styles['ResumeSection']))
        
        for lang in languages:
            elements.append(Paragraph(lang, self.styles['ResumeBody']))
        
        elements.append(Spacer(1, 0.1*inch))
        
        return elements

