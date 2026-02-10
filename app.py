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
# ============= MAIN CONTENT AREA =============
# ============= MAIN CONTENT AREA =============
st.header("📋 Build Your ATS-Optimized Resume")

# Create tabs for better organization
tab1, tab2 = st.tabs(["📝 Enter Details", "📊 Results"])

with tab1:
    # Create a single form for ALL inputs
    with st.form("resume_form", clear_on_submit=False):
        
        # Personal Information
        st.subheader("👤 Personal Information")
        col_a, col_b = st.columns(2)
        
        with col_a:
            form_name = st.text_input("Full Name*", placeholder="John Doe", key="form_name")
            form_email = st.text_input("Email*", placeholder="john@email.com", key="form_email")
        
        with col_b:
            form_phone = st.text_input("Phone*", placeholder="+1 234 567 8900", key="form_phone")
            form_role = st.text_input("Target Job Role*", placeholder="Software Engineer", key="form_role")
        
        # Optional: Job Description
        st.subheader("🎯 Job Description (Optional)")
        form_jd = st.text_area(
            "Paste Job Description",
            placeholder="Paste the job description here to optimize your resume...",
            height=120,
            key="form_jd"
        )
        
        # Optional: Upload Resume
        form_resume = st.file_uploader(
            "📄 Upload Existing Resume (Optional)",
            type=['pdf', 'docx'],
            key="form_resume"
        )
        
        # Education
        st.subheader("🎓 Education")
        form_education = st.text_area(
            "Education Details",
            placeholder="e.g., B.Tech in Computer Science, XYZ University (2020-2024)",
            height=100,
            key="form_education"
        )
        
        # Experience
        st.subheader("💼 Experience")
        form_experience = st.text_area(
            "Work Experience",
            placeholder="e.g., Software Intern at ABC Corp (Jun 2023 - Aug 2023)\n- Developed REST APIs...",
            height=150,
            key="form_experience"
        )
        
        # Projects
        st.subheader("🚀 Projects")
        form_projects = st.text_area(
            "Projects",
            placeholder="e.g., E-commerce Website\n- Built using React and Node.js...",
            height=150,
            key="form_projects"
        )
        
        # Skills
        st.subheader("⚡ Skills")
        form_skills = st.text_input(
            "Skills (comma-separated)",
            placeholder="Python, JavaScript, React, Node.js, MySQL, Git",
            key="form_skills"
        )
        
        # Certifications
        st.subheader("🏆 Certifications & Achievements")
        form_certifications = st.text_area(
            "Certifications & Achievements",
            placeholder="e.g., AWS Certified Developer\nHackathon Winner 2023",
            height=100,
            key="form_certifications"
        )
        
        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Generate ATS-Optimized Resume", use_container_width=True, type="primary")
    
    # Process form submission OUTSIDE the form
    if submitted:
        # Validate mandatory fields
        if not form_name or not form_name.strip():
            st.error("⚠️ Please enter your Full Name!")
        elif not form_phone or not form_phone.strip():
            st.error("⚠️ Please enter your Phone Number!")
        elif not form_email or not form_email.strip():
            st.error("⚠️ Please enter your Email!")
        elif not form_role or not form_role.strip():
            st.error("⚠️ Please enter your Target Job Role!")
        else:
            try:
                with st.spinner("🤖 AI is crafting your perfect resume... This may take 10-15 seconds."):
                    
                    # Parse uploaded resume if provided
                    existing_data = None
                    if form_resume:
                        try:
                            existing_data = parse_resume(form_resume)
                        except Exception as e:
                            st.warning(f"Could not parse uploaded resume: {e}")
                    
                    # Prepare input data
                    input_data = {
                        'full_name': form_name.strip(),
                        'phone': form_phone.strip(),
                        'email': form_email.strip(),
                        'target_role': form_role.strip(),
                        'education': form_education,
                        'experience': form_experience,
                        'projects': form_projects,
                        'skills': form_skills,
                        'certifications': form_certifications,
                        'job_description': form_jd,
                        'existing_data': existing_data
                    }
                    
                    # Generate resume
                    st.session_state.resume_data = generate_resume_content(input_data)
                    
                    # Calculate ATS score
                    st.session_state.ats_score = calculate_ats_score(
                        st.session_state.resume_data, 
                        form_jd,
                        form_role
                    )
                
                st.success("✅ Resume generated successfully!")
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating resume: {str(e)}")
                st.error("Please check your inputs and try again.")

# Display results in second tab
with tab2:
    if st.session_state.get('ats_score') and st.session_state.get('resume_data'):
        
        # Display ATS Score
        score_data = st.session_state.ats_score
        
        col_score1, col_score2, col_score3 = st.columns([1, 2, 1])
        
        with col_score2:
            score_color = (
                "🟢" if score_data['score'] >= 80 
                else "🟡" if score_data['score'] >= 60 
                else "🔴"
            )
            
            st.markdown(f"""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
                <h2>ATS Score</h2>
                <h1 style='font-size: 4rem; margin: 0;'>{score_color} {score_data['score']}/100</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Score breakdown
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Skill Match", f"{score_data['skill_match']}/25")
            st.progress(score_data['skill_match']/25)
        
        with col2:
            st.metric("Keywords", f"{score_data['keyword_relevance']}/25")
            st.progress(score_data['keyword_relevance']/25)
        
        with col3:
            st.metric("Role Alignment", f"{score_data['role_alignment']}/25")
            st.progress(score_data['role_alignment']/25)
        
        with col4:
            st.metric("Formatting", f"{score_data['formatting']}/25")
            st.progress(score_data['formatting']/25)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        st.info(score_data['explanation'])
        
        # Download buttons
        st.subheader("⬇️ Download Your Resume")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            pdf_file = create_pdf(st.session_state.resume_data)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_file,
                file_name=f"{st.session_state.resume_data['name'].replace(' ', '_')}_Resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col_dl2:
            docx_file = create_docx(st.session_state.resume_data)
            st.download_button(
                label="📥 Download DOCX",
                data=docx_file,
                file_name=f"{st.session_state.resume_data['name'].replace(' ', '_')}_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        # Resume Preview
        st.markdown("---")
        st.subheader("👀 Resume Preview")
        
        data = st.session_state.resume_data
        
        st.markdown(f"# {data['name']}")
        st.markdown(f"📞 {data['phone']} | 📧 {data['email']}")
        st.markdown("---")
        
        if data.get('summary'):
            st.subheader("Professional Summary")
            st.write(data['summary'])
        
        if data.get('skills'):
            st.subheader("Skills")
            st.write(data['skills'])
        
        if data.get('experience'):
            st.subheader("Experience")
            st.write(data['experience'])
        
        if data.get('projects'):
            st.subheader("Projects")
            st.write(data['projects'])
        
        if data.get('education'):
            st.subheader("Education")
            st.write(data['education'])
        
        if data.get('certifications'):
            st.subheader("Certifications & Achievements")
            st.write(data['certifications'])
    
    else:
        st.info("👈 Fill out the form in the 'Enter Details' tab and click 'Generate' to see your results here!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Made with ❤️ for Sophyra Platform | AI Intern Qualification Task</p>
    <p>Built with Streamlit & OpenAI GPT-4</p>
</div>
""", unsafe_allow_html=True)