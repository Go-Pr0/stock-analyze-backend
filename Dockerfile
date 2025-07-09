FROM python:3.11-slim

# Disable .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Working directory inside the container
WORKDIR /app

# Install dependencies first for better cache utilisation
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY . ./

# Expose FastAPI default port (Railway will override with $PORT)
EXPOSE 8000

# Railway will use the startCommand from railway.json
# This is a fallback for local development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 