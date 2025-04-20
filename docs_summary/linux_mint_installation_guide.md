# Comprehensive Guide: Running Vortex AI on Linux Mint 22.1 Cinnamon

This guide provides detailed instructions for installing and running Vortex AI with full capabilities on Linux Mint 22.1 Cinnamon. By following these steps, you'll be able to run Vortex AI with its web interface and all features enabled.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
   - [Install System Dependencies](#install-system-dependencies)
   - [Install Python 3.12](#install-python-312)
   - [Install PostgreSQL and pgvector](#install-postgresql-and-pgvector)
   - [Clone the Repository](#clone-the-repository)
   - [Set Up Python Environment](#set-up-python-environment)
3. [Configuration](#configuration)
   - [Configure PostgreSQL Database](#configure-postgresql-database)
   - [Configure LLM Backend](#configure-llm-backend)
   - [Create Configuration File](#create-configuration-file)
4. [Building the Frontend](#building-the-frontend)
5. [Running Vortex AI](#running-vortex-ai)
   - [Start the Web Server](#start-the-web-server)
   - [Access the Web Interface](#access-the-web-interface)
6. [Knowledge Ingestion](#knowledge-ingestion)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

## System Requirements

For optimal performance on Linux Mint 22.1 Cinnamon, ensure your system meets these requirements:

- **CPU**: 4+ cores (8+ cores recommended)
- **RAM**: 16GB minimum (32GB+ recommended)
- **Storage**: 50GB+ SSD space
- **GPU**: Optional but recommended for local LLM hosting (NVIDIA with 8GB+ VRAM)
- **Network**: Stable internet connection

## Installation

### Install System Dependencies

Open a terminal and run the following commands to install essential dependencies:

```bash
# Update package lists
sudo apt update
sudo apt upgrade -y

# Install essential build tools and libraries
sudo apt install -y build-essential curl git wget unzip software-properties-common \
                    apt-transport-https ca-certificates gnupg lsb-release \
                    python3-pip python3-dev python3-venv

# Install Docker (optional, but recommended for full capabilities)
sudo apt remove docker docker-engine docker.io containerd runc
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to the docker group to run Docker without sudo
sudo usermod -aG docker $USER
# Note: You'll need to log out and back in for this change to take effect
```

### Install Python 3.12

Linux Mint 22.1 may not include Python 3.12 by default, so you'll need to install it:

```bash
# Add deadsnakes PPA for Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.12 and development tools
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils

# Install pip for Python 3.12
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
```

### Install PostgreSQL and pgvector

Vortex requires PostgreSQL with the pgvector extension for vector embeddings:

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Add PostgreSQL repository for the latest version
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update

# Get PostgreSQL version
PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)

# Install pgvector extension
sudo apt install -y postgresql-${PG_VERSION}-pgvector

# Restart PostgreSQL to load the extension
sudo systemctl restart postgresql
```

If you encounter issues installing pgvector from the repository, you can build it from source:

```bash
# Install required build dependencies
sudo apt install -y postgresql-server-dev-${PG_VERSION}

# Clone and build pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Clone the Repository

```bash
# Create a directory for Vortex
mkdir -p ~/vortex
cd ~/vortex

# Clone the repository
git clone https://codeberg.org/Adamcatholic/vortex.git .
```

### Set Up Python Environment

Vortex uses Poetry for dependency management:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3.12 -

# Add Poetry to your PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Configure Poetry to use Python 3.12
poetry env use python3.12

# Install dependencies
poetry install

# Activate the virtual environment
source $(poetry env info --path)/bin/activate
```

## Configuration

### Configure PostgreSQL Database

Set up a PostgreSQL database for Vortex:

```bash
# Create a database and user for Vortex
sudo -u postgres psql -c "CREATE USER vortex WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE vortex_db OWNER vortex;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vortex_db TO vortex;"

# Enable required extensions
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

Create a `.env` file in the project root with database connection details:

```bash
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vortex_db
DB_USER=vortex
DB_PASSWORD=your_secure_password
EOF
```

### Configure LLM Backend

You have two options for the LLM backend:

#### Option 1: Use a Local LLM with Ollama (Recommended for Privacy)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (choose based on your system capabilities)
ollama pull mistral:latest
# For more powerful systems with good GPUs:
# ollama pull llama3:70b

# Add LLM configuration to .env
cat >> .env << EOF
LLM_PROVIDER=ollama
LLM_MODEL=mistral:latest
LLM_HOST=http://localhost:11434
EOF
```

#### Option 2: Use an API-based LLM (Better Quality, Requires API Key)

```bash
# Add LLM configuration to .env
cat >> .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=your_api_key_here
EOF
```

### Create Configuration File

Create a `config.toml` file with full capabilities enabled, including reinforcement learning:

```bash
cat > config.toml << EOF
[core]
# Base path for the workspace
workspace_base = "$HOME/vortex/workspace"
# Maximum iterations
max_iterations = 500
# Path to store trajectories
save_trajectory_path = "$HOME/vortex/trajectories"
# Whether to save screenshots in the trajectory
save_screenshots_in_trajectory = true

[llm]
# LLM settings will be loaded from environment variables

[server]
# Server settings for web access
host = "0.0.0.0"
port = 12000
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

[rl]
# Whether to enable reinforcement learning
enabled = true
# Maximum number of turns in a conversation
max_turns = 10
# Strategy to use for rollout
rollout_strategy = "StandardReAct"
# Backend for storing trajectories
storage_backend = "file"
# Path to store trajectories
trajectory_path = "$HOME/vortex/rl_trajectories"
# Whether to enable training
enable_training = true

[learning]
# Whether learning is enabled
enabled = true
# Whether reinforcement learning is enabled
reinforcement_learning = true
# Whether knowledge acquisition is enabled
knowledge_acquisition = true
# Whether to automatically learn from user feedback
learn_from_feedback = true
# Path to store learned knowledge
knowledge_path = "$HOME/vortex/knowledge"
EOF
```

## Building the Frontend

The frontend needs to be built before running the web server:

```bash
# Install Node.js and npm if not already installed
sudo apt install -y nodejs npm

# Navigate to the frontend directory
cd frontend

# Install frontend dependencies
npm install

# Build the frontend
npm run build

# Return to the project root
cd ..
```

If you encounter issues with the Tailwind CSS configuration during the build, you can fix it by editing the `frontend/src/tailwind.css` file:

```bash
# Edit the tailwind.css file to use direct CSS instead of utility classes
cat > frontend/src/tailwind.css << EOF
@tailwind base;
@tailwind components;
@tailwind utilities;

.button-base {
  background-color: #454545;
  border: 1px solid #666;
  border-radius: 0.25rem;
}
EOF

# Rebuild the frontend
cd frontend
npm run build
cd ..
```

## Running Vortex AI

### Start the Web Server

Now you can start the Vortex AI web server:

```bash
# Activate the Poetry environment if not already activated
source $(poetry env info --path)/bin/activate

# Start the web server
python start_web_server.py
```

The server will start on http://0.0.0.0:12000 by default.

### Access the Web Interface

Open your web browser and navigate to:

```
http://localhost:12000
```

You should now see the Vortex AI web interface, where you can interact with the agent.

## Knowledge Ingestion

To make Vortex more powerful, you can ingest knowledge from various sources:

```bash
# Create knowledge directories
mkdir -p knowledge/books
mkdir -p knowledge/documentation
mkdir -p knowledge/websites
mkdir -p knowledge/database

# Ingest PDF books
python ingest_knowledge.py --source knowledge/books --type pdf

# Ingest documentation
python ingest_knowledge.py --source knowledge/documentation --type markdown

# Ingest websites
python ingest_knowledge.py --source knowledge/websites --type url

# Ingest database content
python ingest_knowledge.py --source knowledge/database --type database --config knowledge/database/your_config.json
```

## Troubleshooting

### Common Issues and Solutions

1. **PostgreSQL pgvector Extension Issues**
   
   If you encounter issues with the pgvector extension, try building it from source as described in the installation section.

2. **Frontend Build Failures**
   
   If the frontend build fails with Tailwind CSS errors, use the direct CSS approach described in the "Building the Frontend" section.

3. **Python Version Conflicts**
   
   Ensure you're using Python 3.12 with Poetry:
   ```bash
   poetry env use python3.12
   ```

4. **Docker Permission Issues**
   
   If you encounter permission issues with Docker, ensure your user is in the docker group and you've logged out and back in:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

5. **Web Server Port Conflicts**
   
   If port 12000 is already in use, you can specify a different port:
   ```bash
   python start_web_server.py --port 12001
   ```

## Advanced Configuration

### Running as a System Service

To run Vortex AI as a system service that starts automatically:

```bash
# Create a systemd service file
sudo tee /etc/systemd/system/vortex.service > /dev/null << EOF
[Unit]
Description=Vortex AI Service
After=network.target postgresql.service

[Service]
User=$USER
WorkingDirectory=$HOME/vortex
ExecStart=$HOME/.local/bin/poetry run python start_web_server.py
Restart=on-failure
RestartSec=5
Environment=PATH=$HOME/.local/bin:$PATH

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable vortex
sudo systemctl start vortex

# Check the status
sudo systemctl status vortex
```

### Enabling HTTPS

For secure access, you can set up HTTPS using a reverse proxy like Nginx:

```bash
# Install Nginx
sudo apt install -y nginx

# Create an Nginx configuration file
sudo tee /etc/nginx/sites-available/vortex > /dev/null << EOF
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:12000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/vortex /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install Certbot for HTTPS
sudo apt install -y certbot python3-certbot-nginx

# Obtain an SSL certificate
sudo certbot --nginx -d your_domain.com
```

### GPU Acceleration

If you have an NVIDIA GPU, you can enable GPU acceleration for local LLMs:

```bash
# Install NVIDIA drivers
sudo apt install -y nvidia-driver-535

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo tee /etc/docker/daemon.json > /dev/null << EOF
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF

# Restart Docker
sudo systemctl restart docker

# Update config.toml to enable GPU
sed -i 's/enable_gpu = true/enable_gpu = true/' config.toml
```

---

By following this comprehensive guide, you should now have a fully functional Vortex AI installation on your Linux Mint 22.1 Cinnamon system, with the web interface accessible and all capabilities enabled. If you encounter any issues or have questions, please refer to the troubleshooting section or consult the official documentation.