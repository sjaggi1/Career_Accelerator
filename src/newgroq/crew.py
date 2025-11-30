from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class Newgroq():
    """Newgroq crew with 3 tasks"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        super().__init__()
        # Explicitly create Groq LLM instance
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.llm = LLM(
            model="groq/llama-3.1-8b-instant",
            temperature=0.3,
            api_key=api_key
        )
    # --------------------------
    # Agents
    # --------------------------
    @agent
    def skill_gap_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['skill_gap_analyzer'], 
            verbose=True,
            allow_delegation=False
        )

    @agent
    def learning_path_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['learning_path_designer'], 
            verbose=True,
            allow_delegation=False
        )

    @agent
    def action_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['action_planner'], 
            verbose=True,
            allow_delegation=False
        )

    # --------------------------
    # Tasks
    # --------------------------
    @task
    def skill_gap_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['skill_gap_analysis_task'], 
            agent=self.skill_gap_analyzer(),
        )

    @task
    def learning_path_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['learning_path_design_task'], 
            agent=self.learning_path_designer(),
        )

    @task
    def action_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['action_plan_task'], 
            agent=self.action_planner(),
        )

    # --------------------------
    # Crew
    # --------------------------
    @crew
    def crew(self) -> Crew:
        """Creates the Career Accelerator crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
