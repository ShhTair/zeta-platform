FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-integrations.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-integrations.txt

COPY . .

CMD ["python", "main.py"]
