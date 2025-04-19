# Vortex CLI Tool Guide

This guide provides detailed instructions on how to set up and run Vortex (OpenHands AI Framework) as a command-line tool.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)

## System Requirements

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 4+ cores
- **RAM**: 16GB minimum
- **Storage**: 50GB SSD
- **Network**: Stable internet connection with at least 10Mbps upload/download

#### Recommended Setup
- **CPU**: 8+ cores, preferably with AVX2 support
- **RAM**: 32GB+
- **Storage**: 100GB+ SSD/NVMe
- **Network**: 50Mbps+ connection with low latency

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS (recommended), other Linux distributions, macOS, or Windows with WSL2
- **Python**: version 3.12.x
- **Docker**: version 20.10.x or newer (optional, for containerized runtime)
- **Git**: version 2.30.x or newer

## Installation

### 1. Clone the Repository

```bash
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex
```

### 2. Set Up Python Environment

#### Using Poetry (Recommended)

Poetry is the recommended way to manage dependencies for Vortex:

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

#### Using pip (Alternative)

If you prefer not to use Poetry:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Install Additional System Dependencies

Some features may require additional system packages:

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential curl git python3-pip python3-dev

# For browser functionality
sudo apt install -y chromium-browser
```

## Configuration

### 1. Create a Configuration File

Start by copying the template configuration:

```bash
cp config.template.toml config.toml
```

### 2. Configure API Keys

Edit the `config.toml` file to add your LLM API keys:

```toml
[llm]
# Choose your preferred model
model = "claude-3-5-sonnet-20241022"  # or "gpt-4o", "gemini-2.5-pro", etc.
api_key = "your_api_key_here"

# For Anthropic (Claude) models
[llm.anthropic]
api_key = "your_anthropic_api_key_here"

# For OpenAI models
[llm.openai]
api_key = "your_openai_api_key_here"

# For Google (Gemini) models
[llm.google]
api_key = "your_google_api_key_here"
```

### 3. Configure Runtime Settings

Adjust runtime settings based on your needs:

```toml
[sandbox]
# Choose runtime type: "local", "docker", or "e2b"
runtime = "local"

# Set timeout for commands (in seconds)
timeout = 60

# Enable or disable security features
enable_security = true
```

### 4. Configure Agent Settings

```toml
[agent]
# Choose the agent type
type = "default"

# Set the maximum number of iterations
max_iterations = 100

# Enable or disable history truncation
enable_history_truncation = true
```

## Basic Usage

### Running a Simple Task

To run Vortex with a simple task:

```bash
# Using Poetry
poetry run python -m openhands.cli -t "Write a hello world program in Python"

# Or if you're already in the Poetry shell
python -m openhands.cli -t "Write a hello world program in Python"
```

### Running with a Task File

For longer tasks, you can use a task file:

```bash
# Create a task file
echo "Create a simple web server in Python that serves a 'Hello, World!' page on port 8080." > task.txt

# Run with the task file
python -m openhands.cli -f task.txt
```

### Using a Specific Configuration

To use a specific configuration file:

```bash
python -m openhands.cli --config my_custom_config.toml -t "Your task here"
```

## Advanced Usage

### Setting Session Name

You can set a custom session name for easier identification:

```bash
python -m openhands.cli --name my_session -t "Your task here"
```

### Enabling Admin Mode

For unrestricted capabilities (use with caution):

```bash
# First create an admin configuration
cp config.template.toml config.admin.toml

# Edit config.admin.toml to enable admin mode
# [security]
# admin_mode = true
# security_analyzer = "invariant"
# confirmation_mode = false

# Run with admin configuration
python -m openhands.cli --config config.admin.toml -t "Your task here"
```

### Working with Repositories

To work with a specific repository:

```bash
python -m openhands.cli --repo username/repository -t "Analyze this repository"
```

### Saving Trajectories

To save the execution history for analysis:

```bash
python -m openhands.cli --save-trajectory output.json -t "Your task here"
```

### Replaying Trajectories

To replay a previously saved trajectory:

```bash
python -m openhands.cli --replay-trajectory saved_trajectory.json
```

### Multiline Input Mode

For tasks that require multiple lines:

```bash
python -m openhands.cli --multiline-input -t "Your initial task"
```

### Disabling Auto-Continue

By default, the agent will auto-continue without asking for user input. To disable this:

```bash
python -m openhands.cli --no-auto-continue -t "Your task here"
```

## Troubleshooting

### Common Issues

#### API Key Issues

If you encounter authentication errors:

```
Error: AuthenticationError: Invalid API key
```

Solution: Check your API key in the configuration file and ensure it's correctly set.

#### Context Window Exceeded

If you see an error about context window:

```
Error: ContextWindowExceededError: This model's maximum context length is X tokens
```

Solution: Enable history truncation in your configuration:

```toml
[agent]
enable_history_truncation = true
```

#### Runtime Connection Issues

If the runtime fails to connect:

```
Error: RuntimeError: Failed to connect to runtime
```

Solutions:
- Check if Docker is running (if using Docker runtime)
- Ensure you have the necessary permissions
- Try using a different runtime type in your configuration

#### Out of Memory Errors

If you encounter memory issues:

```
Error: RuntimeError: Out of memory
```

Solutions:
- Reduce the maximum number of iterations
- Use a smaller model
- Increase your system's swap space

### Logs

To get more detailed logs for troubleshooting:

```bash
# Enable debug logging
export OPENHANDS_LOG_LEVEL=DEBUG
python -m openhands.cli -t "Your task here"

# Save logs to a file
python -m openhands.cli -t "Your task here" 2> debug.log
```

## Examples

### Example 1: Writing a Simple Script

```bash
python -m openhands.cli -t "Write a Python script that fetches the current weather for New York City using a public API"
```

### Example 2: Code Analysis

```bash
python -m openhands.cli -t "Analyze the following Python code and suggest improvements:

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(35))"
```

### Example 3: Working with Files

```bash
# Create a file first
echo "# TODO: Implement a sorting algorithm" > sort.py

# Ask the agent to implement it
python -m openhands.cli -t "Implement a merge sort algorithm in the sort.py file"
```

### Example 4: Multi-step Task

```bash
python -m openhands.cli -t "Create a simple Flask application with the following features:
1. A homepage that displays 'Hello, World!'
2. A '/about' page with some information
3. A '/contact' form that logs submissions to a file
4. Proper error handling for 404 and 500 errors"
```

### Example 5: Using with a Repository

```bash
# Clone a repository first
git clone https://github.com/example/repo.git
cd repo

# Run Vortex on the repository
python -m openhands.cli -t "Analyze this repository and create a summary of its structure and main components"
```

---

## Additional Resources

- [Vortex GitHub Repository](https://codeberg.org/Adamcatholic/vortex)
- [OpenHands Documentation](https://vortex.readthedocs.io/)
- [API Reference](https://vortex.readthedocs.io/api/)
- [Community Forum](https://community.vortex.ai/)

For more information, please refer to the official documentation or join the community forum.