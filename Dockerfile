FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-jdk \
    mecab libmecab-dev mecab-ipadic-utf8 \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /etc/mecabrc /usr/local/etc/mecabrc

RUN pip install --upgrade pip setuptools wheel Cython

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader punkt punkt_tab

COPY . .

EXPOSE 3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
