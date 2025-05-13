FROM python:3.9-slim

WORKDIR /app/backend

ENV FLASK_APP=backend.app
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port the app runs on
EXPOSE 5005
CMD ["flask", "run", "--host=0.0.0.0", "--port=5005"]