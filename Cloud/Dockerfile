FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

RUN mkdir -p /data

CMD ["python", "app.py"]
