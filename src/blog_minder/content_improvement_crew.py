import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importing tools
from blog_minder.tools.seo_performance_analyzer import GetPagesMetrics

# LLM Models
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

ollama_base_url = os.environ["OLLAMA_BASE_URL"]
gemma2 = Ollama(
    model = "gemma2",
    base_url = ollama_base_url)

# About Temperature - 0 to 1
# Higher values like 0.8 will make the output more random, 
# while lower values like 0.2 will make it more focused and deterministic.
gpt_4o = ChatOpenAI(
	model = 'gpt-4o',
	temperature = 0.8)


@CrewBase
class ContentImprovementCrew():
    """Content Improvement Crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
	
    @agent
    def junior_data_analyst(self) -> Agent:
        return Agent(
			config=self.agents_config['junior_data_analyst'],
			verbose=True,
			allow_delegation=False,
			llm=gemma2,
            tools=[GetPagesMetrics()]
		)
    
    @task
    def get_posts_metrics_task(self) -> Task:
        return Task(
			config=self.tasks_config['get_posts_metrics_task'],
			agent=self.junior_data_analyst()			
		)	
    

    @crew
    def crew(self) -> Crew:
        """Creates the Content Improvement Crew"""
        return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)