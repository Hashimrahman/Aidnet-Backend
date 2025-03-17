# # ai_service/Dockerfile
# FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements file
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install requirements.txt

# # Copy the entire project
# COPY . .

# # Expose port (used by Daphne)
# EXPOSE 8004

# # Run the application with Daphne
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8004", "ai_service.asgi:application"]

# ai_service/Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the entire project
COPY . .

# Ensure Redis is reachable before starting (no DB, so no migrate)
CMD ["sh", "-c", "sleep 10 && daphne -b 0.0.0.0 -p 8000 ai_service.asgi:application"]