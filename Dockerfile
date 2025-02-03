FROM python:3.10-slim

WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY . /app/

ENV TZ=Europe/Madrid
CMD ["python", "main.py"]
