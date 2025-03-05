FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY config-production.ini config.ini

EXPOSE 5000

CMD ["python", "serve_orderclerk_trades.py"]
