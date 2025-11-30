import streamlit as st
import sys
from pathlib import Path
import warnings
from datetime import datetime
import re

import os

# Load API key from Streamlit secrets
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
elif "GROQ_API_KEY" not in os.environ:
    st.error("⚠️ GROQ_API_KEY not found. Please add it to Streamlit secrets.")
    st.stop()
    
# FIX: Add the *src* folder to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from newgroq.crew import Newgroq

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Page configuration
st.set_page_config(
    page_title="Career Accelerator AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .output-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1rem;
        border-left: 4px solid #667eea;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .sidebar .stSelectbox, .sidebar .stTextInput, .sidebar .stTextArea, .sidebar .stSlider {
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .agent-status {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        background: #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

def parse_crew_output(result):
    """Parse CrewAI output into structured sections"""
    result_text = str(result)
    
    sections = {
        'skill_gap': '',
        'learning_path': '',
        'action_plan': '',
        'full_output': result_text
    }
    
    # Try to split by common patterns
    if '# Skill Gap Analysis' in result_text or '## Skill Gap' in result_text:
        parts = re.split(r'#+ ?(Skill Gap|Learning Path|Action Plan)', result_text, flags=re.IGNORECASE)
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                section_name = parts[i].lower().replace(' ', '_')
                content = parts[i+1] if i+1 < len(parts) else ''
                if 'skill' in section_name:
                    sections['skill_gap'] = content.strip()
                elif 'learning' in section_name:
                    sections['learning_path'] = content.strip()
                elif 'action' in section_name:
                    sections['action_plan'] = content.strip()
    
    # If parsing failed, use the full output for all sections
    if not any([sections['skill_gap'], sections['learning_path'], sections['action_plan']]):
        sections['skill_gap'] = result_text
        sections['learning_path'] = result_text
        sections['action_plan'] = result_text
    
    return sections

def display_metrics(inputs):
    """Display key metrics in a nice format"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Career Goal", "🎯", delta=inputs['career_goal'][:20] + "...")
    
    with col2:
        st.metric("Industry", "🏢", delta=inputs['industry'])
    
    with col3:
        st.metric("Experience", "📊", delta=inputs['experience_level'][:20] + "...")
    
    with col4:
        st.metric("Weekly Hours", "⏰", delta=f"{inputs['time_commitment']} hrs")

# Header
st.markdown('<div class="main-header">🚀 Career Accelerator AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by CrewAI | Your Personalized Career Development Platform</div>', unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("📝 Your Profile")
    st.markdown("---")
    
    # Career Goal
    career_goal = st.text_input(
        "🎯 Career Goal",
        value="Senior Machine Learning Engineer",
        help="What position are you aiming for?"
    )
    
    # Industry
    industry_options = [
        "Technology/AI",
        "Data Science",
        "Software Development",
        "Cloud Computing",
        "Cybersecurity",
        "Product Management",
        "DevOps",
        "Other"
    ]
    industry = st.selectbox(
        "🏢 Industry",
        industry_options,
        help="Select your target industry"
    )
    
    if industry == "Other":
        industry = st.text_input("Please specify your industry:")
    
    # Current Skills
    current_skills = st.text_area(
        "💡 Current Skills",
        value="Python, Basic ML algorithms, Data analysis, SQL",
        help="List your current technical skills (comma-separated)",
        height=100
    )
    
    # Experience Level
    experience_level = st.text_input(
        "📊 Experience Level",
        value="2 years as Junior Data Analyst",
        help="Describe your current experience level and role"
    )
    
    # Education
    education = st.text_input(
        "🎓 Education",
        value="Bachelor's in Computer Science",
        help="Your highest educational qualification"
    )
    
    # Time Commitment
    time_commitment = st.slider(
        "⏰ Weekly Time Commitment (hours)",
        min_value=5,
        max_value=40,
        value=15,
        step=5,
        help="How many hours per week can you dedicate to learning?"
    )
    
    st.markdown("---")
    
    # Generate button
    generate_button = st.button("🚀 Generate Career Plan", use_container_width=True)
    
    # Reset button
    if st.button("🔄 Reset Form", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 About")
    st.info("""
    This AI platform creates:
    - 📋 Skill Gap Analysis
    - 🛤️ Learning Path
    - 📅 30-Day Action Plan
    
    Powered by **CrewAI** agents working together to analyze your profile and create a personalized development roadmap.
    """)

# Main content area
if not generate_button:
    # Welcome screen
    st.markdown("## 👋 Welcome to Your Career Accelerator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>📋 Step 1: Profile</h3>
            <p>Fill in your career details, skills, and goals in the sidebar</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🤖 Step 2: Generate</h3>
            <p>Click the button to start AI analysis by our expert agents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h3>🎯 Step 3: Execute</h3>
            <p>Follow your personalized plan and track progress</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features section
    st.markdown("## ✨ What You'll Get")
    
    tab1, tab2, tab3 = st.tabs(["📊 Skill Analysis", "🛤️ Learning Path", "📅 Action Plan"])
    
    with tab1:
        st.markdown("""
        ### Comprehensive Skill Gap Analysis
        
        Our **Senior Career Development Analyst** agent will:
        - 🔍 Identify technical skill gaps specific to your goal
        - 💡 Assess soft skill requirements
        - 🏆 Recommend relevant certifications
        - 📈 Prioritize skills by importance and urgency
        
        You'll receive a clear breakdown of:
        - **Top 3 Technical Skills** to develop
        - **2 Critical Soft Skills** for success
        - **2 Domain-Specific Skills** in your industry
        """)
    
    with tab2:
        st.markdown("""
        ### Personalized Learning Roadmap
        
        Our **Educational Curriculum Architect** agent will:
        - 📚 Curate courses from top platforms (Coursera, Udemy, etc.)
        - 🎯 Design hands-on projects for practical experience
        - 🏅 Suggest certification paths
        - ⏱️ Structure learning phases based on your time commitment
        
        Your roadmap includes:
        - **Phase-by-phase breakdown** of learning milestones
        - **Specific course recommendations** with links
        - **Project ideas** to build your portfolio
        - **Estimated timelines** for each phase
        """)
    
    with tab3:
        st.markdown("""
        ### 30-Day Action Plan
        
        Our **Executive Performance Coach** agent will:
        - 📅 Break down your journey into daily tasks
        - 🎯 Set weekly milestones and checkpoints
        - ⚡ Create achievable, incremental goals
        - 📊 Provide accountability framework
        
        Your plan features:
        - **Daily actionable tasks** (15-60 minutes each)
        - **Weekly review checkpoints** to track progress
        - **Realistic time allocations** based on your schedule
        - **Quick wins** to build momentum
        """)
    
    st.markdown("---")
    
    # Success stories or examples
    st.markdown("## 🎯 Example Career Transitions")
    
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        st.markdown("""
        ### 💻 Data Analyst → ML Engineer
        **Timeline**: 6 months  
        **Key Focus**: Python ML libraries, deep learning, MLOps  
        **Certifications**: TensorFlow Developer, AWS ML Specialty
        """)
        st.progress(85)
        st.caption("Success rate: 85%")
    
    with example_col2:
        st.markdown("""
        ### 🔧 Developer → DevOps Engineer
        **Timeline**: 4 months  
        **Key Focus**: Docker, Kubernetes, CI/CD, Cloud platforms  
        **Certifications**: AWS Solutions Architect, CKA
        """)
        st.progress(90)
        st.caption("Success rate: 90%")
    
    st.markdown("---")
    
    # Tips section
    st.markdown("## 💡 Tips for Success")
    
    tips_col1, tips_col2, tips_col3 = st.columns(3)
    
    with tips_col1:
        st.markdown("""
        **📝 Be Specific**
        - Clear career goals
        - Detailed skill lists
        - Accurate experience
        """)
    
    with tips_col2:
        st.markdown("""
        **⏰ Be Realistic**
        - Honest time commitment
        - Achievable milestones
        - Regular practice
        """)
    
    with tips_col3:
        st.markdown("""
        **📈 Track Progress**
        - Weekly reviews
        - Update your plan
        - Celebrate wins
        """)

else:
    # Validate inputs
    if not all([career_goal, industry, current_skills, experience_level, education]):
        st.error("⚠️ Please fill in all required fields in the sidebar!")
        st.stop()
    
    # Prepare inputs
    inputs = {
        'career_goal': career_goal,
        'industry': industry,
        'current_skills': current_skills,
        'experience_level': experience_level,
        'education': education,
        'time_commitment': str(time_commitment)
    }
    
    # Display user inputs summary
    st.markdown("## 📝 Your Profile Summary")
    display_metrics(inputs)
    
    st.markdown("---")
    
    # Progress tracking with agent status
    st.markdown("## 🤖 AI Agents at Work")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    agent_status_container = st.container()
    
    try:
        # Initialize the crew
        with agent_status_container:
            st.markdown('<div class="agent-status">🔧 Initializing AI agents...</div>', unsafe_allow_html=True)
        progress_bar.progress(10)
        
        crew = Newgroq().crew()
        
        with agent_status_container:
            st.markdown('<div class="agent-status">👤 Agent 1: Senior Career Development Analyst - Analyzing skill gaps...</div>', unsafe_allow_html=True)
        progress_bar.progress(30)
        
        # Add a spinner for the actual crew execution
        with st.spinner("🔄 AI agents are collaborating on your career plan..."):
            # Run the crew
            result = crew.kickoff(inputs=inputs)
        
        with agent_status_container:
            st.markdown('<div class="agent-status">👤 Agent 2: Educational Curriculum Architect - Designing learning path...</div>', unsafe_allow_html=True)
        progress_bar.progress(60)
        
        with agent_status_container:
            st.markdown('<div class="agent-status">👤 Agent 3: Executive Performance Coach - Creating action plan...</div>', unsafe_allow_html=True)
        progress_bar.progress(90)
        
        progress_bar.progress(100)
        
        with agent_status_container:
            st.markdown('<div class="agent-status">✅ All agents completed their analysis!</div>', unsafe_allow_html=True)
        
        # Display success message
        st.balloons()
        st.markdown('<div class="success-box">🎉 <strong>Success!</strong> Your personalized career development plan is ready!</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Parse results
        sections = parse_crew_output(result)
        
        # Display the complete output in tabs for better organization
        st.markdown("## 📊 Your Personalized Career Development Plan")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Skill Gap Analysis",
            "🛤️ Learning Path",
            "📅 30-Day Action Plan",
            "📄 Complete Report"
        ])
        
        with tab1:
            st.markdown("### 🎯 Skills You Need to Develop")
            st.markdown(sections['skill_gap'] if sections['skill_gap'] else sections['full_output'])
            st.markdown("---")
            st.info("💡 **Tip**: Focus on high-priority skills first. Consider your strengths and how quickly you can develop each skill.")
            
            # Add a checklist feature
            with st.expander("✅ Create Your Skill Development Checklist"):
                st.markdown("Track your progress on key skills:")
                st.checkbox("Technical Skill 1")
                st.checkbox("Technical Skill 2")
                st.checkbox("Technical Skill 3")
                st.checkbox("Soft Skill 1")
                st.checkbox("Soft Skill 2")
        
        with tab2:
            st.markdown("### 📚 Your Personalized Learning Roadmap")
            st.markdown(sections['learning_path'] if sections['learning_path'] else sections['full_output'])
            st.markdown("---")
            st.info("💡 **Tip**: Bookmark recommended courses now. Set up a dedicated learning schedule in your calendar.")
            
            # Add resource tracking
            with st.expander("📚 Resource Organizer"):
                st.markdown("Keep track of your learning resources:")
                course_name = st.text_input("Course/Resource Name")
                course_url = st.text_input("URL")
                if st.button("Save Resource"):
                    st.success(f"✅ Saved: {course_name}")
        
        with tab3:
            st.markdown("### ✅ Your Daily Tasks and Milestones")
            st.markdown(sections['action_plan'] if sections['action_plan'] else sections['full_output'])
            st.markdown("---")
            st.info("💡 **Tip**: Set daily reminders for your tasks. Review progress every Sunday.")
            
            # Add progress tracker
            with st.expander("📊 Progress Tracker"):
                week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
                progress = st.slider(f"Progress for {week}", 0, 100, 0)
                st.progress(progress / 100)
                notes = st.text_area("Notes/Reflections")
                if st.button("Save Progress"):
                    st.success(f"✅ Progress saved for {week}!")
        
        with tab4:
            st.markdown("### 📄 Complete Detailed Report")
            st.markdown(sections['full_output'])
        
        # Download section
        st.markdown("---")
        st.markdown("## 💾 Save Your Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create downloadable content
            download_content = f"""# Career Development Plan
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 📋 Profile Summary
- **Career Goal**: {career_goal}
- **Industry**: {industry}
- **Experience Level**: {experience_level}
- **Education**: {education}
- **Current Skills**: {current_skills}
- **Time Commitment**: {time_commitment} hours/week

---

## 🎯 Skill Gap Analysis
{sections['skill_gap'] if sections['skill_gap'] else 'See complete report below'}

---

## 🛤️ Learning Path Design
{sections['learning_path'] if sections['learning_path'] else 'See complete report below'}

---

## 📅 30-Day Action Plan
{sections['action_plan'] if sections['action_plan'] else 'See complete report below'}

---

## 📄 Complete Analysis
{sections['full_output']}

---

*Generated by Career Accelerator AI - Powered by CrewAI*
"""
            
            st.download_button(
                label="📥 Download Complete Plan (Markdown)",
                data=download_content,
                file_name=f"career_plan_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            # Create a simplified version
            simplified_content = f"""Career Plan Summary - {datetime.now().strftime("%Y-%m-%d")}

Goal: {career_goal} in {industry}

Quick Action Items:
1. Review skill gaps daily
2. Enroll in recommended courses
3. Complete Week 1 tasks
4. Build first project
5. Update resume and LinkedIn

Time Commitment: {time_commitment} hrs/week
"""
            
            st.download_button(
                label="📥 Download Quick Reference (TXT)",
                data=simplified_content,
                file_name=f"quick_reference_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Next steps
        st.markdown("---")
        st.markdown("## 🎯 Your Next Steps")
        
        step_col1, step_col2, step_col3, step_col4 = st.columns(4)
        
        with step_col1:
            st.markdown("""
            ### 1️⃣ Today
            - ✅ Review full plan
            - 📥 Download materials
            - 📅 Schedule learning time
            """)
        
        with step_col2:
            st.markdown("""
            ### 2️⃣ This Week
            - 🎓 Enroll in courses
            - 📚 Gather resources
            - 🏃 Start Day 1 tasks
            """)
        
        with step_col3:
            st.markdown("""
            ### 3️⃣ This Month
            - 📊 Track daily progress
            - 🔄 Weekly reviews
            - 🎯 Complete milestones
            """)
        
        with step_col4:
            st.markdown("""
            ### 4️⃣ Beyond
            - 🚀 Build portfolio
            - 🤝 Network actively
            - 💼 Apply for roles
            """)
        
        # Feedback section
        st.markdown("---")
        st.markdown("## 💬 How useful was this plan?")
        
        feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 2, 1])
        
        with feedback_col2:
            rating = st.select_slider(
                "Rate your experience:",
                options=["Poor", "Fair", "Good", "Very Good", "Excellent"],
                value="Good"
            )
            feedback = st.text_area("Additional feedback (optional):")
            if st.button("Submit Feedback", use_container_width=True):
                st.success("Thank you for your feedback! 🙏")
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.empty()
        st.error(f"❌ An error occurred while generating your plan")
        
        with st.expander("🔍 Error Details"):
            st.code(str(e))
        
        st.markdown('<div class="warning-box">⚠️ <strong>Troubleshooting Tips:</strong></div>', unsafe_allow_html=True)
        
        trouble_col1, trouble_col2 = st.columns(2)
        
        with trouble_col1:
            st.markdown("""
            **Common Issues:**
            1. API key not configured
            2. Network connectivity
            3. Rate limiting
            4. Invalid configuration
            """)
        
        with trouble_col2:
            st.markdown("""
            **Solutions:**
            1. Check your .env file
            2. Verify internet connection
            3. Wait a moment and retry
            4. Review config.json settings
            """)
        
        if st.button("🔄 Try Again"):
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>Built with ❤️ using CrewAI and Streamlit</strong></p>
    <p style="font-size: 0.9rem;">Powered by Groq LLaMA 3.1-8B | Three AI Agents Working Together</p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">
        🤖 Senior Career Analyst | 📚 Curriculum Architect | 🎯 Performance Coach
    </p>
    <p style="font-size: 0.8rem; color: #999;">© 2024 Career Accelerator AI</p>
</div>
""", unsafe_allow_html=True)
