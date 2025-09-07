# Deployment Guide

This guide covers different deployment options for the Smart System Health Monitor.

## 🚀 Quick Deployment Options

### 1. Docker Compose (Recommended)

**Best for**: Production deployments, easy management

```bash
# Clone the repository
git clone https://github.com/sam170203/smart-system-health-monitor.git
cd smart-system-health-monitor

# Copy and edit configuration
cp env.example .env
# Edit .env with your settings

# Deploy
docker-compose up -d

# Access dashboard
open http://localhost:8501
```

**Advantages**:
- Easy to manage
- Automatic restarts
- Volume persistence
- Health checks
- Easy scaling

### 2. Docker (Single Container)

**Best for**: Simple deployments, testing

```bash
# Build image
docker build -f Dockerfile.enhanced -t smart-system-monitor .

# Run container
docker run -d \
  --name smart-system-monitor \
  -p 8501:8501 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/models:/app/models \
  --env-file .env \
  --restart unless-stopped \
  smart-system-monitor
```

### 3. Local Python Installation

**Best for**: Development, custom configurations

```bash
# Setup
python setup.py

# Start dashboard
streamlit run src/dashboard.py

# Start monitoring (separate terminal)
python monitor_enhanced.py
```

## 🌐 Cloud Deployment

### AWS EC2

1. **Launch EC2 instance**
   ```bash
   # Ubuntu 20.04 LTS recommended
   # t3.medium or larger
   # Security group: Allow port 8501
   ```

2. **Install Docker**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Deploy application**
   ```bash
   git clone https://github.com/sam170203/smart-system-health-monitor.git
   cd smart-system-health-monitor
   cp env.example .env
   # Edit .env
   docker-compose up -d
   ```

4. **Access dashboard**
   ```
   http://your-ec2-public-ip:8501
   ```

### Google Cloud Platform

1. **Create Compute Engine instance**
   ```bash
   gcloud compute instances create smart-monitor \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --tags=http-server
   ```

2. **Configure firewall**
   ```bash
   gcloud compute firewall-rules create allow-monitor \
     --allow tcp:8501 \
     --target-tags http-server
   ```

3. **Deploy application**
   ```bash
   # SSH into instance
   gcloud compute ssh smart-monitor
   
   # Follow AWS deployment steps
   ```

### Azure

1. **Create Virtual Machine**
   ```bash
   az vm create \
     --resource-group myResourceGroup \
     --name smart-monitor \
     --image UbuntuLTS \
     --size Standard_B2s \
     --admin-username azureuser
   ```

2. **Open port 8501**
   ```bash
   az vm open-port --port 8501 --resource-group myResourceGroup --name smart-monitor
   ```

3. **Deploy application**
   ```bash
   # SSH into VM
   ssh azureuser@your-vm-public-ip
   
   # Follow AWS deployment steps
   ```

## 🐳 Docker Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Monitoring Settings
MONITORING_INTERVAL=300
LOG_RETENTION_DAYS=30

# Alert Thresholds
CPU_THRESHOLD=80.0
RAM_THRESHOLD=80.0
DISK_THRESHOLD=90.0
NETWORK_THRESHOLD=500000

# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Notifications
EMAIL_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com

# Dashboard Settings
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0

# Machine Learning
ML_ENABLED=true
PREDICTION_HORIZON=10
```

### Docker Compose Services

The `docker-compose.yml` includes:

- **smart-monitor**: Main dashboard service
- **monitor-service**: Background monitoring service
- **postgres**: Optional database for persistent storage

### Volume Mounts

- `./logs:/app/logs` - Monitoring data
- `./models:/app/models` - ML models
- `./config:/app/config` - Configuration files
- `./.env:/app/.env` - Environment variables

## 🔧 Production Configuration

### Security Considerations

1. **Use HTTPS**
   ```bash
   # Add reverse proxy (nginx)
   docker run -d \
     --name nginx-proxy \
     -p 80:80 -p 443:443 \
     -v /var/run/docker.sock:/tmp/docker.sock:ro \
     jwilder/nginx-proxy
   ```

2. **Secure Environment Variables**
   ```bash
   # Use Docker secrets
   echo "your_bot_token" | docker secret create telegram_token -
   ```

3. **Network Security**
   ```bash
   # Create custom network
   docker network create monitor-network
   docker-compose --env-file .env up -d
   ```

### Performance Optimization

1. **Resource Limits**
   ```yaml
   # docker-compose.yml
   services:
     smart-monitor:
       deploy:
         resources:
           limits:
             memory: 1G
             cpus: '0.5'
   ```

2. **Log Rotation**
   ```bash
   # Add to docker-compose.yml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

3. **Health Checks**
   ```yaml
   # Already included in docker-compose.yml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## 📊 Monitoring & Maintenance

### Log Management

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f smart-monitor

# Clean up old logs
docker system prune -f
```

### Backup & Recovery

```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz logs/ models/ config/

# Restore data
tar -xzf backup-20250109.tar.gz
```

### Updates

```bash
# Update application
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 🚨 Troubleshooting

### Common Issues

1. **Port 8501 already in use**
   ```bash
   # Find process using port
   lsof -i :8501
   # Kill process
   kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER logs/ models/ config/
   ```

3. **Docker build fails**
   ```bash
   # Clean Docker cache
   docker system prune -a
   # Rebuild
   docker-compose build --no-cache
   ```

4. **Environment variables not loaded**
   ```bash
   # Check .env file
   cat .env
   # Verify format (no spaces around =)
   ```

### Health Checks

```bash
# Check container status
docker-compose ps

# Check health status
docker inspect smart-system-monitor | grep Health -A 10

# Test dashboard
curl -f http://localhost:8501/_stcore/health
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Check disk usage
docker system df

# Monitor logs
docker-compose logs -f --tail=100
```

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  smart-monitor:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
```

### Load Balancing

```yaml
# Add nginx service
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - smart-monitor
```

## 🔐 Security Best Practices

1. **Use secrets management**
2. **Enable firewall rules**
3. **Regular security updates**
4. **Monitor access logs**
5. **Use HTTPS in production**
6. **Implement rate limiting**
7. **Regular backups**
8. **Access control**

## 📞 Support

For deployment issues:
- Check the troubleshooting section
- Open an issue on GitHub
- Review the documentation
- Check Docker and system logs
