# 📄 ResumeAI Pro - ATS-Friendly Resume Builder

An AI-powered resume creation system that generates ATS-optimized resumes with intelligent scoring.

## 🎯 Features

- ✨ AI-powered resume content generation using GPT-4
- 📊 Comprehensive ATS scoring (0-100)
- 📥 Download in PDF and DOCX formats
- 🎨 Professional, ATS-friendly formatting
- 🔍 Job description matching and optimization
- 📄 Existing resume parsing and enhancement

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI:** OpenAI GPT-4 API
- **PDF Generation:** ReportLab
- **DOCX Generation:** python-docx
- **Resume Parsing:** PyPDF2, pdfplumber

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ats-resume-builder.git
cd ats-resume-builder

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OpenAI API key to .env