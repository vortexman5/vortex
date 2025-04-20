# Comprehensive Vortex Deployment Guide

This guide provides detailed instructions for deploying Vortex in various configurations, from standalone agents with full capabilities to multi-user server deployments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Options](#deployment-options)
   - [Standalone Agent Deployment](#standalone-agent-deployment)
   - [Remote Server Deployment](#remote-server-deployment)
   - [Multi-User Server Deployment](#multi-user-server-deployment)
   - [Kubernetes Deployment](#kubernetes-deployment)
3. [Database Configuration](#database-configuration)
4. [LLM Backend Options](#llm-backend-options)
5. [Security Considerations](#security-considerations)
6. [Scaling and Performance](#scaling-and-performance)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

#### Minimum Requirements (Standalone Agent)
- **CPU**: 4+ cores
- **RAM**: 16GB minimum
- **Storage**: 50GB SSD
- **Network**: Stable internet connection with at least 10Mbps upload/download

#### Recommended for Standalone Agent
- **CPU**: 8+ cores, preferably with AVX2 support
- **RAM**: 32GB+
- **Storage**: 100GB+ SSD/NVMe
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for local LLM hosting)
- **Network**: 50Mbps+ connection with low latency

#### Recommended for Multi-User Server
- **CPU**: 16+ cores, preferably with AVX2 support
- **RAM**: 64GB+
- **Storage**: 500GB+ SSD/NVMe
- **GPU**: NVIDIA GPU with 16GB+ VRAM (for local model inference)
- **Network**: 100Mbps+ connection with low latency

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS (recommended), other Linux distributions, macOS, or Windows with WSL2
- **Python**: version 3.12.x
- **Docker**: version 20.10.x or newer
- **Docker Compose**: version 2.x or newer
- **Git**: version 2.30.x or newer
- **Nginx**: version 1.18.x or newer (for production deployment)
- **PostgreSQL**: version 14.x or newer (for knowledge storage)

## Deployment Options

### Standalone Agent Deployment

This setup provides a fully autonomous Vortex agent with unrestricted capabilities, running locally on your machine.

#### Step 1: Clone the Vortex Repository

```bash
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex
```

#### Step 2: Set Up the Environment

Vortex uses Poetry for dependency management. Install Poetry and the project dependencies:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies using Poetry
poetry install

# Activate the Poetry virtual environment (for Poetry 2.0.0+)
# Option 1: Use the env activate command (recommended)
poetry env use python
source $(poetry env info --path)/bin/activate

# Option 2: Install the shell plugin and use the shell command
# poetry self add poetry-plugin-shell
# poetry shell
```

Alternatively, if you prefer using pip, you can generate a requirements.txt file from Poetry:

```bash
# Generate requirements.txt from Poetry dependencies
poetry export -f requirements.txt --output requirements.txt

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure the Database

Vortex requires a PostgreSQL database for knowledge storage and agent memory:

```bash
# Install PostgreSQL if not already installed
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install pgvector extension (required for vector embeddings)
# For Ubuntu/Debian:
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
sudo wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update

# Get PostgreSQL version
PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)

# Install pgvector for your PostgreSQL version
sudo apt-get install -y postgresql-${PG_VERSION}-pgvector

# Restart PostgreSQL to load the new extension
sudo systemctl restart postgresql

# For macOS with Homebrew:
# brew install pgvector
# brew services restart postgresql

# Create a database and user for Vortex
sudo -u postgres psql -c "CREATE USER vortex WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE vortex_db OWNER vortex;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vortex_db TO vortex;"

# Enable extensions
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"

# If you encounter issues with the vector extension, you may need to build it from source:
# git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
# cd pgvector
# make
# sudo make install
```

Create a `.env` file in the project root with the following content:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vortex_db
DB_USER=vortex
DB_PASSWORD=your_secure_password
```

#### Step 4: Set Up the LLM Backend

##### Option 1: Use a Local LLM (Recommended for Full Autonomy)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a powerful model (adjust based on your GPU capabilities)
ollama pull mistral:latest
ollama pull llama3:70b
```

Update the `.env` file to include:

```
LLM_PROVIDER=ollama
LLM_MODEL=llama3:70b
LLM_HOST=http://localhost:11434
```

##### Option 2: Use an API-based LLM

If you prefer to use an API-based LLM like OpenAI, update the `.env` file:

```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=your_api_key
```

#### Step 5: Configure Agent Capabilities

To set up Vortex with full capabilities and no restrictions, create a `config.yaml` file in the project root:

```yaml
agent:
  name: Vortex
  description: "Autonomous AI agent with full capabilities"
  version: "1.0.0"
  
  # Set to true to enable full autonomy
  autonomous_mode: true
  
  # Remove restrictions on capabilities
  restrictions:
    enabled: false
    
  # Enable all capabilities
  capabilities:
    file_system:
      enabled: true
      unrestricted: true
    network:
      enabled: true
      unrestricted: true
    process_execution:
      enabled: true
      unrestricted: true
    system_access:
      enabled: true
      unrestricted: true
      
  # Memory configuration
  memory:
    long_term_enabled: true
    short_term_capacity: 100
    
  # Microagents configuration
  microagents:
    enabled: true
    auto_creation: true
    
  # Learning configuration
  learning:
    enabled: true
    reinforcement_learning: true
    knowledge_acquisition: true
```

#### Step 6: Set Up Knowledge Ingestion

To enable Vortex to ingest knowledge from various sources:

1. Create a knowledge directory:

```bash
mkdir -p knowledge/books
mkdir -p knowledge/documentation
mkdir -p knowledge/websites
```

2. Add the knowledge ingestion script:

```bash
cp scripts/ingest_knowledge.py .
```

3. Run the knowledge ingestion process:

```bash
# For PDF books
python ingest_knowledge.py --source knowledge/books --type pdf

# For documentation
python ingest_knowledge.py --source knowledge/documentation --type markdown

# For websites
python ingest_knowledge.py --source knowledge/websites --type url
```

#### Step 7: Start the Vortex Agent

```bash
# Start the agent in autonomous mode
python run_agent.py --autonomous
```

#### Step 8: Interact with the Agent

You can interact with the agent through various interfaces:

1. **CLI Interface**:
   ```bash
   python cli.py
   ```

2. **Web Interface**:
   ```bash
   python web_interface.py
   ```
   Then open your browser to http://localhost:8000

3. **API Interface**:
   ```bash
   python api_server.py
   ```
   The API will be available at http://localhost:5000

### Remote Server Deployment

This setup allows you to deploy Vortex on a remote server with a web GUI interface that you can access from anywhere.

#### Step 1: Prepare Your Remote Server

First, you'll need a Linux server with sufficient resources. I recommend:
- Ubuntu 22.04 LTS or Linux Mint 22.1
- At least 4 CPU cores
- 16GB+ RAM
- 50GB+ SSD storage
- Open ports for HTTP/HTTPS (80/443)

SSH into your server and install the prerequisites:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential dependencies
sudo apt install -y build-essential curl git python3-pip python3-dev python3-venv nginx certbot python3-certbot-nginx

# Install Docker
sudo apt remove docker docker-engine docker.io containerd runc
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 2: Clone and Configure Vortex

```bash
# Create directory and clone repository
mkdir -p ~/vortex
cd ~/vortex
git clone https://codeberg.org/Adamcatholic/vortex.git .

# Install Python dependencies
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
poetry install
```

#### Step 3: Create an Unrestricted Configuration

Create a configuration file with admin mode and all features enabled:

```bash
# Create config file
cp config.template.toml config.toml
```

Edit the config.toml file:

```bash
nano config.toml
```

Add these settings for full capabilities:

```toml
[core]
# Base path for the workspace
workspace_base = "/home/your_username/vortex/workspace"
# Maximum iterations
max_iterations = 500
# JWT secret for authentication (generate a random string)
jwt_secret = "your-random-secure-string-here"

[llm]
# Set your preferred LLM provider
provider = "openai"  # or "anthropic", "google", etc.
model = "gpt-4o"     # or "claude-3-5-sonnet-20241022", "gemini-2.5-pro", etc.
api_key = "your_api_key_here"

[server]
# Server settings for web access
host = "0.0.0.0"  # Listen on all interfaces
port = 8000
debug = false
log_level = "info"

[security]
# Enable admin mode for unrestricted capabilities
admin_mode = true
# Disable confirmation mode to avoid prompts
confirmation_mode = false
# Disable security analyzer
enable_security_analyzer = false

[agent]
# Enable all capabilities
enable_browsing = true
enable_jupyter = true
enable_llm_editor = true
enable_prompt_extensions = true
enable_history_truncation = true

[sandbox]
# Increase timeout for longer operations
timeout = 300
# Use host network for unrestricted network access
use_host_network = true
# Enable GPU support if available
enable_gpu = true
# Keep runtime alive after session ends
keep_runtime_alive = true
# Additional Docker runtime kwargs for more capabilities
docker_runtime_kwargs = {"privileged": true}
```

#### Step 4: Create a Docker Compose File

Create a docker-compose.yml file for easy deployment:

```bash
nano docker-compose.yml
```

Add the following content:

```yaml
version: '3.8'

services:
  vortex:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: vortex-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./config.toml:/app/config.toml
      - ./workspace:/app/workspace
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_MODEL=${LLM_MODEL}
      - SECURITY_ADMIN_MODE=true
      - SANDBOX_USE_HOST_NETWORK=true
      - SANDBOX_TIMEOUT=300
    privileged: true
    networks:
      - vortex-network

  nginx:
    image: nginx:latest
    container_name: vortex-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/www:/var/www/html
    depends_on:
      - vortex
    networks:
      - vortex-network

networks:
  vortex-network:
    driver: bridge
```

#### Step 5: Create a Dockerfile

```bash
nano Dockerfile
```

Add the following content:

```dockerfile
FROM nikolaik/python-nodejs:python3.12-nodejs22

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Create necessary directories
RUN mkdir -p workspace data

# Expose port
EXPOSE 8000

# Start the server
CMD ["poetry", "run", "python", "-m", "openhands.server.main"]
```

#### Step 6: Set Up Nginx as a Reverse Proxy

Create the Nginx configuration directory:

```bash
mkdir -p nginx/conf.d nginx/ssl nginx/www
```

Create the Nginx configuration file:

```bash
nano nginx/conf.d/vortex.conf
```

Add the following content (replace yourdomain.com with your actual domain):

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://vortex:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Step 7: Set Up SSL with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com
```

#### Step 8: Create Environment Variables File

```bash
nano .env
```

Add your API keys:

```
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o
```

#### Step 9: Start the Services

```bash
docker compose up -d
```

#### Step 10: Access Your Vortex Instance

Now you can access your fully-featured Vortex instance at:

```
https://yourdomain.com
```

### Multi-User Server Deployment

This setup is designed for organizations that need to provide Vortex access to multiple users.

#### Step 1: Clone the Repository

```bash
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex
```

#### Step 2: Set Up Python Environment

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment (for Poetry 2.0.0+)
# Option 1: Use the env activate command (recommended)
poetry env use python
source $(poetry env info --path)/bin/activate

# Option 2: Install the shell plugin and use the shell command
# poetry self add poetry-plugin-shell
# poetry shell
```

#### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

#### Step 4: Build the Frontend

```bash
npm run build
```

#### Step 5: Create a Server Configuration File

```bash
cp config.template.toml config.server.toml
```

#### Step 6: Configure Server Settings

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

#### Step 7: Configure LLM and Runtime Settings

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

#### Step 8: Configure Storage Settings

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

#### Step 9: Deploy with Docker Compose

1. Configure environment variables:

```bash
# Create .env file
cat > .env << EOL
VORTEX_CONFIG_PATH=/app/config.server.toml
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
EOL
```

2. Start the services:

```bash
docker-compose up -d
```

#### Step 10: Configure Nginx as a reverse proxy

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

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/vortex /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Kubernetes Deployment

For large-scale deployments, Kubernetes is recommended:

#### Step 1: Create Kubernetes Manifests

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

#### Step 2: Apply the Manifests

```bash
kubectl apply -f kubernetes/
```

## Database Configuration

Vortex uses PostgreSQL for knowledge storage, vector embeddings, and agent memory.

### Basic PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install pgvector extension (required for vector embeddings)
# For Ubuntu/Debian:
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
sudo wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update

# Get PostgreSQL version
PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)

# Install pgvector for your PostgreSQL version
sudo apt-get install -y postgresql-${PG_VERSION}-pgvector

# Restart PostgreSQL to load the new extension
sudo systemctl restart postgresql

# For macOS with Homebrew:
# brew install pgvector
# brew services restart postgresql

# Create a database and user
sudo -u postgres psql -c "CREATE USER vortex WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE vortex_db OWNER vortex;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vortex_db TO vortex;"

# Enable required extensions
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"

# If you encounter issues with the vector extension, you may need to build it from source:
# git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
# cd pgvector
# make
# sudo make install
```

### Database Schema

The Vortex database includes the following key tables:

1. **knowledge_items**: Stores knowledge fragments with vector embeddings
2. **memory_items**: Stores agent memory entries
3. **trajectories**: Stores interaction trajectories for learning
4. **users**: Stores user information (for multi-user deployments)
5. **sessions**: Stores active sessions

### Vector Database Configuration

For efficient semantic search, Vortex uses the PostgreSQL vector extension:

```sql
-- Create a table for vector embeddings
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB
);

-- Create an index for similarity search
CREATE INDEX embedding_idx ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### Database Scaling

For larger deployments, consider:

1. **Connection Pooling**: Use PgBouncer to manage database connections
2. **Replication**: Set up read replicas for query-heavy workloads
3. **Partitioning**: Partition large tables by date or user

## LLM Backend Options

Vortex supports multiple LLM backends, each with different trade-offs.

### Option 1: API-based LLMs

#### OpenAI

```toml
[llm]
provider = "openai"
model = "gpt-4o"
api_key = "your_openai_api_key"
```

#### Anthropic

```toml
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key = "your_anthropic_api_key"
```

#### Google

```toml
[llm]
provider = "google"
model = "gemini-2.5-pro"
api_key = "your_google_api_key"
```

### Option 2: Self-hosted LLMs

#### Ollama

```toml
[llm]
provider = "ollama"
model = "llama3:70b"
host = "http://localhost:11434"
```

#### LM Studio

```toml
[llm]
provider = "lmstudio"
model = "local-model"
host = "http://localhost:1234/v1"
```

#### vLLM

```toml
[llm]
provider = "vllm"
model = "/path/to/model"
host = "http://localhost:8000"
```

### LLM Fallback Configuration

For improved reliability, configure fallback models:

```toml
[llm]
provider = "openai"
model = "gpt-4o"
api_key = "your_openai_api_key"

[llm.fallback]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key = "your_anthropic_api_key"
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

### Additional Security Measures for Unrestricted Deployments

Since unrestricted deployments have significant security implications:

1. **IP Restrictions**: Limit access to your specific IP address in Nginx:

```nginx
location / {
    # Allow only your IP
    allow 123.123.123.123;
    # Deny all other IPs
    deny all;
    
    proxy_pass http://vortex:8000;
    # ... other proxy settings
}
```

2. **Basic Authentication**: Add username/password protection:

```bash
# Install apache2-utils for htpasswd
sudo apt install -y apache2-utils

# Create password file
sudo htpasswd -c nginx/conf.d/.htpasswd yourusername
```

Update your Nginx config:

```nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/conf.d/.htpasswd;
    
    proxy_pass http://vortex:8000;
    # ... other proxy settings
}
```

3. **Firewall Configuration**:

```bash
# Allow only SSH and HTTPS
sudo ufw allow ssh
sudo ufw allow https
sudo ufw enable
```

4. **Run in a dedicated user account** with appropriate permissions
5. **Consider using a virtual machine or container** for isolation
6. **Monitor the agent's activities** closely
7. **Implement a kill switch mechanism** for emergency shutdown

## Scaling and Performance

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

### Performance Optimization

1. **Caching**: Implement caching for common requests
2. **Database Indexing**: Ensure proper indexes on frequently queried fields
3. **Connection Pooling**: Use connection pooling for database connections
4. **Asynchronous Processing**: Use background workers for long-running tasks

## Monitoring and Maintenance

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

### Backup and Recovery

1. **Database Backups**:

```bash
# Create a backup script
cat > /usr/local/bin/backup-vortex.sh << 'EOL'
#!/bin/bash
BACKUP_DIR="/backups/vortex"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
pg_dump -U vortex vortex_db | gzip > $BACKUP_DIR/vortex_db_$TIMESTAMP.sql.gz

# Backup configuration
cp /path/to/vortex/config.toml $BACKUP_DIR/config_$TIMESTAMP.toml

# Backup knowledge directories
tar -czf $BACKUP_DIR/knowledge_$TIMESTAMP.tar.gz /path/to/vortex/knowledge

# Rotate backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql.gz" -type f -mtime +7 -delete
find $BACKUP_DIR -name "*.toml" -type f -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +7 -delete
EOL

chmod +x /usr/local/bin/backup-vortex.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-vortex.sh") | crontab -
```

2. **Restore Procedure**:

```bash
# Restore database
gunzip -c /backups/vortex/vortex_db_20250419_020000.sql.gz | psql -U vortex vortex_db

# Restore configuration
cp /backups/vortex/config_20250419_020000.toml /path/to/vortex/config.toml

# Restore knowledge directories
tar -xzf /backups/vortex/knowledge_20250419_020000.tar.gz -C /
```

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