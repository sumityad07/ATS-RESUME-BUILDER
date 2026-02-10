import re
from collections import Counter

def calculate_ats_score(resume_data, job_description, target_role):
    """
    Calculate comprehensive ATS score (0-100)
    """
    
    # Initialize scores
    skill_match_score = 0
    keyword_relevance_score = 0
    role_alignment_score = 0
    formatting_score = 0
    
    # 1. Skill Match (25 points)
    skill_match_score = calculate_skill_match(resume_data, job_description)
    
    # 2. Keyword Relevance (25 points)
    keyword_relevance_score = calculate_keyword_relevance(resume_data, job_description, target_role)
    
    # 3. Role Alignment (25 points)
    role_alignment_score = calculate_role_alignment(resume_data, target_role)
    
    # 4. Formatting (25 points)
    formatting_score = calculate_formatting_score(resume_data)
    
    # Total score
    total_score = skill_match_score + keyword_relevance_score + role_alignment_score + formatting_score
    
    # Generate explanation
    explanation = generate_score_explanation(
        total_score,
        skill_match_score,
        keyword_relevance_score,
        role_alignment_score,
        formatting_score
    )
    
    return {
        'score': round(total_score),
        'skill_match': round(skill_match_score),
        'keyword_relevance': round(keyword_relevance_score),
        'role_alignment': round(role_alignment_score),
        'formatting': round(formatting_score),
        'explanation': explanation
    }

def calculate_skill_match(resume_data, job_description):
    """Calculate how well resume skills match JD"""
    
    if not job_description:
        return 20  # Default score if no JD provided
    
    # Extract skills from resume
    resume_skills = extract_skills_list(resume_data.get('skills', ''))
    
    # Extract skills from JD
    jd_skills = extract_skills_from_text(job_description)
    
    if not jd_skills:
        return 20
    
    # Calculate match percentage
    matched_skills = set(resume_skills).intersection(set(jd_skills))
    match_percentage = len(matched_skills) / len(jd_skills) if jd_skills else 0
    
    return match_percentage * 25

def calculate_keyword_relevance(resume_data, job_description, target_role):
    """Calculate keyword relevance score"""
    
    if not job_description:
        return 20  # Default score
    
    # Combine all resume text
    resume_text = ' '.join([
        str(resume_data.get('summary', '')),
        str(resume_data.get('skills', '')),
        str(resume_data.get('experience', '')),
        str(resume_data.get('projects', ''))
    ]).lower()
    
    jd_text = job_description.lower()
    
    # Extract important keywords from JD
    jd_keywords = extract_keywords(jd_text)
    
    # Count how many JD keywords appear in resume
    matched_keywords = sum(1 for keyword in jd_keywords if keyword in resume_text)
    
    keyword_match_rate = matched_keywords / len(jd_keywords) if jd_keywords else 0
    
    return keyword_match_rate * 25

def calculate_role_alignment(resume_data, target_role):
    """Calculate how well resume aligns with target role"""
    
    role_keywords = {
        'software engineer': ['development', 'programming', 'coding', 'software', 'engineer', 'python', 'java'],
        'data scientist': ['data', 'analysis', 'machine learning', 'python', 'statistics', 'modeling'],
        'product manager': ['product', 'strategy', 'roadmap', 'stakeholder', 'agile', 'scrum'],
        'designer': ['design', 'ui', 'ux', 'figma', 'adobe', 'creative', 'user experience'],
        'marketing': ['marketing', 'campaign', 'seo', 'content', 'analytics', 'social media']
    }
    
    resume_text = ' '.join([
        str(resume_data.get('summary', '')),
        str(resume_data.get('experience', '')),
        str(resume_data.get('projects', ''))
    ]).lower()
    
    target_role_lower = target_role.lower()
    
    # Find matching role category
    relevant_keywords = []
    for role, keywords in role_keywords.items():
        if role in target_role_lower:
            relevant_keywords = keywords
            break
    
    if not relevant_keywords:
        return 20  # Default if role not in predefined list
    
    # Count keyword matches
    matches = sum(1 for keyword in relevant_keywords if keyword in resume_text)
    alignment_score = (matches / len(relevant_keywords)) * 25
    
    return min(alignment_score, 25)

def calculate_formatting_score(resume_data):
    """Calculate formatting and structure score"""
    
    score = 0
    
    # Check essential sections exist (5 points each)
    if resume_data.get('summary'):
        score += 5
    if resume_data.get('skills'):
        score += 5
    if resume_data.get('experience') or resume_data.get('projects'):
        score += 5
    if resume_data.get('education'):
        score += 5
    
    # Check contact info is present (5 points)
    if all([resume_data.get('name'), resume_data.get('email'), resume_data.get('phone')]):
        score += 5
    
    return min(score, 25)

def extract_skills_list(skills_text):
    """Extract individual skills from skills text"""
    if not skills_text:
        return []
    
    # Split by common delimiters
    skills = re.split(r'[,;|\n]', skills_text.lower())
    return [skill.strip() for skill in skills if skill.strip()]

def extract_skills_from_text(text):
    """Extract technical skills from text"""
    
    common_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue',
        'node.js', 'express', 'django', 'flask', 'spring boot',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes',
        'git', 'ci/cd', 'jenkins', 'terraform',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'html', 'css', 'typescript', 'rest api', 'graphql',
        'agile', 'scrum', 'jira', 'figma', 'adobe xd'
    ]
    
    text_lower = text.lower()
    found_skills = [skill for skill in common_skills if skill in text_lower]
    
    return found_skills

def extract_keywords(text):
    """Extract important keywords from text"""
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has'}
    
    # Split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Get most common keywords
    word_freq = Counter(keywords)
    top_keywords = [word for word, _ in word_freq.most_common(30)]
    
    return top_keywords

def generate_score_explanation(total, skill, keyword, role, formatting):
    """Generate human-readable score explanation"""
    
    explanation = []
    
    if total >= 80:
        explanation.append("✅ Excellent! Your resume is highly optimized for ATS.")
    elif total >= 60:
        explanation.append("⚠️ Good resume, but there's room for improvement.")
    else:
        explanation.append("❌ Your resume needs significant optimization for ATS.")
    
    if skill < 15:
        explanation.append("\n• Add more relevant technical skills matching the job description.")
    
    if keyword < 15:
        explanation.append("\n• Incorporate more keywords from the job description naturally.")
    
    if role < 15:
        explanation.append("\n• Better align your experience with the target role requirements.")
    
    if formatting < 20:
        explanation.append("\n• Ensure all standard sections are included (Summary, Skills, Experience, Education).")
    
    if total >= 80:
        explanation.append("\n\n💡 Your resume should pass most ATS systems successfully!")
    
    return ' '.join(explanation)