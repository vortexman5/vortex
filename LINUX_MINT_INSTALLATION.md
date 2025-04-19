# Vortex (OpenHands AI Framework) Installation Guide for Linux Mint 22.1 Cinnamon

This guide provides detailed instructions for installing, configuring, and deploying the Vortex/OpenHands AI framework on Linux Mint 22.1 Cinnamon. Follow these steps to get the framework running on your laptop.

## System Requirements

### Minimum Hardware Requirements
- **CPU**: 4+ cores (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 20GB free space (SSD recommended)
- **Network**: Stable internet connection

### Recommended Hardware
- **CPU**: 8+ cores (Intel i7/AMD Ryzen 7 or better)
- **RAM**: 16GB+ (32GB for optimal performance)
- **Storage**: 50GB+ free space on SSD
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional, for local model inference)

## 1. Prepare Your System

First, ensure your Linux Mint system is up-to-date:

```bash
# Update package lists and upgrade installed packages
sudo apt update
sudo apt upgrade -y
```

## 2. Install Prerequisites

### 2.1 Install Development Tools

```bash
# Install essential build tools and libraries
sudo apt install -y build-essential curl git python3-pip python3-dev python3-venv
```

### 2.2 Install Docker

Docker is required for containerized deployment:

```bash
# Remove any old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository (using Ubuntu Jammy repository for Linux Mint 22.1)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package lists
sudo apt update

# Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to the docker group to run Docker without sudo
sudo usermod -aG docker $USER

# Apply the new group membership (alternatively, you can log out and back in)
newgrp docker
```

### 2.3 Install Docker Compose

```bash
# Install Docker Compose
sudo apt install -y docker-compose-plugin

# Verify installation
docker compose version
```

### 2.4 Install Node.js

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

### 2.5 Install Python Poetry

