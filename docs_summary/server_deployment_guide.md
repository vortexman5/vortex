# Vortex Server Deployment Guide

This guide provides detailed instructions on how to set up and deploy Vortex (OpenHands AI Framework) as a server for multi-user access.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Server Configuration](#server-configuration)
4. [Deployment Options](#deployment-options)
5. [Security Considerations](#security-considerations)
6. [Scaling](#scaling)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

#### Minimum Production Requirements
- **CPU**: 8+ cores
- **RAM**: 32GB minimum
- **Storage**: 100GB SSD
- **Network**: Stable internet connection with at least 50Mbps upload/download

#### Recommended Production Setup
- **CPU**: 16+ cores, preferably with AVX2 support
- **RAM**: 64GB+
- **Storage**: 500GB+ SSD/NVMe
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for local model inference)
- **Network**: 100Mbps+ connection with low latency

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS (recommended)
- **Docker**: version 20.10.x or newer
- **Docker Compose**: version 2.x or newer
- **Python**: version 3.12.x
- **Node.js**: version 20.x or newer (for frontend)
- **Nginx**: version 1.18.x or newer (for production deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex
```

### 2. Set Up Python Environment

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Build the Frontend

```bash
npm run build
```

## Server Configuration

### 1. Create a Server Configuration File

```bash
cp config.template.toml config.server.toml
```

### 2. Configure Server Settings

Edit `config.server.toml` to include server-specific settings:

```toml
[server]
# Host to bind the server to
host = "0.0.0.0"

# Port to run the server on
port = 8000

# Enable CORS for cross-origin requests
enable_cors = true

# Set allowed origins for CORS
cors_origins = ["*"]

# Enable WebSocket support
enable_websocket = true

# Set session timeout (in seconds)
session_timeout = 3600

# Set maximum concurrent sessions
max_concurrent_sessions = 10

# Enable authentication
enable_auth = true

# Authentication type: "basic", "jwt", or "none"
auth_type = "jwt"

# JWT secret key (if using JWT authentication)
jwt_secret = "your_secure_jwt_secret_here"

# Enable rate limiting
enable_rate_limit = true

# Rate limit (requests per minute)
rate_limit = 60
```

### 3. Configure LLM and Runtime Settings

```toml
[llm]
# Choose your preferred model
model = "claude-3-5-sonnet-20241022"
api_key = "your_api_key_here"

[sandbox]
# Choose runtime type: "docker" recommended for server deployment
runtime = "docker"

# Set timeout for commands (in seconds)
timeout = 60

# Enable security features
enable_security = true

# Set resource limits for Docker containers
memory_limit = "4g"
cpu_limit = 2.0
```

### 4. Configure Storage Settings

```toml
[storage]
# Storage type: "local", "s3", or "google_cloud"
type = "local"

# Local storage path
local_path = "/data/vortex"

# S3 configuration (if using S3 storage)
[storage.s3]
bucket = "vortex-data"
region = "us-west-2"
access_key = "your_access_key"
secret_key = "your_secret_key"

# Google Cloud Storage configuration (if using GCS)
[storage.google_cloud]
bucket = "vortex-data"
project_id = "your-project-id"
```

## Deployment Options

### Option 1: Docker Compose (Recommended for Production)

1. Create a Docker Compose file:

```bash
# docker-compose.yml is already provided in the repository
```

2. Configure environment variables:

```bash
# Create .env file
cat > .env << EOL
VORTEX_CONFIG_PATH=/app/config.server.toml
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
EOL
```

3. Start the services:

```bash
docker-compose up -d
```

### Option 2: Manual Deployment

1. Start the server:

```bash
# Using Poetry
poetry run python -m openhands.server --config config.server.toml

# Or if you're already in the Poetry shell
python -m openhands.server --config config.server.toml
```

2. Configure Nginx as a reverse proxy (recommended for production):

```nginx
# /etc/nginx/sites-available/vortex
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/vortex /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Kubernetes Deployment

For large-scale deployments, Kubernetes is recommended. A basic Kubernetes deployment would include:

1. Create Kubernetes manifests:

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vortex
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vortex
  template:
    metadata:
      labels:
        app: vortex
    spec:
      containers:
      - name: vortex
        image: vortex:latest
        ports:
        - containerPort: 8000
        env:
        - name: VORTEX_CONFIG_PATH
          value: /app/config.server.toml
        volumeMounts:
        - name: config-volume
          mountPath: /app/config.server.toml
          subPath: config.server.toml
      volumes:
      - name: config-volume
        configMap:
          name: vortex-config

---
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vortex
spec:
  selector:
    app: vortex
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vortex
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: vortex.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vortex
            port:
              number: 80
```

2. Apply the manifests:

```bash
kubectl apply -f kubernetes/
```

## Security Considerations

### API Key Management

For production deployments, never hardcode API keys in configuration files. Instead:

1. Use environment variables:

```toml
[llm]
model = "claude-3-5-sonnet-20241022"
api_key = "${ANTHROPIC_API_KEY}"
```

2. Use a secrets management solution:
   - Kubernetes Secrets
   - HashiCorp Vault
   - AWS Secrets Manager
   - Google Secret Manager

### Authentication

1. Enable JWT authentication for production:

```toml
[server]
enable_auth = true
auth_type = "jwt"
jwt_secret = "${JWT_SECRET}"
```

2. Implement a proper user management system:
   - Store user credentials securely (bcrypt)
   - Implement password policies
   - Add two-factor authentication for admin access

### Network Security

1. Always use HTTPS in production:
   - Set up SSL certificates (Let's Encrypt)
   - Configure Nginx to redirect HTTP to HTTPS

2. Implement proper firewall rules:
   - Restrict access to the server port
   - Use security groups or iptables

3. Consider using a Web Application Firewall (WAF)

### Sandbox Security

1. Configure resource limits:

```toml
[sandbox]
memory_limit = "4g"
cpu_limit = 2.0
disk_limit = "10g"
```

2. Enable security analyzers:

```toml
[security]
security_analyzer = "invariant"
confirmation_mode = true
```

## Scaling

### Horizontal Scaling

For handling more concurrent users:

1. Deploy multiple instances behind a load balancer
2. Use Redis for session storage:

```toml
[server.session]
type = "redis"
redis_url = "redis://redis:6379/0"
```

3. Use a shared storage backend:

```toml
[storage]
type = "s3"
```

### Vertical Scaling

For handling more complex tasks:

1. Increase resource limits for containers
2. Use more powerful hardware
3. Configure larger context windows for LLMs

## Monitoring

### Health Checks

The server provides health check endpoints:

- `/health`: Basic health check
- `/health/detailed`: Detailed health status

### Metrics

1. Enable Prometheus metrics:

```toml
[server.monitoring]
enable_metrics = true
metrics_path = "/metrics"
```

2. Set up Grafana dashboards for visualization

### Logging

1. Configure logging levels:

```toml
[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR
file = "/var/log/vortex/server.log"
max_size = 100  # MB
backup_count = 5
```

2. Set up log aggregation:
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Graylog
   - Datadog

## Troubleshooting

### Common Issues

#### Server Won't Start

```
Error: Address already in use
```

Solution: Check if another process is using the configured port:

```bash
sudo lsof -i :8000
```

#### High Memory Usage

If the server is consuming too much memory:

1. Reduce the number of concurrent sessions:

```toml
[server]
max_concurrent_sessions = 5
```

2. Implement session cleanup:

```toml
[server]
session_cleanup_interval = 300  # seconds
```

#### Slow Response Times

If the server is responding slowly:

1. Check LLM API latency
2. Monitor system resources
3. Consider using a more powerful instance
4. Implement caching for common requests

#### Connection Timeouts

If clients are experiencing timeouts:

1. Increase timeout settings:

```toml
[server]
request_timeout = 120  # seconds
```

2. Check network connectivity
3. Ensure the LLM provider is responsive

### Debugging

For detailed debugging:

```bash
# Enable debug logging
export OPENHANDS_LOG_LEVEL=DEBUG
python -m openhands.server --config config.server.toml

# Save logs to a file
python -m openhands.server --config config.server.toml 2> debug.log
```

---

## Additional Resources

- [Vortex GitHub Repository](https://codeberg.org/Adamcatholic/vortex)
- [OpenHands Documentation](https://vortex.readthedocs.io/)
- [API Reference](https://vortex.readthedocs.io/api/)
- [Community Forum](https://community.vortex.ai/)

For more information, please refer to the official documentation or join the community forum.