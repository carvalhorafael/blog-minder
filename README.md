# BlogMinder
Welcome to the BlogMinder project. The objective of this project is to delegate maintenance and content creation tasks for a blog to AI.

To achieve this objective, this project uses a set of crews powered by [crewAI](https://crewai.com).

## Running the Project
To kickstart your crew of AI agents and begin task execution:

1. Start `Ollama` (only to Mac Users, read **Setup** section below)
2. Run docker containers
    - `docker compose up -d`
3. Enter to crewAI container
    - `docker compose exec crewai bash`
4. Put your crew to work:
    - `poetry run blog_minder`

This last command initializes the blog-minder, bringing crews together with their agents and assigning them tasks as defined in their configuration.

## Understanding the project
The blog-minder is made up of several crews, each one created to perform complex activities in the project.

Each crew has a file with the suffix `_crew.py` in which it is possible to find its set of AI agents, each with roles, objectives and tools.

These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file describes the capabilities and configurations of each agent.

## Understanding each crew
### Content Integrity Crew
Responsible for:
- download the list of all blog posts and save it in a CSV file;
- identify which posts are experiencing content cannibalization due to being duplicates or very similar posts.

File: `content_integrity_crew.py`.

### Content Consolidation Crew
This crew always works with two duplicate or very similar posts. And for every two posts the crew is responsible for improving the content of the best positioned post and unpublishing the content of the worst positioned post (removing content duplication).

In detail, this team is responsible for:
- determine which post is the best and worst positioned in Google search;
- download the content of both posts;
- improve the best positioned post by adding elements from the worst positioned one;
- update the content of the best positioned post with the new content created;
- change the status of the worst positioned post to draft;
- change the status of the best positioned post to pending

File: `content_consolidation_crew.py`.

# Setup the project
## Ollama to local LLM models
### MacOS users
Ollama via Docker on Mac OS cannot access GPU processing, as explained here: https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image

> We recommend running Ollama alongside Docker Desktop for macOS in order for Ollama to enable GPU acceleration for models.

Therefore, you need to install and run Ollama locally.

### Windows and Linux users
Ollama can run with GPU acceleration inside Docker containers for Nvidia GPUs.
Just check `docker-compose.yml` and uncomment the snippets.

### After install Ollama
Pull the models, just like:
- `ollama pull llama3`
- `ollama pull gemma2`
- `ollama pull mistral`


## Docker for all other dependencies
For all other dependencies you should use Docker.

- Start containers
    - `docker-compose up -d`

## API Settings and Keys
All settings must be stored in a `.env` file in the project directory root. For security reasons this file is not versioned.

Create a file called `.env` in the project directory root with the following content:

~~~
# For the native tool that searches the internet
SERPER_API_KEY=

# OpenAI API key for using GPTs models
OPENAI_API_KEY=

# Ollama server URL on localhost
OLLAMA_BASE_URL=

# To connect to the wordpress blog.
BLOG_URL=
WORDPRESS_USER=
WORDPRESS_APP_PASSWORD=

# To access Google Search Console
GOOGLE_SEARCH_CONSOLE_JSON_CREDENTIAL=
GOOGLE_SEARCH_CONSOLE_SITE_DOMAIN=

# Paths to some utils files
LIST_OF_DUPLICATE_POSTS_PATH=
BLOG_POSTS_CSV_FILE_PATH=
~~~

## Directory for temporary files
Agents create several temporary files while carrying out their tasks. These temporary files are not versioned, but you need to create the directory structure below so that agents can create the files.

~~~
tmp
  |
  credentials
  |
  posts
~~~

## Credentials for Google Search Console
The credentials for accessing the Google Search Console API are in a `.json` file that must be stored in `/tmp/credentials`.

The path to this file must be added to the `GOOGLE_SEARCH_CONSOLE_JSON_CREDENTIAL` variable in the `.env` file.

# Open Ollama-WebUI
A positive side effect of this project is the possibility of interacting with LLM models from the browser (similar to ChatGPT). To do this, simply:

- open the browser
- enter the address: `http://localhost:8080/`

# Stop docker containers
- `docker-compose stop`