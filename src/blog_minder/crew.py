import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importing tools
from blog_minder.tools.csv_reader import ReadCsv
from blog_minder.tools.blog_posts_reader import FetchPosts
from blog_minder.tools.cannibalization_content_identifier import FindDuplicatesAndSimilarities

# LLM Models
from langchain_community.llms import Ollama
llama3 = Ollama(
    model="llama3",
    base_url = os.environ["OLLAMA_BASE_URL"])
gemma2 = Ollama(
    model="gemma2",
    base_url = os.environ["OLLAMA_BASE_URL"])
mistral = Ollama(
    model="mistral",
    base_url = os.environ["OLLAMA_BASE_URL"])


@CrewBase
class BlogMinderCrew():
	"""BlogMinder crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def content_downloader(self) -> Agent:
		return Agent(
			config=self.agents_config['content_downloader'],
			verbose=True,
			allow_delegation=False,
			memory=True,
			llm=gemma2
		)

	@agent
	def content_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['content_analyst'],
			verbose=True,
			allow_delegation=False,
			memory=True,
			llm=gemma2
		)

	@task
	def fetch_all_posts_task(self) -> Task:
		return Task(
			config=self.tasks_config['fetch_all_posts_task'],
			agent=self.content_downloader(),
			tools=[FetchPosts()]
		)

	@task
	def identify_posts_cannibalization_task(self) -> Task:
		return Task(
			config=self.tasks_config['identify_posts_cannibalization_task'],
			agent=self.content_analyst(),
			tools=[ReadCsv(), FindDuplicatesAndSimilarities()],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the BlogMinder crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)