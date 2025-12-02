# ATS Resume Generator

A professional tool to create ATS-optimized resume PDF files tailored to specific job descriptions.

## Features

- **ATS Optimization**: Automatically matches your resume to job descriptions with 100-200 relevant skills
- **Data Persistence**: Save your information once and reuse it for multiple resumes
- **Clean PDF Generation**: Produces professional, ATS-friendly PDFs without images or complex formatting
- **Intelligent Keyword Extraction**: Analyzes job descriptions to extract key skills and requirements
- **Detailed Experience Sections**: Emphasizes your last two positions with detailed, story-like descriptions
- **Simple, User-Friendly Interface**: Easy-to-use web interface for all your resume needs

## Technology Stack

### Backend
- **Flask**: Python web framework
- **ReportLab**: PDF generation library
- **NLTK/SpaCy**: Natural language processing for keyword extraction

### Frontend
- **HTML5/CSS3**: Clean, modern interface
- **Vanilla JavaScript**: No framework dependencies for simplicity

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or navigate to the project directory**
```bash
cd resume_maker
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Download required NLP data (for keyword extraction)**
```bash
python -m spacy download en_core_web_sm
```

## Running the Application

### 1. Start the Backend Server

#### On Windows:
```powershell
cd backend
python app.py
```

#### On Linux/Mac:
```bash
cd backend
python3 app.py
```

The backend server will start on `http://localhost:5000`

### 2. Open the Frontend

Open `frontend/index.html` in your web browser, or use a local server:

#### Using Python:
```bash
cd frontend
python -m http.server 8000
```

Then navigate to `http://localhost:8000` in your browser.

## Usage Guide

### 1. Enter Job Description
- Paste the job description in the first text area
- Click "Analyze Job Description" to extract keywords

### 2. Fill in Personal Information
- Name, email, phone, address, LinkedIn profile
- Professional title/headline

### 3. Add Your Experience
- Click "+ Add Experience" to add work positions
- **Important**: Make your last two positions very detailed with story-like descriptions
- Include specific achievements, technologies used, and impact

### 4. Add Additional Sections
- Projects & Portfolio
- Certifications
- Education

### 5. Skills Section
- Add your core skills (comma-separated)
- The system will automatically add 100-200 relevant skills based on the job description

### 6. Generate Resume
- Click "Save Data" to save your information for future use
- Click "Generate Resume PDF" to create your ATS-optimized resume

## Resume Format Guidelines

The generated resume follows these ATS-friendly practices:

- **No Images**: Pure text-based format
- **No Underlines**: Clean, simple formatting
- **Simple Professional Summary**: 2-3 sentences highlighting key experience
- **Comprehensive Skills Section**: 100-200 skills matched to job description
- **Detailed Recent Experience**: Last two positions have extensive, story-like descriptions
- **Clean Typography**: Uses standard fonts (Helvetica) for maximum compatibility
- **Proper Sections**: Clear hierarchy with standard section names

## Project Structure

```
resume_maker/
│
├── backend/
│   ├── app.py                      # Main Flask application
│   └── services/
│       ├── data_service.py         # Data persistence service
│       ├── ats_matcher.py          # Keyword matching and optimization
│       └── pdf_generator.py        # PDF generation service
│
├── frontend/
│   ├── index.html                  # Main UI
│   ├── styles.css                  # Styling
│   └── app.js                      # Frontend logic
│
├── data/                           # Saved user data (auto-created)
├── output/                         # Generated PDFs (auto-created)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/save-data` - Save user resume data
- `GET /api/load-data` - Load saved user data
- `POST /api/analyze-job` - Analyze job description and extract keywords
- `POST /api/generate-resume` - Generate ATS-optimized PDF resume

## Tips for Best Results

1. **Job Description**: Always paste the complete job description for best keyword matching
2. **Recent Positions**: Write detailed, story-like descriptions for your last 2 positions
3. **Skills**: Add your core skills; the system will expand them based on the job description
4. **Save Regularly**: Use the "Save Data" button to avoid losing your information
5. **Professional Summary**: Keep it simple and focused (or leave empty for auto-generation)

## Troubleshooting

### Backend won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that port 5000 is not in use

### PDF generation fails
- Verify ReportLab is installed: `pip install reportlab`
- Check that the `output/` directory exists (it should be created automatically)

### Cannot load saved data
- Ensure the backend server is running
- Check that the `data/` directory exists and has proper permissions

## Future Enhancements

- Multiple resume templates
- Export to different formats (Word, JSON)
- Resume comparison and scoring
- Cover letter generation
- Browser extension for quick job description capture

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or questions, please check the troubleshooting section or review the code comments in the source files.

