import streamlit as st
from utils.resume_parser import parse_resume
from utils.ai_generator import generate_resume_content
from utils.ats_scorer import calculate_ats_score
from utils.pdf_generator import create_pdf, create_docx
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ResumeAI Pro - ATS Resume Builder",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .score-box {
        padding: 2rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        font-size: 2rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📄 ResumeAI Pro</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">AI-Powered ATS-Friendly Resume Builder</p>', unsafe_allow_html=True)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'ats_score' not in st.session_state:
    st.session_state.ats_score = None

# Sidebar for input collection
st.sidebar.header("📝 Enter Your Details")

# Mandatory fields
with st.sidebar:
    st.subheader("🔴 Mandatory Information")
    full_name = st.text_input("Full Name*", placeholder="John Doe")
    phone = st.text_input("Phone Number*", placeholder="+1 234 567 8900")
    email = st.text_input("Email ID*", placeholder="john.doe@email.com")
    target_role = st.text_input("Target Job Role*", placeholder="Software Engineer")
    
    st.subheader("⚪ Optional Information")
    job_description = st.text_area(
        "Job Description (Paste JD here)", 
        placeholder="Paste the job description to optimize your resume...",
        height=150
    )
    
    uploaded_resume = st.file_uploader(
        "Upload Existing Resume (PDF/DOCX)", 
        type=['pdf', 'docx'],
        help="Upload your existing resume to extract and enhance information"
    )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Resume Information")
    
    # Additional details form
    with st.form("resume_details"):
        st.subheader("🎓 Education")
        education = st.text_area(
            "Education Details",
            placeholder="e.g., B.Tech in Computer Science, XYZ University (2020-2024)",
            height=100
        )
        
        st.subheader("💼 Experience")
        experience = st.text_area(
            "Work Experience",
            placeholder="e.g., Software Intern at ABC Corp (Jun 2023 - Aug 2023)\n- Developed REST APIs...",
            height=150
        )
        
        st.subheader("🚀 Projects")
        projects = st.text_area(
            "Projects",
            placeholder="e.g., E-commerce Website\n- Built using React and Node.js...",
            height=150
        )
        
        st.subheader("⚡ Skills")
        skills = st.text_input(
            "Skills (comma-separated)",
            placeholder="Python, JavaScript, React, Node.js, MySQL, Git"
        )
        
        st.subheader("🏆 Certifications & Achievements")
        certifications = st.text_area(
            "Certifications & Achievements",
            placeholder="e.g., AWS Certified Developer\nHackathon Winner 2023",
            height=100
        )
        
        submit_button = st.form_submit_button("🚀 Generate ATS-Optimized Resume")

# Generate resume when form is submitted

if submit_button:
    # Validate mandatory fields
    if not all([full_name, phone, email, target_role]):
        st.error("⚠️ Please fill all mandatory fields!")
    else:
        try:
            with st.spinner("🤖 AI is crafting your perfect resume..."):
                
                print("=== DEBUG: Starting resume generation ===")
                print(f"Name: {full_name}")
                print(f"Role: {target_role}")
                
                # Parse uploaded resume if provided
                existing_data = None
                if uploaded_resume:
                    print("Parsing uploaded resume...")
                    existing_data = parse_resume(uploaded_resume)
                    print(f"Parsed data: {existing_data is not None}")
                
                # Prepare input data
                input_data = {
                    'full_name': full_name,
                    'phone': phone,
                    'email': email,
                    'target_role': target_role,
                    'education': education,
                    'experience': experience,
                    'projects': projects,
                    'skills': skills,
                    'certifications': certifications,
                    'job_description': job_description,
                    'existing_data': existing_data
                }
                
                print("Calling AI generator...")
                # Generate optimized resume content using AI
                st.session_state.resume_data = generate_resume_content(input_data)
                print(f"Resume data generated: {st.session_state.resume_data is not None}")
                
                print("Calculating ATS score...")
                # Calculate ATS score
                st.session_state.ats_score = calculate_ats_score(
                    st.session_state.resume_data, 
                    job_description,
                    target_role
                )
                print(f"ATS Score: {st.session_state.ats_score['score']}")
                
            st.success("✅ Resume generated successfully!")
            st.balloons()  # Celebration effect!
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating resume: {str(e)}")
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

# Display results in the right column
with col2:
    st.header("📊 Results")
    
    if st.session_state.ats_score:
        score_data = st.session_state.ats_score
        
        # Display ATS Score
        score_color = (
            "green" if score_data['score'] >= 80 
            else "orange" if score_data['score'] >= 60 
            else "red"
        )
        
        st.markdown(f"""
        <div class="score-box">
            <h3>ATS Score</h3>
            <h1 style="color: {score_color};">{score_data['score']}/100</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Score breakdown
        st.subheader("📈 Score Breakdown")
        st.progress(score_data['skill_match']/100)
        st.caption(f"Skill Match: {score_data['skill_match']}/100")
        
        st.progress(score_data['keyword_relevance']/100)
        st.caption(f"Keyword Relevance: {score_data['keyword_relevance']}/100")
        
        st.progress(score_data['role_alignment']/100)
        st.caption(f"Role Alignment: {score_data['role_alignment']}/100")
        
        st.progress(score_data['formatting']/100)
        st.caption(f"Formatting: {score_data['formatting']}/100")
        
        # Explanation
        st.subheader("💡 Recommendations")
        st.info(score_data['explanation'])
        
        # Download buttons
        st.subheader("⬇️ Download Resume")
        
        if st.session_state.resume_data:
            col_pdf, col_docx = st.columns(2)
            
            with col_pdf:
                pdf_file = create_pdf(st.session_state.resume_data)
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_file,
                    file_name=f"{full_name.replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf"
                )
            
            with col_docx:
                docx_file = create_docx(st.session_state.resume_data)
                st.download_button(
                    label="📥 Download DOCX",
                    data=docx_file,
                    file_name=f"{full_name.replace(' ', '_')}_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

# Display generated resume preview
if st.session_state.resume_data:
    st.header("👀 Resume Preview")
    st.markdown("---")
    
    data = st.session_state.resume_data
    
    # Header
    st.markdown(f"# {data['name']}")
    st.markdown(f"📞 {data['phone']} | 📧 {data['email']}")
    
    # Professional Summary
    if 'summary' in data:
        st.subheader("Professional Summary")
        st.write(data['summary'])
    
    # Skills
    if 'skills' in data:
        st.subheader("Skills")
        st.write(data['skills'])
    
    # Experience
    if 'experience' in data:
        st.subheader("Experience")
        st.write(data['experience'])
    
    # Projects
    if 'projects' in data:
        st.subheader("Projects")
        st.write(data['projects'])
    
    # Education
    if 'education' in data:
        st.subheader("Education")
        st.write(data['education'])
    
    # Certifications
    if 'certifications' in data:
        st.subheader("Certifications & Achievements")
        st.write(data['certifications'])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Made with ❤️ for Sophyra Platform | AI Intern Qualification Task</p>
    <p>Built with Streamlit & OpenAI GPT-4</p>
</div>
""", unsafe_allow_html=True)