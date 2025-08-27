FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user with home directory
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Create necessary directories and set permissions
RUN mkdir -p analyses daily_results /home/appuser/.streamlit \
    && chown -R appuser:appuser /app /home/appuser \
    && chmod -R 755 /app /home/appuser

# Make startup script executable
RUN chmod +x start_production.sh

# Switch to non-root user
USER appuser

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose Streamlit port
EXPOSE 8501

# Start the application
CMD ["./start_production.sh"]