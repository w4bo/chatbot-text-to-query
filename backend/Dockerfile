FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Default command to start uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]