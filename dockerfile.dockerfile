FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
ENV PORT=5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
