from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os

@CrewBase
class Newgroq():
    """Newgroq crew with 3 tasks"""
    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        # Verify API key is set
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY environment variable is not set!")
        
        # Create LLM instance once
        self.llm_instance = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=api_key,
            temperature=0.3
        )
        print(f"✅ LLM initialized with Groq")
    
    @agent
    def skill_gap_analyzer(self) -> Agent:
        return Agent(
            role="Senior Career Development Analyst",
            goal="Analyze the user's current skills, experience level, and career goals to identify critical skill gaps and learning opportunities in {industry}",
            backstory="You're a veteran HR consultant with 15+ years of experience in talent development across Fortune 500 companies. You've helped thousands of professionals identify their blind spots and unlock their potential. You provide specific, actionable insights with real-world examples.",
            llm=self.llm_instance,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def learning_path_designer(self) -> Agent:
        return Agent(
            role="Educational Curriculum Architect",
            goal="Design a personalized, actionable learning path based on identified skill gaps for achieving {career_goal} in {industry}",
            backstory="You're an expert instructional designer who has created learning programs for top tech companies and educational institutions. You understand adult learning principles, microlearning strategies, and the balance between theory and practical application. You curate the best resources from MOOCs, bootcamps, books, and hands-on projects.",
            llm=self.llm_instance,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def action_planner(self) -> Agent:
        return Agent(
            role="Executive Performance Coach",
            goal="Create a detailed, day-by-day 30-day action plan that synthesizes all insights into concrete, achievable daily tasks for {career_goal}",
            backstory="You're a high-performance coach who works with executives and ambitious professionals to break down overwhelming goals into manageable daily actions. You understand habit formation, accountability systems, and realistic time management.",
            llm=self.llm_instance,
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def skill_gap_analysis_task(self) -> Task:
        return Task(
            description="Give a **short skill gap analysis** for {career_goal} in {industry}. List top 3 technical, 2 soft, and 2 domain skill gaps. Include key certifications.",
            expected_output="Markdown summary of top skill gaps and priorities. Keep very short (<500 tokens).",
            agent=self.skill_gap_analyzer(),
        )
    
    @task
    def learning_path_design_task(self) -> Task:
        return Task(
            description="Using skill gaps, create a **brief learning path** for {career_goal}. Include courses, projects, and certifications. Consider {time_commitment} hrs/week.",
            expected_output="Short markdown roadmap with phases and key resources (<500 tokens).",
            agent=self.learning_path_designer(),
        )
    
    @task
    def action_plan_task(self) -> Task:
        return Task(
            description="Combine all outputs into a **short 30-day plan** for {career_goal}. Include main daily tasks and weekly goals.",
            expected_output="Short markdown plan with key tasks and weekly checkpoints (<500 tokens).",
            agent=self.action_planner(),
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Career Accelerator crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
