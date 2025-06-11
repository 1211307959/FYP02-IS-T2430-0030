# Deployment Guide - Revenue Prediction System

## Overview
This guide covers deploying the Revenue Prediction System to production environments, including setup procedures, configuration management, monitoring, and maintenance.

## Production Architecture

### System Components
- **Frontend:** Next.js application (React-based)
- **Backend:** Flask API server with LightGBM model
- **Model:** Ethical Time-Enhanced LightGBM model files
- **Data:** CSV files for training and reference data

### Deployment Options
1. **Local Production:** Single server deployment
2. **Cloud Deployment:** Scalable cloud infrastructure
3. **Container Deployment:** Docker-based deployment
4. **Serverless:** Function-based deployment

## Prerequisites

### System Requirements
- **Operating System:** Linux/Ubuntu 20.04+ (recommended), Windows 10+, macOS 10.15+
- **Python:** 3.9 or higher
- **Node.js:** 18.0 or higher
- **Memory:** Minimum 4GB RAM, 8GB recommended
- **Storage:** Minimum 2GB free space
- **Network:** Port 3000 (frontend) and 5000 (backend) available

### Dependencies
```bash
# Python packages
pip install -r requirements.txt

# Node.js packages  
npm install
```

## Local Production Deployment

### 1. Environment Setup

Create production environment configuration:

```bash
# Create production environment file
cat > .env.production << EOF
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:5000
FLASK_ENV=production
FLASK_DEBUG=false
API_HOST=0.0.0.0
API_PORT=5000
EOF
```

### 2. Frontend Build

Build the Next.js application for production:

```bash
# Install dependencies
npm ci --only=production

# Build application
npm run build

# Start production server
npm start
```

### 3. Backend Setup

Configure and start the Flask API:

```bash
# Ensure model files are present
ls -la *.pkl

# Start production API server
python combined_time_enhanced_ethical_api.py
```

### 4. Process Management

Use PM2 or systemd for process management:

#### Using PM2
```bash
# Install PM2
npm install -g pm2

# Start frontend
pm2 start npm --name "frontend" -- start

# Start backend  
pm2 start combined_time_enhanced_ethical_api.py --name "backend" --interpreter python3

# Save PM2 configuration
pm2 save
pm2 startup
```

#### Using systemd
Create service files for automatic startup:

```bash
# Frontend service
sudo tee /etc/systemd/system/revenue-frontend.service << EOF
[Unit]
Description=Revenue Prediction Frontend
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/path/to/idssnew
ExecStart=/usr/bin/npm start
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Backend service
sudo tee /etc/systemd/system/revenue-backend.service << EOF
[Unit]
Description=Revenue Prediction Backend
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/path/to/idssnew
ExecStart=/usr/bin/python3 combined_time_enhanced_ethical_api.py
Restart=always
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl enable revenue-frontend
sudo systemctl enable revenue-backend
sudo systemctl start revenue-frontend
sudo systemctl start revenue-backend
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (t3.medium recommended)
# Ubuntu 20.04 LTS
# Security group: HTTP (80), HTTPS (443), SSH (22), Custom (3000, 5000)

# Connect and setup
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip nodejs npm nginx -y
```

#### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/yourusername/idssnew.git
cd idssnew

# Install Python dependencies
pip3 install -r requirements.txt

# Install Node dependencies
npm ci --only=production

# Build frontend
npm run build
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/revenue-prediction
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/revenue-prediction /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Google Cloud Platform

#### 1. App Engine Deployment

Create `app.yaml`:
```yaml
runtime: python39

env_variables:
  FLASK_ENV: production

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

Deploy:
```bash
gcloud app deploy
```

#### 2. Cloud Run Deployment

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY --from=frontend /app/.next ./.next
COPY --from=frontend /app/public ./public

EXPOSE 5000
CMD ["python", "combined_time_enhanced_ethical_api.py"]
```

Deploy:
```bash
gcloud run deploy revenue-prediction --source . --platform managed
```

## Docker Deployment

### 1. Multi-Stage Dockerfile

```dockerfile
# Frontend build stage
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Backend stage
FROM python:3.9-slim AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/public ./public

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 3000 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start command
CMD ["python", "combined_time_enhanced_ethical_api.py"]
```

### 2. Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  revenue-app:
    build: .
    ports:
      - "80:5000"
      - "3000:3000"
    environment:
      - FLASK_ENV=production
      - NODE_ENV=production
    volumes:
      - ./data:/app/data:ro
      - model-data:/app/models
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - revenue-app
    restart: unless-stopped

volumes:
  model-data:
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration Management

### 1. Environment Variables

```bash
# Production environment variables
export NODE_ENV=production
export FLASK_ENV=production
export API_HOST=0.0.0.0
export API_PORT=5000
export FRONTEND_PORT=3000
export MODEL_PATH=/app/models
export DATA_PATH=/app/data
export LOG_LEVEL=INFO
export MAX_WORKERS=4
```

### 2. Configuration Files

Create `config/production.py`:
```python
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    
    # API Configuration
    HOST = os.environ.get('API_HOST', '0.0.0.0')
    PORT = int(os.environ.get('API_PORT', 5000))
    
    # Model Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', './models')
    DATA_PATH = os.environ.get('DATA_PATH', './data')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Performance
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 4))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
```

