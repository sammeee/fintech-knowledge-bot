FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 7860

# Start FastAPI backend
#CMD ["streamlit", "run", "app_spaces.py", "--server.port=7860", "--server.address=0.0.0.0"]
CMD ["streamlit", "run", "app_spaces.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false", "--server.enableCORS=false"]
