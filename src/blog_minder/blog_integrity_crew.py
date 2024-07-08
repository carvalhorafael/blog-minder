import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importing tools
from blog_minder.tools.blog_posts_manager import FetchPosts
from blog_minder.tools.cannibalization_content_identifier import FindDuplicatesAndSimilarities

# LLM Models
from langchain_community.llms import Ollama
gemma2 = Ollama(
    model = "gemma2",
    base_url = os.environ["OLLAMA_BASE_URL"])


@CrewBase
class BlogIntegrityCrew():
	"""Blog Integrity Crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def blog_editor(self) -> Agent:
		return Agent(
			config=self.agents_config['blog_editor'],
			verbose=True,
			allow_delegation=False,
			memory=False,
			llm=gemma2,
			tools=[FetchPosts()]
		)

	@agent
	def content_inspector(self) -> Agent:
		return Agent(
			config=self.agents_config['content_inspector'],
			verbose=True,
			allow_delegation=False,
			memory=False,
			llm=gemma2
		)

	@task
	def fetch_all_posts_task(self) -> Task:
		return Task(
			config=self.tasks_config['fetch_all_posts_task'],
			agent=self.blog_editor()
		)

	@task
	def identify_posts_cannibalization_task(self) -> Task:
		return Task(
			config=self.tasks_config['identify_posts_cannibalization_task'],
			agent=self.content_inspector(),
			tools=[FindDuplicatesAndSimilarities()]
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Blog Integrity Crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)