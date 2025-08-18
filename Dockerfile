FROM python:3.11-slim

WORKDIR /backendflask

COPY . .

RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*


RUN chmod +x scripts/*.sh

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
