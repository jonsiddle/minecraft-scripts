FROM python:3.14-slim

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY bridge.py bridge.py

EXPOSE 19132

CMD ["python3", "bridge.py"]
