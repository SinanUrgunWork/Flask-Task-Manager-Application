FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

COPY .env .env

ENV FLASK_APP=app

CMD ["flask", "run", "--host=0.0.0.0"]
