FROM python:3.11-slim

WORKDIR /app

# Копируем requirements из подпапки aquacontrol
COPY aquacontrol/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код из подпапки aquacontrol
COPY aquacontrol/ .

RUN adduser --disabled-password --gecos '' --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "aq_main:app", "--host", "0.0.0.0", "--port", "8000"]
