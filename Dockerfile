FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY ./main.py /app/main.py
COPY ../ai_engine /app/ai_engine
COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
