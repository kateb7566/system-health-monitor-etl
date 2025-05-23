FROM python:3.12-slim as build-stage

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim as final-stage

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /app/__main__.py .

EXPOSE 5000

CMD ["python", "__main__.py"]