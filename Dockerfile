FROM python:3.11-slim

WORKDIR /flaskcar

COPY . .

RUN apt-get update && apt-get install -y gcc libmariadb-dev && rm -rf /var/lib/apt/lists/*

RUN chmod +x scripts/*.sh

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]