Poetry is used for Python dependency management:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to your PATH (add this to your ~/.bashrc or ~/.zshrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
poetry --version
```

## 3. Clone the Repository

```bash
# Create a directory for your projects (optional)
mkdir -p ~/projects
cd ~/projects

# Clone the repository
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex
```

## 4. Install Python Dependencies

```bash
# Install Python dependencies using Poetry
poetry install

# Alternatively, if you prefer to use a virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## 5. Configure the Framework

### 5.1 Create Configuration File

```bash
# Create a configuration file from the template
cp config.template.toml config.toml

# Open the configuration file in your preferred editor
nano config.toml
```

### 5.2 Configure LLM Provider

Edit the `config.toml` file to set up your preferred LLM provider. Here's an example configuration for OpenAI:

```toml
[llm]
provider = "openai"
model = "gpt-4o"
api_key = "your_openai_api_key_here"
```

For Anthropic Claude:

```toml
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key = "your_anthropic_api_key_here"
```

For Google Gemini:

```toml
[llm]
provider = "google"
model = "gemini-2.5-pro"
api_key = "your_google_api_key_here"
```

### 5.3 Configure Storage

For local storage (default):

```toml
[storage]
type = "local"
path = "./data"
```

### 5.4 Configure Server Settings

```toml
[server]
host = "0.0.0.0"  # Listen on all interfaces
port = 8000
debug = false
log_level = "info"
```

## 6. Deployment Options

### 6.1 Docker Deployment (Recommended)

This is the easiest way to deploy the framework:

```bash
# Build and start the containers
docker compose up -d

# Check container status
docker compose ps

# View logs
docker compose logs -f
```

### 6.2 Manual Deployment

If you prefer not to use Docker:

```bash
# Activate the Poetry environment
poetry shell

# Start the server
poetry run openhands server --config config.toml

# Alternatively, if you're using a virtual environment:
source venv/bin/activate
openhands server --config config.toml
```

## 7. Access the Framework

### 7.1 Web Interface

Once the server is running, you can access the web interface:

1. Open your web browser
2. Navigate to `http://localhost:8000`
3. You should see the OpenHands web interface

### 7.2 API Access

For programmatic access:

```bash
# Example API request using curl
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{"message": "Hello, OpenHands!"}' \
  http://localhost:8000/api/v1/message
```

## 8. Testing the Installation

### 8.1 Basic Test

```bash
# Test the server health
curl http://localhost:8000/health

# Expected response: {"status":"ok"}
```

### 8.2 Test LLM Integration

Create a test script to verify LLM integration:

```bash
# Create a test script
cat > test_llm.py << 'EOF'
import requests
import json

url = "http://localhost:8000/api/v1/message"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_auth_token"  # Replace with your actual token if auth is enabled
}
data = {
    "message": "What is the capital of France?"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.json())
EOF

# Run the test
python3 test_llm.py
```

## 9. Common Issues and Troubleshooting

### 9.1 Docker Permission Issues

If you encounter permission issues with Docker:

```bash
# Ensure your user is in the docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

### 9.2 Port Conflicts

If port 8000 is already in use:

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Modify the port in config.toml
# [server]
# port = 8001  # Change to an available port
```

### 9.3 API Key Issues

If you encounter authentication errors with the LLM provider:

1. Verify your API key is correct
2. Check if you have sufficient credits/quota
3. Ensure your API key has the necessary permissions

### 9.4 Memory Issues

If the application crashes due to memory limitations:

```bash
# Check available memory
free -h

# Adjust Docker memory limits in docker-compose.yml
# services:
#   openhands:
#     deploy:
#       resources:
#         limits:
#           memory: 4G  # Adjust based on your system
```

## 10. Updating the Framework

To update to the latest version:

```bash
# Navigate to your repository directory
cd ~/projects/vortex

# Pull the latest changes
git pull

# If using Docker:
docker compose down
docker compose up -d --build

# If using manual deployment:
poetry install
```

## 11. Development Setup (Optional)

If you want to contribute to the project:

```bash
# Install development dependencies
poetry install --with dev

# Set up pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest
```

## 12. Linux Mint-Specific Considerations

### 12.1 System Monitoring

Linux Mint comes with System Monitor, but for better monitoring:

```bash
# Install htop for better process monitoring
sudo apt install htop

# Monitor system resources
htop
```

### 12.2 Firewall Configuration

If you have the firewall enabled:

```bash
# Allow the port used by OpenHands
sudo ufw allow 8000/tcp

# Verify the rule was added
sudo ufw status
```

### 12.3 Desktop Integration

Create a desktop shortcut for easy access:

```bash
# Create a .desktop file
cat > ~/.local/share/applications/openhands.desktop << 'EOF'
[Desktop Entry]
Name=OpenHands AI
Comment=OpenHands AI Framework
Exec=xdg-open http://localhost:8000
Icon=applications-science
Terminal=false
Type=Application
Categories=Development;AI;
EOF

# Make it executable
chmod +x ~/.local/share/applications/openhands.desktop
```

## 13. Performance Optimization

### 13.1 Swap Space

If your laptop has limited RAM, consider increasing swap space:

```bash
# Check current swap
free -h

# Create a swap file (adjust size as needed)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 13.2 CPU Governor

For better performance:

```bash
# Install cpufrequtils
sudo apt install cpufrequtils

# Set CPU governor to performance when plugged in
sudo cpufreq-set -g performance

# Set CPU governor to powersave when on battery (for better battery life)
sudo cpufreq-set -g powersave
```

## 14. Backup and Restore

### 14.1 Backup Configuration

```bash
# Backup your configuration
cp config.toml config.toml.backup

# Backup data directory
tar -czvf openhands-data-backup.tar.gz ./data
```

### 14.2 Restore from Backup

```bash
# Restore configuration
cp config.toml.backup config.toml

# Restore data directory
tar -xzvf openhands-data-backup.tar.gz
```

## Conclusion

You have successfully installed and configured the Vortex/OpenHands AI framework on your Linux Mint 22.1 Cinnamon laptop. If you encounter any issues not covered in this guide, please refer to the project documentation or open an issue in the repository.

For more information on using the framework, refer to the README.md and other documentation in the repository.
