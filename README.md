# 📄 ResumeAI Pro - ATS-Friendly Resume Builder

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sumityad07-ats-resume-builder-app-9ghv9r.streamlit.app)

> **🚀 [Try Live Demo](https://sumityad07-ats-resume-builder-app-9ghv9r.streamlit.app)** | **🎥 ** | **💻 [View Code](https://github.com/sumityad07/ats-resume-builder)**

---

**Built for:** Sophyra Platform - AI Intern Qualification Task  
**Submitted by:** [Your Name]  
**Date:** February 2026

---

## 🎯 Overview

An AI-powered resume creation system that generates ATS-optimized resumes with intelligent scoring using Google's Gemini AI.


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