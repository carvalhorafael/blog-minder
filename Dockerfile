# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Set environment variables for CrewAI
# ENV SERPER_API_KEY=your_serper_api_key
# ENV OPENAI_API_KEY=your_openai_api_key

# Run the application
# CMD ["python", "src/project_name/main.py"]

# Keep the container running
# CMD ["tail", "-f", "/dev/null"]
