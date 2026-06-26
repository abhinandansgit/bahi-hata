# Python 3.11 slim variant for lightweight Linux container
FROM python:3.11-slim-bullseye

# Set environment variables for Python optimization and Docker output
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies necessary for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project
COPY . .

# Collect static files directly into the container
RUN python manage.py collectstatic --noinput

# Expose the Gunicorn port
EXPOSE 8000

# Start Gunicorn server directly bypassing manage.py runserver
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bahihata.wsgi:application"]
