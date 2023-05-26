

CMD ["python", "run.py"]

# Используем базовый образ Python
FROM python:3.10

# Установка переменных среды
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=127.43.41.41

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование зависимостей в контейнер
COPY requirements.txt .

# Установка зависимостей
RUN pip install -r requirements.txt

# Копирование остальных файлов в контейнер
COPY . .

# Запуск приложения при старте контейнера
CMD ["flask", "run"]

