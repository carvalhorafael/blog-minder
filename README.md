# Setup

## Ollama
### MacOS users
Ollama via Docker on Mac OS cannot access GPU processing, as explained here: https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image

> We recommend running Ollama alongside Docker Desktop for macOS in order for Ollama to enable GPU acceleration for models.

Therefore, you need to install and run Ollama locally.

### Windows and Linux users
Ollama can run with GPU acceleration inside Docker containers for Nvidia GPUs.
Just check `docker-compose.yml` and uncomment the snippets.

### After install Ollama
Pull `Llama 3` model:
`ollama pull llama3`


## All other stuffs 
For all other things you can use Docker.

- Start containers
    - `docker-compose up -d`

# Open Ollama-WebUI
A positive side effect of this project is the possibility of interacting with LLM models from the browser (similar to ChatGPT). To do this, simply:

- open the browser
- enter the address: `http://localhost:8080/`

# Run crewAI 
Open a terminal inside crewai:
- `docker-compose exec crewai bash`

Get crew to work:
- `python main.py`

# Stop docker containers
- `docker-compose stop`