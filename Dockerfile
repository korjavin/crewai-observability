# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Add build argument for commit SHA and set it as an env var
ARG COMMIT_SHA=unknown
ENV COMMIT_SHA=${COMMIT_SHA}

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the project files into the container
COPY . .

# Install project dependencies
RUN poetry install --no-root --no-dev

# Command to run the application
CMD ["poetry", "run", "python", "main.py"]
