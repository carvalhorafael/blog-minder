import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importing tools
from blog_minder.tools.seo_performance_analyzer import GetPagesMetrics
from blog_minder.tools.blog_posts_manager import FetchPostsSaveToDatabase
from blog_minder.tools.blog_posts_enhancers import MarkPostsForImprovement

# LLM Models
from langchain_community.llms import Ollama

ollama_base_url = os.environ["OLLAMA_BASE_URL"]
gemma2 = Ollama(
    model = "gemma2",
    base_url = ollama_base_url)


@CrewBase
class ContentPerformanceAnalyzerCrew():
    """Content Performance Analyzer Crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
	
    @agent
    def blog_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['blog_editor'],
            verbose=True,
            allow_delegation=False,
            llm=gemma2,
            tools=[FetchPostsSaveToDatabase()]
        )        
    
    @agent
    def junior_data_analyst(self) -> Agent:
        return Agent(
			config=self.agents_config['junior_data_analyst'],
			verbose=True,
			allow_delegation=False,
			llm=gemma2,
            tools=[GetPagesMetrics(), MarkPostsForImprovement()]
		)
    
    @task
    def fetch_all_posts_save_to_database_task(self) -> Task:
        return Task(
			config=self.tasks_config['fetch_all_posts_save_to_database_task'],
			agent=self.blog_editor()			
		)
    
    @task
    def get_posts_metrics_task(self) -> Task:
        return Task(
			config=self.tasks_config['get_posts_metrics_task'],
			agent=self.junior_data_analyst()			
		)	
    
    @task
    def mark_posts_to_be_improved_task(self) -> Task:
        return Task(
			config=self.tasks_config['mark_posts_to_be_improved_task'],
			agent=self.junior_data_analyst()			
		)	
    

    @crew
    def crew(self) -> Crew:
        """Creates the Content Performance Analyzer Crew"""
        return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)