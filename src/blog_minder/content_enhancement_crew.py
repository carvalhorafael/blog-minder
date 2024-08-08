import os
import sqlite3
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput

# Importing tools
# from blog_minder.tools.blog_posts_enhancers import AppendContentToPost


# LLM Models
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

gemma2 = Ollama(
    model = "gemma2",
    base_url = os.environ["OLLAMA_BASE_URL"])

# About Temperature - 0 to 1
# Higher values like 0.8 will make the output more random, 
# while lower values like 0.2 will make it more focused and deterministic.
gpt_4o = ChatOpenAI(
	model = 'gpt-4o',
	temperature = 0.8)


# Callbacks
def append_post_content_callback(output: TaskOutput, post_id: int, database_path: str, table_name: str):
    content = output.raw_output.replace("```html", "").replace("```", "") # remove possible html formating code    
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    cur.execute(f'''
        UPDATE {table_name}
        SET new_content = IFNULL(new_content, '') || ?
        WHERE id = ?
    ''', (content, post_id))
    conn.commit()
    conn.close()


@CrewBase
class ContentEnhancementCrew():
    """Content Enhancement Crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, inputs):
        self.inputs = inputs
          
    @agent
    def blog_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['blog_editor'],
            verbose=True,
            allow_delegation=False,
            llm=gemma2
        )

    @agent
    def content_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['content_analyst'],
            verbose=True,
            allow_delegation=False,
            llm=gpt_4o
        )
    
    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            verbose=True,
            allow_delegation=False,
            llm=gpt_4o
        )
    
    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'],
            verbose=True,
            allow_delegation=False,
            llm=gpt_4o
        )
    
    @task
    def analyze_article_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_article_task'],
            agent=self.content_analyst()
        )
    
    @task
    def recommend_improvements_task(self) -> Task:
        return Task(
            config=self.tasks_config['recommend_improvements_task'],
            agent=self.seo_specialist()
        )
    
    @task
    def rewrite_article_first_part_task(self) -> Task:
        post_id = self.inputs['post_id']
        database_path = self.inputs['database_path']
        table_name = self.inputs['table_name']
        return Task(
            config=self.tasks_config['rewrite_article_first_part_task'],
            agent=self.content_writer(),
            context=[self.recommend_improvements_task()],
            callback=self.create_callback(append_post_content_callback, post_id, database_path, table_name)
        )
    
    @task
    def rewrite_article_second_part_task(self) -> Task:
        post_id = self.inputs['post_id']
        database_path = self.inputs['database_path']
        table_name = self.inputs['table_name']
        return Task(
            config=self.tasks_config['rewrite_article_second_part_task'],
            agent=self.content_writer(),
            context=[self.recommend_improvements_task()],
            callback=self.create_callback(append_post_content_callback, post_id, database_path, table_name)
        )
    
    # Wraps the callback to pass the duplicate_hash as parameter
    def create_callback(self, append_post_content_callback, post_id, database_path, table_name):
        def wrapper(output: TaskOutput):
            return append_post_content_callback(output, post_id, database_path, table_name)
        return wrapper
    
    @crew
    def crew(self) -> Crew:
        """Creates the Content Enhancement Crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=2
        )
