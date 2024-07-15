import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importing tools
from blog_minder.tools.blog_posts_manager import FetchAndSavePostsContent, UpdatePostStatus
from blog_minder.tools.seo_performance_analyzer import IdentifyWinningPost
from crewai_tools import FileReadTool
# from blog_minder.tools.cannibalization_content_identifier import FindDuplicatesAndSimilarities

# LLM Models
from langchain_community.llms import Ollama
ollama_base_url = os.environ["OLLAMA_BASE_URL"]
llama3 = Ollama(
    model = "llama3",
    base_url = ollama_base_url)
gemma2 = Ollama(
    model = "gemma2",
    base_url = ollama_base_url)
gemma2_27b = Ollama(
    model = "gemma2:27b",
    base_url = ollama_base_url)
mistral = Ollama(
    model = "mistral",
    base_url = ollama_base_url)


@CrewBase
class ContentConsolidationCrew():
	"""Content Consolidation Crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def content_evaluator(self) -> Agent:
		return Agent(
			config=self.agents_config['content_evaluator'],
			verbose=True,
			allow_delegation=False,
			memory=False,
			llm=gemma2
		)
	
	@agent
	def content_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_writer'],
			verbose=True,
			allow_delegation=False,
			memory=False,
			llm=gemma2,
			tools=[FileReadTool()]
		)

	@agent
	def blog_editor(self) -> Agent:
		return Agent(
			config=self.agents_config['blog_editor'],
			verbose=True,
			allow_delegation=False,
			memory=False,
			llm=gemma2,
			tools=[UpdatePostStatus(), FetchAndSavePostsContent()]
		)

	@task
	def decide_winning_post_task(self) -> Task:
		return Task(
			config=self.tasks_config['decide_winning_post_task'],
			agent=self.content_evaluator(),
			tools=[IdentifyWinningPost()]
		)
	
	@task
	def fetch_and_save_content_of_posts_task(self) -> Task:
		return Task(
			config=self.tasks_config['fetch_and_save_content_of_posts_task'],
			agent=self.blog_editor()
		)
	
	@task
	def put_the_losing_post_in_draft_task(self) -> Task:
		return Task(
			config=self.tasks_config['put_the_losing_post_in_draft_task'],
			agent=self.blog_editor(),
			tools=[UpdatePostStatus()]
		)
	
	@task
	def merge_and_improve_winner_post_content_task(self) -> Task:
		return Task(
			config=self.tasks_config['merge_and_improve_winner_post_content_task'],
			agent=self.content_writer()
		)
	# @task
	# def merge_and_improve_post_content_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['merge_and_improve_post_content_task'],
	# 		agent=self.content_writer(),
	# 		context=[self.decide_winning_post_task()]
	# 	)

	# @task
	# def update_winner_and_loser_posts(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['update_winner_and_loser_posts'],
	# 		agent=self.blog_editor(),
	# 		context=[self.merge_and_improve_post_content_task()]
	# 	)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the Content Consolidation Crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)