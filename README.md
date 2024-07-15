# BlogMinder Crew
Welcome to the BlogMinder Crew project, powered by [crewAI](https://crewai.com).

## Running the Project
To kickstart your crew of AI agents and begin task execution:

1. Start `Ollama` (only to Mac Users, read **Setup** section below)
2. Run docker containers
    - `docker compose up -d`
3. Enter to crewAI container
    - `docker compose exec crewai bash`
4. Put your crew to work:
    - `poetry run blog_minder`

This last command initializes the blog-minder Crew, assembling the agents and assigning them tasks as defined in your configuration.

## Understanding Your Crew
The blog-minder Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.


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


## All other stuffs 
For all other things you should use Docker.

- Start containers
    - `docker-compose up -d`

# Open Ollama-WebUI
A positive side effect of this project is the possibility of interacting with LLM models from the browser (similar to ChatGPT). To do this, simply:

- open the browser
- enter the address: `http://localhost:8080/`

# Stop docker containers
- `docker-compose stop`