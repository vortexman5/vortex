# Deploying Vortex as a Standalone Agent with Full Capabilities on a Remote Server

This guide walks you through setting up Vortex on a remote server with a web GUI interface that you can access from anywhere. This setup will have full capabilities and no restrictions.

## Step 1: Prepare Your Remote Server

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

## Step 2: Clone and Configure Vortex

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

## Step 3: Create an Unrestricted Configuration

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

## Step 4: Create a Docker Compose File

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

## Step 5: Create a Dockerfile

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

## Step 6: Set Up Nginx as a Reverse Proxy

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

## Step 7: Set Up SSL with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com
```

## Step 8: Create Environment Variables File

```bash
nano .env
```

Add your API keys:

```
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o
```

## Step 9: Start the Services

```bash
docker compose up -d
```

## Step 10: Access Your Vortex Instance

Now you can access your fully-featured Vortex instance at:

```
https://yourdomain.com
```

## Additional Security Considerations

Since this is a fully unrestricted setup, consider these security measures:

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

## Monitoring and Maintenance

To monitor your Vortex instance:

```bash
# View logs
docker compose logs -f

# Check container status
docker compose ps

# Restart services
docker compose restart
```

This setup gives you a fully-featured Vortex instance with:
- Web GUI accessible from anywhere
- SSL encryption
- Admin mode with unrestricted capabilities
- All features enabled
- Persistent workspace and data
- Docker containerization for easy management

You can now use Vortex as a powerful AI assistant with full capabilities through your browser from anywhere in the world.