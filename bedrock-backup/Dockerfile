FROM python:3.14-slim

RUN apt-get update
RUN apt-get install -y docker-cli bup

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backup.py backup.py
COPY mcbak mcbak

CMD ["python3", "backup.py"]
