# OpenHands Setup Guide Without Docker

This repository contains detailed instructions for setting up, running, and using OpenHands without Docker on a private server.

## Detailed Instructions for Setting Up OpenHands Without Docker on a Private Server

### 1. System Requirements

- **Operating System**: Linux (Ubuntu ≥ 22.04 recommended) or macOS
- **Hardware**: 
  - Minimum 4GB RAM (8GB+ recommended)
  - 10GB+ free disk space
  - CPU with 2+ cores

### 2. Installing Dependencies

First, install the required dependencies:

```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential git curl

# Install Python 3.12
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

# Install NodeJS 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install tmux (required for local runtime)
sudo apt-get install -y tmux
```

### 3. Cloning and Setting Up the Repository

```bash
# Clone the repository
git clone https://github.com/All-Hands-AI/OpenHands.git
cd OpenHands

# Build the project (installs dependencies)
make build
```

### 4. Configuring OpenHands

#### Setting Up the Configuration File

```bash
# Create a configuration file from the template
cp config.template.toml config.toml

# Run the setup configuration script
make setup-config
```

During the setup, you'll be prompted to:
1. Enter your LLM API key
2. Select a model (Claude 3.5 Sonnet is recommended, but you can use GPT-4o or others)
3. Configure other variables

#### Manual Configuration (Alternative)

You can also manually edit the `config.toml` file:

```bash
# Edit the configuration file
nano config.toml
```

Key settings to modify:

```toml
[core]
# Set your workspace directory
workspace_base = "/path/to/your/workspace"
# Use local runtime instead of Docker
runtime = "local"

[llm]
# Your LLM API key
api_key = "your-api-key-here"
# Model to use
model = "anthropic/claude-3-5-sonnet-20241022"
# Or for OpenAI
# model = "gpt-4o"
```

### 5. Running OpenHands Without Docker

#### Option 1: Run the Full Application

```bash
# Start both backend and frontend
make run
```

#### Option 2: Start Backend and Frontend Separately

```bash
# Start the backend server
make start-backend

# In another terminal, start the frontend
make start-frontend
```

The application will be available at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:3000

### 6. Using the Local Runtime

To explicitly use the local runtime (without Docker), ensure your `config.toml` has:

```toml
[core]
runtime = "local"
```

The local runtime runs directly on your machine without containerization, which means:
- It has direct access to your system
- It runs with your user permissions
- It can access all your local files and resources

### 7. Debugging and Troubleshooting

#### Enable Debug Mode

```bash
# Enable debug mode to see detailed logs
export DEBUG=1
make start-backend
```

Debug logs will be saved in `logs/llm/CURRENT_DATE/` directory.

#### Common Issues and Solutions

1. **Missing Dependencies**:
   ```bash
   # Check if all dependencies are installed
   make check-dependencies
   ```

2. **Port Conflicts**:
   ```bash
   # Check if ports 3000 and 3001 are already in use
   lsof -i :3000
   lsof -i :3001
   ```

3. **LLM API Issues**:
   - Verify your API key is correct
   - Check your internet connection
   - Ensure you have sufficient credits with your LLM provider

4. **Browser Integration Issues**:
   ```bash
   # Install Playwright browsers
   npx playwright install
   ```

### 8. Advanced Configuration

#### Customizing the Agent

You can customize the agent behavior in the `config.toml` file:

```toml
[agent]
# Enable or disable browsing capability
enable_browsing = true

# Enable or disable Jupyter/IPython
enable_jupyter = true

# Enable history truncation for long conversations
enable_history_truncation = true
```

#### Memory Management

Configure how conversation history is managed:

```toml
[condenser]
# Options: "noop", "observation_masking", "recent", "llm", "amortized", "llm_attention"
type = "llm"
llm_config = "condenser"
keep_first = 1
max_size = 100
```

### 9. Evaluation and Benchmarking

OpenHands includes an evaluation framework for benchmarking agent performance:

```bash
# Run the evaluation framework
cd evaluation
poetry run python -m evaluation.run_benchmark --benchmark your_benchmark_name
```

### 10. Security Considerations

When running without Docker, be aware that:
- The agent has the same system access as your user account
- It can read, write, and execute files in accessible directories
- Consider running in a dedicated user account with limited permissions

### 11. Updating OpenHands

To update to the latest version:

```bash
git pull
make build
```

### 12. Additional Resources

- Documentation: https://docs.all-hands.dev
- GitHub Repository: https://github.com/All-Hands-AI/OpenHands
- Community: Join the Slack workspace or Discord server mentioned in the README