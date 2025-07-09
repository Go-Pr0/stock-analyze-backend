FROM python:3.11-slim

# Disable .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Working directory inside the container
WORKDIR /app

# Install dependencies first for better cache utilisation
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY backend/ ./

# Expose FastAPI default port
EXPOSE 8000

# Provide sensible default (can be overridden at runtime)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 