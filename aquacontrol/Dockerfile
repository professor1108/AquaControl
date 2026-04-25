FROM python:3.11-slim

WORKDIR /app

# Копируем только requirements.txt сначала (для кэширования слоёв)
COPY aquacontrol/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код основного сервиса из подпапки aquacontrol
COPY . .

# Убедимся, что есть __init__.py для корректных относительных импортов
# (если его нет в вашей папке – создайте пустой файл)
RUN touch /app/__init__.py

EXPOSE 8000

CMD ["uvicorn", "aq_main:app", "--host", "0.0.0.0", "--port", "8000"]
