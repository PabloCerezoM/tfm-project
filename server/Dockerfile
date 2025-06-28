# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py ./

# Expose port (change if your app uses a different port)
EXPOSE 8000

# Start the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
