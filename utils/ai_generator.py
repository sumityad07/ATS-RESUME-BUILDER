import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import time

load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(f"✅ Gemini API configured with key: {GOOGLE_API_KEY[:10]}...")
else:
    print("⚠️ WARNING: No GOOGLE_API_KEY found!")


def generate_resume_content(input_data):
    """
    Use Gemini AI to generate optimized resume content
    """
    
    # Check if API key is set
    if not GOOGLE_API_KEY:
        print("⚠️ No API key - using fallback")
        return format_basic_resume(input_data)
    
    # Create comprehensive prompt
    prompt = create_resume_prompt(input_data)
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"\n🔄 Attempt {retry_count + 1}/{max_retries}")
            
            # Initialize Gemini model
            model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Using stable model
            
            print(f"📤 Sending request to Gemini AI...")
            print(f"📝 Prompt length: {len(prompt)} characters")
            
            # Generate content with configuration
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings={
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            
            # Check if response exists and has text
            if not response or not hasattr(response, 'text'):
                print(f"⚠️ No response or no text attribute")
                print(f"Response: {response}")
                retry_count += 1
                time.sleep(2)
                continue
            
            ai_content = response.text
            
            if not ai_content or len(ai_content) < 100:
                print(f"⚠️ Response too short: {len(ai_content)} chars")
                print(f"Content: {ai_content[:200]}")
                retry_count += 1
                time.sleep(2)
                continue
            
            print(f"✅ AI Response received: {len(ai_content)} characters")
            print(f"📄 First 200 chars: {ai_content[:200]}")
            
            # Parse AI response
            resume_data = parse_ai_response(ai_content, input_data)
            
            # Validate parsed data
            if not resume_data.get('summary') or len(resume_data.get('summary', '')) < 20:
                print("⚠️ Parsed data seems incomplete, retrying...")
                retry_count += 1
                time.sleep(2)
                continue
            
            print("✅ Resume data parsed successfully!")
            return resume_data
            
        except Exception as e:
            print(f"❌ Error on attempt {retry_count + 1}: {e}")
            import traceback
            traceback.print_exc()
            retry_count += 1
            time.sleep(2)
    
    # If all retries failed, use fallback
    print("⚠️ All AI attempts failed, using enhanced fallback")
    return format_basic_resume(input_data)


def create_resume_prompt(data):
    """Create detailed prompt for Gemini AI"""
    
    prompt = f"""Act as an expert ATS resume writer. Create a highly professional, ATS-optimized resume.

CANDIDATE DETAILS:
Name: {data['full_name']}
Email: {data['email']}
Phone: {data['phone']}
Target Role: {data['target_role']}

EXPERIENCE PROVIDED:
{data.get('experience', 'Create entry-level experience')}

PROJECTS PROVIDED:
{data.get('projects', 'Create 2 relevant projects')}

EDUCATION PROVIDED:
{data.get('education', 'Create appropriate education')}

SKILLS PROVIDED:
{data.get('skills', 'Suggest comprehensive skills')}

CERTIFICATIONS PROVIDED:
{data.get('certifications', 'None')}
"""
    
    if data.get('job_description'):
        prompt += f"""
JOB DESCRIPTION TO MATCH:
{data['job_description'][:1000]}

CRITICAL: Extract keywords from this JD and use them throughout the resume.
"""
    
    prompt += f"""

CREATE A COMPLETE RESUME WITH THESE EXACT SECTIONS:

PROFESSIONAL SUMMARY:
Write a compelling 3-sentence summary for a {data['target_role']}. Include specific skills and career goals. Make it impactful and professional.

SKILLS:
List 12-15 technical and soft skills relevant to {data['target_role']}. Include programming languages, frameworks, tools, and soft skills. Format as comma-separated list.

EXPERIENCE:
Expand the provided experience into 2-3 professional roles with:
- Job Title | Company Name
- Duration (Month Year - Month Year)
- 4-5 bullet points per role with action verbs (Developed, Implemented, Led, Designed)
- Include metrics and numbers (increased by X%, reduced by Y, led team of Z)
- Show technical skills used
If no experience provided, create realistic internship/project-based roles.

PROJECTS:
Expand the provided projects into 2-3 detailed projects with:
- Project Name | Technologies Used
- Problem solved and approach taken
- Technical implementation details
- Measurable results or impact
Make them impressive and technical.

EDUCATION:
Format the education professionally:
- Degree Name (Full form)
- University/College Name
- Graduation Year
- GPA/CGPA if strong
- Relevant coursework

CERTIFICATIONS:
List certifications, online courses, or achievements:
- Certification Name - Issuing Organization (Year)
Make it professional.

CRITICAL FORMATTING RULES:
1. Use EXACTLY these section headers: PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION, CERTIFICATIONS
2. Make content detailed and professional
3. Use numbers and metrics
4. Include action verbs
5. Make it ATS-friendly
6. NO placeholders like "To be added" or "Not provided"
7. Create complete, realistic content

OUTPUT THE COMPLETE RESUME NOW:"""
    
    return prompt


def parse_ai_response(ai_text, original_data):
    """Parse Gemini AI response into structured format"""
    
    print("📝 Parsing AI response...")
    
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
    
    # Clean up formatting
    ai_text = ai_text.replace('**', '').replace('##', '').replace('#', '')
    ai_text = re.sub(r'\*\s', '• ', ai_text)
    
    print(f"Cleaned text length: {len(ai_text)}")
    
    # More flexible extraction patterns
    patterns = {
        'summary': r'PROFESSIONAL SUMMARY:?\s*\n+((?:(?!\n\s*(?:SKILLS|EXPERIENCE|PROJECTS|EDUCATION|CERTIFICATIONS):).)+)',
        'skills': r'SKILLS:?\s*\n+((?:(?!\n\s*(?:EXPERIENCE|PROJECTS|EDUCATION|CERTIFICATIONS):).)+)',
        'experience': r'EXPERIENCE:?\s*\n+((?:(?!\n\s*(?:PROJECTS|EDUCATION|CERTIFICATIONS):).)+)',
        'projects': r'PROJECTS:?\s*\n+((?:(?!\n\s*(?:EDUCATION|CERTIFICATIONS):).)+)',
        'education': r'EDUCATION:?\s*\n+((?:(?!\n\s*CERTIFICATIONS:).)+)',
        'certifications': r'CERTIFICATIONS:?\s*\n+(.*?)$'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, ai_text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
            sections[key] = content
            print(f"✅ Extracted {key}: {len(content)} chars")
        else:
            print(f"⚠️ Could not extract {key}")
    
    # Validate critical sections
    critical_sections = ['summary', 'skills', 'experience']
    for section in critical_sections:
        if not sections[section] or len(sections[section]) < 20:
            print(f"❌ Critical section '{section}' is too short or missing!")
            print(f"Content: {sections[section][:100]}")
            # Don't use fallback for individual sections, let the retry handle it
    
    return sections


def format_basic_resume(data):
    """Enhanced fallback formatting"""
    
    print("🔄 Using ENHANCED fallback resume formatting...")
    
    role = data['target_role']
    
    # Generate detailed summary
    summary = f"Results-driven {role} with strong technical skills and proven ability to deliver high-quality solutions. Experienced in full software development lifecycle, from requirements gathering to deployment and maintenance. Passionate about leveraging cutting-edge technologies to solve complex problems and drive business value. Excellent communicator with demonstrated ability to collaborate effectively in team environments and adapt to rapidly changing requirements."
    
    # Generate comprehensive skills
    skills_map = {
        'software': "Python, JavaScript, Java, React, Node.js, Express, Django, Flask, HTML/CSS, SQL, PostgreSQL, MongoDB, Git, GitHub, Docker, REST APIs, Microservices, Agile/Scrum, Unit Testing, Problem Solving, Team Collaboration, Communication",
        'developer': "JavaScript, TypeScript, Python, React, Angular, Vue.js, Node.js, Express, RESTful APIs, GraphQL, HTML5, CSS3, SASS, Webpack, Git, CI/CD, Jest, Responsive Design, Problem Solving, Debugging, Code Review",
        'data': "Python, SQL, R, Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, Tableau, Power BI, Excel, Statistics, Machine Learning, Deep Learning, Data Visualization, ETL, A/B Testing, Critical Thinking, Communication",
        'engineer': "Python, Java, C++, Data Structures, Algorithms, System Design, Object-Oriented Programming, Database Design, Git, Linux, Testing, Debugging, CI/CD, AWS, Problem Solving, Analytical Skills"
    }
    
    skills = skills_map.get('software', "Python, JavaScript, Problem Solving, Team Collaboration, Communication, Git, Agile Methodologies")
    for key in skills_map:
        if key in role.lower():
            skills = skills_map[key]
            break
    
    # Add user-provided skills
    if data.get('skills'):
        user_skills = [s.strip() for s in data['skills'].split(',') if s.strip()]
        existing_skills = [s.strip() for s in skills.split(',')]
        combined_skills = list(dict.fromkeys(user_skills + existing_skills))  # Remove duplicates
        skills = ', '.join(combined_skills[:15])  # Limit to 15 skills
    
    # Generate detailed experience
    if data.get('experience') and len(data['experience'].strip()) > 20:
        experience = f"""{role} | {data.get('experience', 'Technology Company')}
June 2023 - Present
• Developed and deployed 10+ features for production applications serving 50,000+ users, improving user engagement by 35%
• Implemented robust backend APIs using modern frameworks, achieving 99.9% uptime and sub-200ms response times
• Collaborated with cross-functional team of 8 members in Agile environment, participating in daily standups, sprint planning, and retrospectives
• Conducted comprehensive code reviews and mentored 2 junior developers, improving code quality and team productivity
• Optimized database queries and application performance, reducing page load time by 45% and server costs by 20%

Technical Intern | Previous Company
January 2023 - May 2023
• Contributed to development of customer-facing web application using modern JavaScript frameworks
• Implemented 15+ unit tests achieving 90% code coverage and reducing bugs in production by 30%
• Participated in agile ceremonies and collaborated with designers to implement pixel-perfect UI components
• Gained hands-on experience with CI/CD pipelines, automated testing, and deployment workflows"""
    else:
        experience = f"""{role} Intern | Technology Solutions Inc.
June 2023 - August 2023
• Developed and deployed 5 new features for customer-facing web application using React and Node.js, improving user engagement by 25%
• Implemented RESTful APIs serving 10,000+ daily requests with 99.9% uptime and sub-100ms response times
• Collaborated with cross-functional team of 8 members in Agile environment, participating in daily standups and sprint planning
• Conducted code reviews and wrote comprehensive unit tests, achieving 85% code coverage
• Optimized database queries reducing page load time by 40% and improving overall application performance

Student Developer | University Computer Lab
September 2022 - May 2023
• Provided technical support and guidance to 200+ students on programming concepts and software development tools
• Developed internal tools and scripts automating routine tasks, saving 10+ hours of manual work per week
• Conducted peer tutoring sessions on data structures, algorithms, and best coding practices
• Maintained and updated lab equipment and software, ensuring 99% uptime for student access"""
    
    # Generate detailed projects
    if data.get('projects') and len(data['projects'].strip()) > 20:
        base_projects = data['projects']
        projects = f"""{base_projects}

Task Management Application | Python, Django, PostgreSQL, Docker
• Developed collaborative task management system with real-time updates using WebSockets and modern web technologies
• Designed and implemented RESTful API with JWT authentication serving 15+ endpoints with comprehensive documentation
• Created responsive UI with drag-and-drop functionality for intuitive task organization and project management
• Implemented automated testing suite with 90% code coverage and containerized application using Docker for easy deployment
• Achieved 500+ downloads and 4.5-star rating on GitHub with active community contributions"""
    else:
        projects = f"""E-Commerce Platform | React, Node.js, MongoDB, Stripe API, AWS
• Built full-stack online shopping platform with user authentication, product catalog, shopping cart, and secure payment integration
• Implemented advanced search and filtering functionality, recommendation engine, and order tracking system
• Achieved 95% test coverage using Jest and React Testing Library with automated CI/CD pipeline
• Deployed on AWS with load balancing and auto-scaling, handling 1000+ concurrent users
• Integrated third-party APIs for payment processing, email notifications, and analytics tracking

Task Management Application | Python, Django, PostgreSQL, Docker, Redis
• Developed collaborative project management tool with real-time updates using WebSockets and caching for performance
• Designed RESTful API with JWT authentication, role-based access control, and comprehensive API documentation
• Created responsive UI with drag-and-drop functionality, Gantt charts, and deadline notifications
• Containerized application using Docker, implemented CI/CD with GitHub Actions, achieving 90% test coverage
• Deployed on cloud platform with automated backups and monitoring, serving 500+ active users"""
    
    # Generate education
    if data.get('education') and len(data['education'].strip()) > 20:
        education = data['education']
    else:
        education = """Bachelor of Technology in Computer Science
XYZ University
Expected Graduation: May 2024
CGPA: 8.5/10
Relevant Coursework: Data Structures and Algorithms, Database Management Systems, Web Technologies, Software Engineering, Operating Systems, Computer Networks, Machine Learning"""
    
    # Generate certifications
    if data.get('certifications') and len(data['certifications'].strip()) > 10:
        certifications = data['certifications']
    else:
        certifications = """• AWS Certified Cloud Practitioner - Amazon Web Services (2023)
• Full Stack Web Development Certification - Coursera (2023)
• Google Data Analytics Professional Certificate - Google (2023)
• JavaScript Algorithms and Data Structures - freeCodeCamp (2023)"""
    
    return {
        'name': data['full_name'],
        'email': data['email'],
        'phone': data['phone'],
        'target_role': data['target_role'],
        'summary': summary,
        'skills': skills,
        'experience': experience,
        'projects': projects,
        'education': education,
        'certifications': certifications
    }