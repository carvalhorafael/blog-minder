import os
import json
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput

# Importing tools
from blog_minder.tools.blog_posts_manager import FetchAndSavePostsContent, UpdatePostStatus, SavePostContent, UpdatePostContent
from blog_minder.tools.seo_performance_analyzer import IdentifyWinningPost
from crewai_tools import FileReadTool

# LLM Models
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

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

# About Temperature - 0 to 1
# Higher values like 0.8 will make the output more random, 
# while lower values like 0.2 will make it more focused and deterministic.
gpt_4o = ChatOpenAI(
	model = 'gpt-4o',
	temperature = 0.8)
gpt_3_turbo = ChatOpenAI(
	model = 'gpt-3.5-turbo',
	temperature = 0.8)


# Callbacks
def save_new_post_callback(output: TaskOutput, duplicate_hash: str):
	content = output.raw_output.replace("```html", "").replace("```", "") # remove possible html formating code
	filepath = f'tmp/posts/{duplicate_hash}_winner_new.html'
	with open(filepath, 'w') as file:
            file.write(content)


@CrewBase
class ContentConsolidationCrew():
	"""Content Consolidation Crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def __init__(self, inputs):
		self.inputs = inputs

	@agent
	def content_evaluator(self) -> Agent:
		return Agent(
			config=self.agents_config['content_evaluator'],
			verbose=True,
			allow_delegation=False,
			llm=gemma2
		)
	
	@agent
	def content_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_writer'],
			verbose=True,
			allow_delegation=False,
			llm=gpt_4o,
			tools=[FileReadTool()]
		)

	@agent
	def blog_editor(self) -> Agent:
		return Agent(
			config=self.agents_config['blog_editor'],
			verbose=True,
			allow_delegation=False,
			llm=gemma2,
			tools=[UpdatePostStatus(), FetchAndSavePostsContent(), UpdatePostContent()]
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
			agent=self.blog_editor(),
			context=[self.decide_winning_post_task()]
		)
	
	@task
	def merge_and_improve_winner_post_content_task(self) -> Task:
		duplicate_hash = self.inputs['duplicate_hash']
		return Task(
			config=self.tasks_config['merge_and_improve_winner_post_content_task'],
			agent=self.content_writer(),
			context=[self.decide_winning_post_task()],
			callback=self.create_callback(save_new_post_callback, duplicate_hash)
		)
	
	# Wraps the callback to pass the duplicate_hash as parameter
	def create_callback(self, save_new_post_callback, duplicate_hash):
		def wrapper(output: TaskOutput):
			return save_new_post_callback(output, duplicate_hash)
		return wrapper
	
	@task
	def put_the_losing_post_in_draft_task(self) -> Task:
		return Task(
			config=self.tasks_config['put_the_losing_post_in_draft_task'],
			agent=self.blog_editor(),
			context=[self.decide_winning_post_task()],
			tools=[UpdatePostStatus()]
		)
	
	@task
	def put_the_winning_post_in_pending_task(self) -> Task:
		return Task(
			config=self.tasks_config['put_the_winning_post_in_pending_task'],
			agent=self.blog_editor(),
			context=[self.decide_winning_post_task()],
			tools=[UpdatePostStatus()]
		)

	@task
	def update_winner_post_content_task(self) -> Task:
		return Task(
			config=self.tasks_config['update_winner_post_content_task'],
			agent=self.blog_editor(),
			context=[self.decide_winning_post_task()],
			tools=[UpdatePostContent()]
		)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the Content Consolidation Crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)