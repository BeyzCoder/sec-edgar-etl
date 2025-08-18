FROM python:3.11-slim

WORKDIR /app

COPY load_companyticker.py .

RUN pip install --no-cache-dir sqlalchemy psycopg2-binary

CMD ["python", "load_companyticker.py"]
