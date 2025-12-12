FROM python:3.10-slim

# Set working directory inside container to FullStack
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the producer code into /FullStack
COPY producer.py .

# Run the producer
CMD ["python", "producer.py"]
