import os
import yaml
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from src.tools.blog_posts_reader import fetch_posts
# from src.tools.csv_reader import read_csv_file
# from src.tools.keyword_analyzer import keyword_analyzer
# from src.tools.seo_keyword_suggestion import seo_keyword_suggestion
# from src.tools.content_quality_analyzer import content_quality_analyzer
# from src.tools.content_merger import content_merger

# Define crewAI builtin Tools
read_posts_file_tool = FileReadTool(file_path=os.environ["POSTS_CSV_FILE_PATH"])

### OLLAMA (THANKS TO LANGCHAIN)
from langchain_community.llms import Ollama
llama3 = Ollama(
    model="llama3",
    base_url = os.environ["OLLAMA_BASE_URL"])
mistral = Ollama(
    model="mistral",
    base_url = os.environ["OLLAMA_BASE_URL"])

# Load agent configurations from YAML file
with open('config/agents.yaml', 'r') as file:
    agents_config = yaml.safe_load(file)

# Create agents from configurations
agents = {}
for agent_name, agent_info in agents_config.items():
    tools = [globals()[tool_name] for tool_name in agent_info['tools']]
    llm = globals()[agent_info['llm']]
    agents[agent_name] = Agent(
        role=agent_info['role'],
        goal=agent_info['goal'],
        verbose=True,
        memory=agent_info['memory'],
        backstory=agent_info['backstory'],
        llm=llm,
        tools=tools
    )

# Load task configurations from YAML file
with open('config/tasks.yaml', 'r') as file:
    tasks_config = yaml.safe_load(file)

# Create tasks from configurations
tasks = []
for task_name, task_info in tasks_config.items():
    # tools = [globals()[tool_name] for tool_name in task_info['tools']]
    tasks.append(Task(
        description=task_info['description'],
        expected_output=task_info['expected_output'],
        agent=agents[task_info['agent']],
        # tools=tools
    ))

# Form the crew
crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.sequential,
    verbose=2
)

# Run the crew
print("Starting the crew execution")
result = crew.kickoff(inputs={'blog_url': os.environ["BLOG_URL"]})
print(result)
