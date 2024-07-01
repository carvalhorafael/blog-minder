import os
import yaml
from crewai import Agent, Task, Crew, Process
from tools.wordpress_reader import fetch_wordpress_posts
from tools.keyword_analyzer import keyword_analyzer
from tools.seo_keyword_suggestion import seo_keyword_suggestion
from tools.content_quality_analyzer import content_quality_analyzer
from tools.content_merger import content_merger

# Load agent configurations from YAML file
with open('config/agents.yaml', 'r') as file:
    agents_config = yaml.safe_load(file)

# Create agents from configurations
agents = {}
for agent_name, agent_info in agents_config.items():
    tools = [globals()[tool_name] for tool_name in agent_info['tools']]
    agents[agent_name] = Agent(
        role=agent_info['role'],
        goal=agent_info['goal'],
        verbose=True,
        memory=True,
        backstory=agent_info['backstory'],
        tools=tools
    )

# Load task configurations from YAML file
with open('config/tasks.yaml', 'r') as file:
    tasks_config = yaml.safe_load(file)

# Create tasks from configurations
tasks = []
for task_name, task_info in tasks_config.items():
    tasks.append(Task(
        description=task_info['description'],
        expected_output=task_info['expected_output'],
        agent=agents[task_info['agent']],
    ))

# Form the crew
crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.sequential
)

# Run the crew
result = crew.kickoff(inputs={'blog_url': 'https://example.com'})
print(result)
