# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```powershell
pip install Flask Flask-CORS reportlab python-dotenv
```

### Step 2: Start the Backend Server

**Windows:**
```powershell
cd backend
python app.py
```

**Linux/Mac:**
```bash
cd backend
python3 app.py
```

The server will start on `http://localhost:5000`

### Step 3: Open the Frontend

Open `frontend/index.html` in your web browser, or use a local server:

```powershell
cd frontend
python -m http.server 8000
```

Then navigate to `http://localhost:8000`

---

## 📝 How to Use

### 1. Enter Job Description
- Paste the complete job description in the text area
- Click **"Analyze Job Description"** to extract keywords
- The system will identify 100-200 relevant skills automatically

### 2. Fill in Your Information

**Personal Information:**
- Full name, professional title
- Email, phone, address, LinkedIn profile

**Professional Summary:**
- Keep it simple (2-3 sentences)
- Leave empty for auto-generation

**Skills:**
- Add your core skills (comma-separated)
- The system will expand them based on job description

**Work Experience:**
- Click "+ Add Experience" for each position
- ⚠️ **Important**: Make your last 2 positions very detailed
- Include specific achievements and technologies used

**Additional Sections:**
- Projects & Portfolio
- Certifications
- Education

### 3. Generate Your Resume

- Click **"Save Data"** to save for future use
- Click **"Generate Resume PDF"** to create your ATS-optimized resume
- The PDF will automatically download

---

## ✨ Key Features

### ATS Optimization
- Automatically matches 100-200 relevant skills to job description
- Clean, text-only format (no images, complex formatting)
- Standard section names for ATS compatibility

### Resume Format
- **No Images**: Pure text-based
- **No Underlines**: Clean typography
- **Simple Fonts**: Helvetica for maximum compatibility
- **Detailed Recent Experience**: Last 2 positions get full descriptions
- **Keyword-Rich**: Skills section optimized for ATS scanning

### Data Persistence
- Your information is saved automatically
- Reuse for multiple job applications
- Just change the job description and regenerate

---

## 🧪 Testing

Run the test script to verify everything works:

```powershell
python test_app.py
```

This will:
1. Test keyword extraction
2. Test resume optimization
3. Test data persistence
4. Generate a sample PDF

---

## 📄 Example Output

Your resume will include:

1. **Header**: Name, title, contact information
2. **Professional Summary**: 2-3 sentences
3. **Skills**: 100-200 keywords matched to job description
4. **Professional Experience**: Detailed last 2 positions, concise older ones
5. **Projects & Portfolio**: Optional section
6. **Certifications**: Optional section
7. **Education**: Degree, institution, dates, GPA

---

## 💡 Tips for Best Results

### Job Description
- ✅ Paste the **complete** job description
- ✅ Include requirements, qualifications, and nice-to-haves
- ✅ The more details, the better the keyword matching

### Recent Positions (Last 2)
- ✅ Write detailed, story-like descriptions
- ✅ Include specific achievements with numbers/metrics
- ✅ Mention technologies, frameworks, and methodologies used
- ✅ Describe impact and outcomes of your work
- ✅ Aim for 500-1000 words per position

### Older Positions
- ✅ Keep them concise (100-300 words)
- ✅ Focus on key responsibilities
- ✅ The system will automatically limit length

### Skills
- ✅ Add your core 10-20 skills manually
- ✅ The system will add 80-180 more based on job description
- ✅ All skills are formatted for optimal ATS scanning

### Professional Summary
- ✅ Keep it simple and focused
- ✅ 2-3 sentences max
- ✅ Or leave empty for auto-generation

---

## 🔧 Troubleshooting

### Backend won't start
```powershell
# Install dependencies again
pip install -r requirements.txt

# Check if port 5000 is in use
netstat -ano | findstr :5000
```

### Can't connect to backend
- Ensure backend is running: `python backend/app.py`
- Check browser console for errors
- Verify URL is `http://localhost:5000`

### PDF generation fails
- Check `output/` directory exists (created automatically)
- Verify ReportLab is installed: `pip install reportlab`
- Check console for error messages

### Data not saving
- Ensure `data/` directory exists (created automatically)
- Check file permissions
- Verify backend server is running

---

## 🎯 What Makes This ATS-Friendly?

### ✅ Text-Based Format
- No images, icons, or graphics
- No tables, columns, or complex layouts
- Clean, linear structure

### ✅ Standard Fonts
- Uses Helvetica (standard system font)
- No custom or decorative fonts
- Consistent font sizes

### ✅ Keyword Optimization
- 100-200 skills matched to job description
- Relevant keywords throughout
- Industry-standard terminology

### ✅ Clear Section Headers
- PROFESSIONAL SUMMARY
- SKILLS
- PROFESSIONAL EXPERIENCE
- CERTIFICATIONS
- EDUCATION

### ✅ Simple Formatting
- No underlines
- No colored text
- No special characters
- Consistent spacing

---

## 📊 What the System Does Automatically

1. **Extracts Keywords** from job description
2. **Generates 100-200 Skills** relevant to the position
3. **Optimizes Content** for ATS scanning
4. **Formats PDF** with clean, ATS-friendly layout
5. **Saves Your Data** for reuse
6. **Emphasizes Recent Experience** (last 2 positions)
7. **Creates Professional PDFs** ready to submit

---

## 🎓 Best Practices

### Do's ✅
- ✅ Analyze job description before filling form
- ✅ Save data frequently
- ✅ Write detailed descriptions for recent positions
- ✅ Use industry-standard terminology
- ✅ Include specific achievements and metrics
- ✅ Tailor each resume to the specific job

### Don'ts ❌
- ❌ Don't use complex formatting
- ❌ Don't add images or graphics
- ❌ Don't use tables or columns
- ❌ Don't omit important keywords
- ❌ Don't use abbreviations without spelling out first
- ❌ Don't forget to update for each application

---

## 🚀 You're Ready!

Your ATS Resume Generator is fully functional and ready to help you create professional, ATS-optimized resumes. Good luck with your job applications! 🎉

