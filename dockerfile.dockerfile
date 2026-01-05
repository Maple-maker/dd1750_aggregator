FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pdf_parser.py .
COPY form_generator.py .

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV PORT=5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
