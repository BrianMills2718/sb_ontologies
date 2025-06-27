# Generated Dockerfile for SystemExecutionHarness
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy generated system
COPY . .

# Expose default port
EXPOSE 8080

# Run the generated system
CMD ["python", "main.py"]
