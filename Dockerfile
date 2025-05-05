# Use Python 3.9 as base image with explicit platform targeting
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY python_isda_cds/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY python_isda_cds/ ./python_isda_cds/

# Set Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the API
CMD ["python", "-m", "python_isda_cds.main"]