## Security Configuration

### 1. HTTPS Setup

Using Let's Encrypt with Certbot:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Security Headers

Add to Nginx configuration:
```nginx
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
```

### 3. API Security

Update Flask application:
```python
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app, origins=['https://your-domain.com'])

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/predict-revenue', methods=['POST'])
@limiter.limit("100 per minute")
def predict_revenue():
    # Implementation
    pass
```

## Monitoring and Logging

### 1. Application Monitoring

#### Health Checks
```python
# Enhanced health check endpoint
@app.route('/health')
def health_check():
    try:
        # Check model loading
        model_status = check_model_health()
        
        # Check data access
        data_status = check_data_access()
        
        # Check memory usage
        memory_usage = get_memory_usage()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'model_loaded': model_status,
            'data_accessible': data_status,
            'memory_usage_mb': memory_usage,
            'version': '1.0.0'
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

#### Metrics Collection
```python
# Add metrics collection
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(request.method, request.endpoint).inc()
    REQUEST_LATENCY.observe(time.time() - request.start_time)
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### 2. Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/revenue_prediction.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Revenue Prediction API startup')
```

### 3. External Monitoring

#### Uptime Monitoring
- Use services like Pingdom, UptimeRobot, or StatusCake
- Monitor both frontend (port 3000) and backend (port 5000)
- Set up alerts for downtime

#### Performance Monitoring
- New Relic, Datadog, or custom Prometheus setup
- Monitor response times, error rates, and resource usage
- Set up alerts for performance degradation

## Backup and Recovery

### 1. Data Backup

```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backup/revenue-prediction"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup model files
cp *.pkl "$BACKUP_DIR/$DATE/"

# Backup data files
cp data/*.csv "$BACKUP_DIR/$DATE/"

# Backup configuration
cp -r config "$BACKUP_DIR/$DATE/"

# Create archive
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"

# Remove old backups (keep 30 days)
find "$BACKUP_DIR" -name "backup-*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup-$DATE.tar.gz"
```

### 2. Disaster Recovery

```bash
#!/bin/bash
# restore.sh - Restore from backup

BACKUP_FILE=$1
RESTORE_DIR="/tmp/restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

# Extract backup
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Stop services
sudo systemctl stop revenue-frontend
sudo systemctl stop revenue-backend

# Restore files
cp "$RESTORE_DIR"/*/*.pkl ./
cp "$RESTORE_DIR"/*/data/*.csv ./data/
cp -r "$RESTORE_DIR"/*/config ./

# Start services
sudo systemctl start revenue-backend
sudo systemctl start revenue-frontend

echo "Restore completed from $BACKUP_FILE"
```

## Performance Optimization

### 1. Backend Optimization

```python
# Use Gunicorn for production
# gunicorn_config.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 5
```

Start with:
```bash
gunicorn -c gunicorn_config.py combined_time_enhanced_ethical_api:app
```

### 2. Frontend Optimization

```javascript
// next.config.js production optimizations
module.exports = {
  experimental: {
    optimizeCss: true,
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}
```

### 3. Database Optimization

For larger datasets, consider:
- PostgreSQL for structured data storage
- Redis for caching frequently accessed predictions
- Connection pooling for database connections

## Troubleshooting

### Common Issues

#### 1. Model Loading Failures
```bash
# Check model files
ls -la *.pkl
file *.pkl

# Verify Python environment
python -c "import lightgbm; print(lightgbm.__version__)"

# Test model loading
python -c "from revenue_predictor_time_enhanced_ethical import load_model; load_model()"
```

#### 2. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep -E ':(3000|5000)'

# Kill conflicting processes
sudo lsof -ti:5000 | xargs kill -9
```

#### 3. Memory Issues
```bash
# Monitor memory usage
free -h
top -p $(pgrep -f "python.*combined_time_enhanced_ethical_api")

# Adjust worker processes
export MAX_WORKERS=2
```

### Log Analysis

```bash
# Monitor application logs
tail -f logs/revenue_prediction.log

# Monitor system logs
journalctl -u revenue-backend -f

# Check error patterns
grep -E "(ERROR|CRITICAL)" logs/revenue_prediction.log | tail -20
```

## Maintenance

### 1. Regular Updates

```bash
#!/bin/bash
# maintenance.sh - Weekly maintenance script

# Update dependencies
pip install -r requirements.txt --upgrade
npm update

# Clean up logs
find logs/ -name "*.log" -mtime +7 -delete

# Restart services
sudo systemctl restart revenue-backend
sudo systemctl restart revenue-frontend

# Health check
curl -f http://localhost:5000/health || echo "Health check failed"
```

### 2. Model Updates

```bash
#!/bin/bash
# update_model.sh - Model update procedure

# Backup current model
cp revenue_model_time_enhanced_ethical.pkl revenue_model_backup_$(date +%Y%m%d).pkl

# Deploy new model
cp new_model/revenue_model_time_enhanced_ethical.pkl ./

# Test new model
python -c "from revenue_predictor_time_enhanced_ethical import load_model; load_model()"

# Restart backend
sudo systemctl restart revenue-backend

# Verify health
sleep 5
curl -f http://localhost:5000/health
```

For additional deployment scenarios and advanced configurations, refer to the API documentation and testing guide. 