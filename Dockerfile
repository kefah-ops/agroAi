# Start from a lightweight Python image
FROM python:3.13-slim

# Create and set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose the port Railway expects
EXPOSE 8080

# Run database migrations before starting the app
CMD ["sh", "-c", "flask db upgrade || flask db create_all && gunicorn -b 0.0.0.0:8080 run:app"]
