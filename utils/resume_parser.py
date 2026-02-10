import PyPDF2
import pdfplumber
from docx import Document
import re

def parse_resume(uploaded_file):
    """
    Parse uploaded resume (PDF or DOCX) and extract information
    """
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        return parse_pdf(uploaded_file)
    elif file_type == 'docx':
        return parse_docx(uploaded_file)
    else:
        return None

def parse_pdf(pdf_file):
    """Extract text from PDF"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        return extract_resume_sections(text)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None

def parse_docx(docx_file):
    """Extract text from DOCX"""
    try:
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return extract_resume_sections(text)
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return None

def extract_resume_sections(text):
    """
    Extract structured information from resume text
    """
    # This is a simplified extraction - you can enhance with NLP
    
    data = {
        'raw_text': text,
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text),
        'education': extract_section(text, ['education', 'academic']),
        'experience': extract_section(text, ['experience', 'work history', 'employment']),
        'projects': extract_section(text, ['projects', 'personal projects']),
    }
    
    return data

def extract_email(text):
    """Extract email using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extract phone number"""
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_skills(text):
    """Extract skills section"""
    # Common skill keywords
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mysql',
        'mongodb', 'aws', 'docker', 'kubernetes', 'git', 'html', 'css',
        'machine learning', 'data science', 'tensorflow', 'pytorch'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill)
    
    return ', '.join(found_skills)

def extract_section(text, keywords):
    """Extract specific section based on keywords"""
    lines = text.split('\n')
    section_text = []
    capturing = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Check if this line is a section header
        if any(keyword in line_lower for keyword in keywords):
            capturing = True
            continue
        
        # Stop capturing if we hit another section header
        if capturing and line.isupper() and len(line) > 3:
            break
        
        if capturing and line.strip():
            section_text.append(line)
    
    return '\n'.join(section_text)