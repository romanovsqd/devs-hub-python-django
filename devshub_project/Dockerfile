FROM python:3.14-slim

RUN groupadd -r groupdjango && useradd -r -g groupdjango userdjango

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

RUN apt update && apt upgrade -y && pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER userdjango

CMD ["gunicorn", "devshub.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
