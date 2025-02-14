# Используем образ Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /code

# Устанавливаем все необходимые зависимости для работы с Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg2 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    xdg-utils \
    libxss1

# Устанавливаем ключ для Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-archive-keyring.gpg

# Добавляем репозиторий Google Chrome
RUN echo "deb [signed-by=/usr/share/keyrings/google-archive-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Обновляем репозитории и устанавливаем Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Проверяем версию Google Chrome
RUN google-chrome --version

# Копируем requirements.txt и устанавливаем зависимости
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в контейнер
COPY . .
