import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def generate_resume_content(input_data):
    """
    Use Gemini AI to generate optimized resume content
    """
    
    # Check if API key is set
    if not GOOGLE_API_KEY:
        print("⚠️ Warning: Google API key not found. Using fallback...")
        return format_basic_resume(input_data)
    
    # Create comprehensive prompt
    prompt = create_resume_prompt(input_data)
    
    try:
        # Try multiple models in order of preference
        model_names = [
            'gemini-2.5-flash',
            'gemini-flash-latest',
            'gemini-2.0-flash'
        ]
        
        model = None
        model_used = None
        
        for model_name in model_names:
            try:
                print(f"🔄 Trying model: {model_name}...")
                model = genai.GenerativeModel(model_name)
                model_used = model_name
                print(f"✅ Successfully loaded model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Model {model_name} not available: {e}")
                continue
        
        if not model:
            print("❌ No Gemini models available. Using fallback...")
            return format_basic_resume(input_data)
        
        print(f"📤 Sending request to Gemini AI ({model_used})...")
        
        # Generate content with safety settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Check if response was blocked
        if not response or not response.text:
            print("⚠️ Response was empty or blocked. Using fallback...")
            return format_basic_resume(input_data)
        
        ai_content = response.text
        
        print("✅ AI Response received successfully!")
        print(f"📊 Response length: {len(ai_content)} characters")
        
        # Parse AI response into structured format
        resume_data = parse_ai_response(ai_content, input_data)
        
        return resume_data
        
    except Exception as e:
        print(f"❌ Error generating resume with Gemini AI: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to basic formatting
        return format_basic_resume(input_data)


def create_resume_prompt(data):
    """Create detailed prompt for Gemini AI"""
    
    prompt = f"""You are an expert ATS (Applicant Tracking System) resume writer with 10+ years of experience. Create a professional, ATS-optimized resume that will pass automated screening systems.

**CANDIDATE INFORMATION:**
Name: {data['full_name']}
Email: {data['email']}
Phone: {data['phone']}
Target Role: {data['target_role']}

**PROVIDED INFORMATION:**
Education: {data.get('education') or 'Not provided - please create appropriate education for this role'}
Experience: {data.get('experience') or 'Not provided - create relevant entry-level or internship experience'}
Projects: {data.get('projects') or 'Not provided - create 2-3 relevant technical projects'}
Skills: {data.get('skills') or 'Not provided - suggest comprehensive technical and soft skills'}
Certifications: {data.get('certifications') or 'Not provided - suggest relevant certifications if appropriate'}
"""
    
    if data.get('job_description'):
        prompt += f"""
**TARGET JOB DESCRIPTION:**
{data['job_description'][:1500]}

🎯 CRITICAL: Carefully analyze this job description and:
1. Extract key technical skills, tools, and technologies mentioned
2. Identify important keywords and phrases
3. Match the experience level and requirements
4. Incorporate these naturally throughout the resume
"""
    
    prompt += """

**OUTPUT REQUIREMENTS:**

Generate a complete ATS-optimized resume using EXACTLY these section headers:

PROFESSIONAL SUMMARY:
[Write a compelling 2-3 sentence professional summary that:
- Highlights the candidate's key qualifications for the target role
- Includes 1-2 years of experience level (or "aspiring" for entry-level)
- Mentions 2-3 core technical competencies
- Shows enthusiasm and career direction
Example: "Results-driven Software Engineer with 2 years of experience in full-stack development. Proficient in React, Node.js, and Python with a proven track record of delivering scalable web applications. Passionate about clean code and user-centric design."]

SKILLS:
[List 12-15 relevant skills in this exact format, comma-separated:
Technical Skills: [programming languages, frameworks, tools]
Soft Skills: [communication, leadership, problem-solving, etc.]

Example: Python, JavaScript, React, Node.js, SQL, MongoDB, Git, Docker, AWS, RESTful APIs, Agile/Scrum, Problem Solving, Team Collaboration, Communication, Time Management]

EXPERIENCE:
[Create 1-2 professional experiences following this format:

Job Title | Company Name
Month Year - Month Year (or "Present")
• [Achievement with quantifiable metric] - Start with action verb (Developed, Implemented, Led, Designed, Optimized)
• [Technical contribution] - Mention specific technologies used
• [Business impact] - Show how your work added value (improved performance, reduced costs, increased efficiency)
• [Collaboration or leadership] - Demonstrate teamwork or initiative

Example:
Software Development Intern | Tech Solutions Inc.
June 2023 - August 2023
• Developed and deployed 5 new features for customer-facing web application using React and Node.js, improving user engagement by 25%
• Implemented RESTful APIs serving 10,000+ daily requests with 99.9% uptime
• Collaborated with cross-functional team of 8 members in Agile environment, participating in daily standups and sprint planning
• Optimized database queries reducing page load time by 40%

If no experience provided, create realistic internship or relevant project-based experience]

PROJECTS:
[Create 2-3 impressive projects following this format:

Project Name | Technologies Used
• [Problem statement or goal of the project]
• [Technical implementation - architecture, key features, algorithms used]
• [Measurable results or impact - users, performance, functionality]
• [Optional: GitHub link or live demo placeholder]

Example:
E-Commerce Platform | React, Node.js, MongoDB, Stripe API
• Built full-stack online shopping platform with user authentication, product catalog, and secure payment integration
• Implemented shopping cart functionality, order tracking, and admin dashboard with real-time analytics
• Achieved 95% test coverage using Jest and React Testing Library
• Deployed on AWS with CI/CD pipeline using GitHub Actions

Task Management App | Python, Django, PostgreSQL, Docker
• Developed collaborative task management system with real-time updates using WebSockets
• Designed and implemented RESTful API with JWT authentication serving 15+ endpoints
• Created responsive UI with drag-and-drop functionality for task organization
• Containerized application using Docker for easy deployment]

EDUCATION:
[Format education professionally:

Degree Name (e.g., Bachelor of Technology in Computer Science)
University/College Name
Graduation Year or Expected Graduation: Month Year
[Include GPA/Percentage only if above 7.5/10 or 75%]
[Optional: Relevant coursework: Data Structures, Algorithms, Database Systems, Web Development]

Example:
Bachelor of Technology in Computer Science
XYZ University
Expected Graduation: May 2024
CGPA: 8.5/10
Relevant Coursework: Data Structures, Algorithms, Database Management, Machine Learning, Web Technologies]

CERTIFICATIONS:
[List certifications, courses, or achievements:
• Certification Name - Issuing Organization (Year)
• Online Course - Platform Name (Year)
• Achievement or Award - Organization (Year)

Example:
• AWS Certified Cloud Practitioner - Amazon Web Services (2023)
• Full Stack Web Development - Coursera (2023)
• Winner, Smart India Hackathon - Government of India (2023)
• Google Data Analytics Professional Certificate - Google (2023)]

**CRITICAL ATS OPTIMIZATION RULES:**
1. ✅ Use standard section headers (no creative names)
2. ✅ Include action verbs: Developed, Implemented, Designed, Led, Optimized, Architected, Collaborated, Achieved
3. ✅ Add metrics and numbers: percentages, timelines, team sizes, user counts
4. ✅ Incorporate keywords naturally from job description
5. ✅ Use industry-standard terminology and acronyms
6. ✅ Keep formatting simple (no tables, columns, or graphics)
7. ✅ Make content scannable with bullet points
8. ✅ Ensure technical skills match job requirements
9. ✅ Show impact and results, not just responsibilities
10. ✅ Maintain consistent date formats and tenses

**IMPORTANT:** 
- Generate realistic, professional content
- Make it specific to the {data['target_role']} role
- Ensure all information is ATS-compliant
- Use the EXACT section headers provided above
- Be detailed and comprehensive

Generate the complete resume now:
"""
    
    return prompt


def parse_ai_response(ai_text, original_data):
    """Parse Gemini AI response into structured format"""
    
    print("📝 Parsing AI response into structured sections...")
    
    sections = {
        'name': original_data['full_name'],
        'email': original_data['email'],
        'phone': original_data['phone'],
        'target_role': original_data['target_role'],
        'summary': '',
        'skills': '',
        'experience': '',
        'projects': '',
        'education': '',
        'certifications': ''
    }
    
    # Clean up markdown formatting from AI response
    ai_text = ai_text.replace('**', '').replace('##', '').replace('#', '')
    ai_text = re.sub(r'\*\s', '• ', ai_text)  # Convert * to bullets
    
    # Define regex patterns for each section
    patterns = {
        'summary': r'PROFESSIONAL SUMMARY:?\s*\n+(.*?)(?=\n\s*SKILLS:|\n\s*TECHNICAL SKILLS:|$)',
        'skills': r'(?:SKILLS|TECHNICAL SKILLS):?\s*\n+(.*?)(?=\n\s*EXPERIENCE:|$)',
        'experience': r'EXPERIENCE:?\s*\n+(.*?)(?=\n\s*PROJECTS:|$)',
        'projects': r'PROJECTS:?\s*\n+(.*?)(?=\n\s*EDUCATION:|$)',
        'education': r'EDUCATION:?\s*\n+(.*?)(?=\n\s*CERTIFICATIONS:|$)',
        'certifications': r'CERTIFICATIONS:?\s*\n+(.*?)$'
    }
    
    # Extract each section
    for key, pattern in patterns.items():
        match = re.search(pattern, ai_text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # Clean up extra whitespace
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
            content = re.sub(r'[ \t]+', ' ', content)
            sections[key] = content
            print(f"✅ Extracted {key}: {len(content)} characters")
        else:
            print(f"⚠️ Could not extract {key} from AI response")
    
    # Fallback: Use original data if AI extraction failed
    for key in ['skills', 'experience', 'projects', 'education', 'certifications']:
        if not sections[key] and original_data.get(key):
            sections[key] = original_data[key]
            print(f"↩️ Using original {key} data")
    
    # Generate defaults for critical empty sections
    if not sections['summary']:
        sections['summary'] = generate_default_summary(original_data)
        print("🔄 Generated default summary")
    
    if not sections['skills']:
        sections['skills'] = generate_default_skills(original_data['target_role'])
        print("🔄 Generated default skills")
    
    if not sections['experience']:
        sections['experience'] = generate_default_experience(original_data['target_role'])
        print("🔄 Generated default experience")
    
    if not sections['projects']:
        sections['projects'] = generate_default_projects(original_data['target_role'])
        print("🔄 Generated default projects")
    
    if not sections['education']:
        sections['education'] = generate_default_education()
        print("🔄 Generated default education")
    
    if not sections['certifications']:
        sections['certifications'] = generate_default_certifications(original_data['target_role'])
        print("🔄 Generated default certifications")
    
    print("✅ Resume parsing complete!")
    return sections


def generate_default_summary(data):
    """Generate a professional summary"""
    role = data['target_role']
    return f"Motivated {role} with strong technical aptitude and passion for innovation. Demonstrated ability to quickly learn new technologies and contribute to team success. Seeking opportunities to apply skills in {role.lower()} and drive impactful results through creative problem-solving and collaboration."


def generate_default_skills(role):
    """Generate role-appropriate default skills"""
    role_lower = role.lower()
    
    skill_sets = {
        'software': "Python, JavaScript, Java, React, Node.js, HTML/CSS, SQL, Git, RESTful APIs, Agile Development, Problem Solving, Team Collaboration, Communication, Time Management",
        'developer': "JavaScript, Python, React, Angular, Node.js, Express, MongoDB, SQL, Git, Docker, RESTful APIs, Responsive Design, Problem Solving, Debugging, Team Collaboration",
        'engineer': "Python, Java, C++, Data Structures, Algorithms, System Design, Git, Linux, Testing, CI/CD, Problem Solving, Analytical Thinking, Communication, Team Collaboration",
        'data': "Python, SQL, R, Pandas, NumPy, Scikit-learn, Tableau, Power BI, Statistics, Machine Learning, Data Visualization, Excel, Problem Solving, Analytical Thinking, Communication",
        'analyst': "SQL, Python, Excel, Tableau, Power BI, Data Analysis, Statistical Analysis, Data Visualization, Critical Thinking, Problem Solving, Communication, Attention to Detail",
        'design': "Figma, Adobe XD, Sketch, Photoshop, Illustrator, UI/UX Design, Prototyping, Wireframing, User Research, Visual Design, Creativity, Communication, Collaboration",
        'product': "Product Strategy, Roadmap Planning, User Stories, Agile/Scrum, JIRA, Market Research, Data Analysis, Stakeholder Management, Communication, Leadership, Problem Solving",
        'marketing': "Digital Marketing, SEO/SEM, Google Analytics, Social Media Marketing, Content Creation, Email Marketing, A/B Testing, Communication, Creativity, Data Analysis"
    }
    
    # Find matching skill set
    for key, skills in skill_sets.items():
        if key in role_lower:
            return skills
    
    # Default generic skills
    return "Communication, Problem Solving, Team Collaboration, Critical Thinking, Time Management, Adaptability, Leadership, Attention to Detail, Project Management, Microsoft Office"


def generate_default_experience(role):
    """Generate role-appropriate default experience"""
    return f"""{role} Intern | Tech Company
June 2023 - August 2023
• Collaborated with cross-functional team of 6 members to develop and deploy new features for production applications
• Contributed to codebase improvements resulting in 15% performance enhancement and better code maintainability
• Participated in Agile ceremonies including daily standups, sprint planning, and retrospectives
• Gained hands-on experience with industry-standard tools, best practices, and professional development workflows

Student Technical Assistant | University Computer Lab
September 2022 - May 2023
• Provided technical support and guidance to 200+ students on software tools and programming concepts
• Troubleshot and resolved technical issues, improving lab efficiency by 20%
• Conducted peer tutoring sessions on programming fundamentals and debugging techniques"""


def generate_default_projects(role):
    """Generate role-appropriate default projects"""
    role_lower = role.lower()
    
    if 'software' in role_lower or 'developer' in role_lower or 'engineer' in role_lower:
        return """E-Commerce Web Application | React, Node.js, MongoDB, Stripe
• Built full-stack online shopping platform with user authentication, product catalog, and secure payment integration
• Implemented shopping cart, order management, and admin dashboard with real-time inventory tracking
• Achieved 95% test coverage using Jest and React Testing Library
• Deployed on AWS EC2 with automated CI/CD pipeline using GitHub Actions

Task Management System | Python, Django, PostgreSQL, Docker
• Developed collaborative project management tool with real-time updates using WebSockets
• Designed and implemented RESTful API with JWT authentication serving 20+ endpoints
• Created responsive UI with drag-and-drop functionality for intuitive task organization
• Containerized application using Docker for consistent deployment across environments"""
    
    elif 'data' in role_lower:
        return """Customer Segmentation Analysis | Python, Pandas, Scikit-learn, Tableau
• Analyzed 50,000+ customer records to identify distinct market segments using K-means clustering
• Built predictive model achieving 87% accuracy in customer behavior classification
• Created interactive Tableau dashboard for business stakeholders to explore insights
• Recommendations led to 15% improvement in targeted marketing campaign effectiveness

Sales Forecasting Model | Python, Time Series Analysis, Prophet
• Developed time series forecasting model to predict monthly sales with 92% accuracy
• Processed and cleaned 3 years of historical sales data across multiple product categories
• Implemented automated data pipeline for daily model updates and predictions
• Presented findings to management team with actionable business insights"""
    
    else:
        return f"""Personal Portfolio Website | HTML, CSS, JavaScript
• Designed and developed professional portfolio showcasing projects and technical skills
• Implemented responsive design ensuring optimal viewing across devices and screen sizes
• Integrated contact form with email functionality and added smooth animations
• Deployed using GitHub Pages with custom domain

Capstone Project: {role} Application
• Led team of 4 in developing comprehensive solution addressing real-world problem
• Applied Agile methodology with 2-week sprints and regular stakeholder presentations
• Conducted user testing with 25+ participants and incorporated feedback iteratively
• Presented final product to faculty panel and received distinction grade"""


def generate_default_education():
    """Generate default education section"""
    return """Bachelor of Technology in Computer Science
University Name
Expected Graduation: May 2024
CGPA: 8.2/10
Relevant Coursework: Data Structures and Algorithms, Database Management Systems, Web Technologies, Software Engineering, Operating Systems"""


def generate_default_certifications(role):
    """Generate role-appropriate certifications"""
    role_lower = role.lower()
    
    if 'software' in role_lower or 'developer' in role_lower:
        return """• Full Stack Web Development - freeCodeCamp (2023)
• JavaScript Algorithms and Data Structures - Coursera (2023)
• Git and GitHub Essentials - LinkedIn Learning (2023)"""
    
    elif 'data' in role_lower:
        return """• Google Data Analytics Professional Certificate - Google (2023)
• Python for Data Science - IBM Coursera (2023)
• SQL for Data Analysis - Udacity (2023)"""
    
    else:
        return """• Relevant Professional Development Courses - Online Platforms (2023)
• Technical Skill Certifications - Industry-Recognized Programs
• Continuing Education in Field of Specialization"""


def format_basic_resume(data):
    """Fallback basic formatting if AI completely fails"""
    
    print("🔄 Using complete fallback resume formatting...")
    
    return {
        'name': data['full_name'],
        'email': data['email'],
        'phone': data['phone'],
        'target_role': data['target_role'],
        'summary': generate_default_summary(data),
        'skills': data.get('skills') or generate_default_skills(data['target_role']),
        'experience': data.get('experience') or generate_default_experience(data['target_role']),
        'projects': data.get('projects') or generate_default_projects(data['target_role']),
        'education': data.get('education') or generate_default_education(),
        'certifications': data.get('certifications') or generate_default_certifications(data['target_role'])
    }