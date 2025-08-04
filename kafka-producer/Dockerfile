# kafka-producer Dockerfile
FROM python:3.9

WORKDIR /src

# Copy and install requirements first (better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "producer.py"]