FROM python:3.11-slim

WORKDIR /app

COPY notifications/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notifications/ .

RUN adduser --disabled-password --gecos '' --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "n_main:app", "--host", "0.0.0.0", "--port", "8001"]
