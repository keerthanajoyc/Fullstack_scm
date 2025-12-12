FROM python:3.11-slim

WORKDIR /app

# Copy dependency file
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy ONLY the app folder correctly
COPY app/ ./app

# Make sure WORKDIR points to /app
WORKDIR /app

EXPOSE 8000

# Run the FastAPI app correctly from the package
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
