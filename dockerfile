FROM python:3.9-slim

EXPOSE 9192

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    libpq-dev gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "APP.py","--server.port=9192"]