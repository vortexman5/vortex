# Consolidated Configuration Guide

This guide explains the consolidated configuration system in Vortex AI, which combines all features and options into a single, comprehensive configuration file.

## Table of Contents

1. [Introduction](#introduction)
2. [Using the Consolidated Configuration](#using-the-consolidated-configuration)
3. [Configuration Sections](#configuration-sections)
4. [Feature-Specific Configurations](#feature-specific-configurations)
5. [Environment-Specific Configurations](#environment-specific-configurations)
6. [Advanced Configuration](#advanced-configuration)

## Introduction

Vortex AI uses a TOML-based configuration system that allows you to customize various aspects of its behavior. Previously, different features and modes had separate configuration files, which could be confusing and difficult to manage. The consolidated configuration system combines all these options into a single, comprehensive file.

The consolidated configuration includes:
- Core settings for workspace, debugging, and runtime
- LLM provider and model settings
- Agent capabilities and behavior
- Server settings for web access
- Security settings, including admin mode
- Sandbox environment configuration
- Reinforcement learning settings
- Knowledge and learning capabilities
- Conversation history management (condensers)

## Using the Consolidated Configuration

### Basic Usage

1. Copy the consolidated template to create your configuration:

```bash
cp config.consolidated.toml config.toml
```

2. Edit the configuration file to set your API keys and customize settings:

```bash
nano config.toml
```

3. Start Vortex with the new configuration:

```bash
python start_web_server.py
```

### Minimal Configuration

For a minimal configuration, you only need to set the LLM API key and model:

```toml
[llm]
api_key = "your-api-key"
model = "gpt-4o"
```

All other settings will use their default values.

## Configuration Sections

### Core Settings

The `[core]` section controls fundamental aspects of Vortex:

```toml
[core]
# Base path for the workspace
workspace_base = "./workspace"
# Maximum iterations
max_iterations = 500
# Path to store trajectories
save_trajectory_path = "./trajectories"
# Runtime environment
runtime = "local"
# Default agent
default_agent = "VortexAgent"
```

### LLM Settings

The `[llm]` section configures the language model:

```toml
[llm]
# Provider to use
provider = "openai"
# API key
api_key = "your-api-key"
# Model to use
model = "gpt-4o"
# Temperature
temperature = 0.7
# Maximum output tokens
max_output_tokens = 1024
```

### Agent Settings

The `[agent]` section controls agent capabilities:

```toml
[agent]
# Enable browsing
enable_browsing = true
# Enable Jupyter
enable_jupyter = true
# Enable LLM editor
enable_llm_editor = true
# Enable prompt extensions
enable_prompt_extensions = true
# Enable history truncation
enable_history_truncation = true
```

### Server Settings

The `[server]` section configures the web server:

```toml
[server]
# Host to bind to
host = "0.0.0.0"
# Port to run on
port = 12000
# Debug mode
debug = false
# Log level
log_level = "info"
```

### Security Settings

The `[security]` section controls security features:

```toml
[security]
# Admin mode (unrestricted capabilities)
admin_mode = true
# Confirmation mode
confirmation_mode = false
# Security analyzer
enable_security_analyzer = false
```

### Sandbox Settings

The `[sandbox]` section configures the sandbox environment:

```toml
[sandbox]
# Timeout in seconds
timeout = 300
# Use host network
use_host_network = true
# Enable GPU support
enable_gpu = true
# Keep runtime alive
keep_runtime_alive = true
```

### Reinforcement Learning Settings

The `[rl]` section controls reinforcement learning:

```toml
[rl]
# Enable reinforcement learning
enabled = true
# Maximum turns
max_turns = 10
# Rollout strategy
rollout_strategy = "StandardReAct"
# Storage backend
storage_backend = "file"
# Trajectory path
trajectory_path = "./rl_trajectories"
# Enable training
enable_training = true
```

### Learning Settings

The `[learning]` section configures learning capabilities:

```toml
[learning]
# Enable learning
enabled = true
# Enable reinforcement learning
reinforcement_learning = true
# Enable knowledge acquisition
knowledge_acquisition = true
# Learn from feedback
learn_from_feedback = true
# Knowledge path
knowledge_path = "./knowledge"
```

### Condenser Settings

The `[condenser]` section controls conversation history management:

```toml
[condenser]
# Condenser type
type = "amortized"
# Keep first N events
keep_first = 1
# Maximum history size
max_size = 100
```

## Feature-Specific Configurations

### Multiple LLM Configurations

You can define multiple LLM configurations for different purposes:

```toml
[llm]
# Default LLM configuration
api_key = "your-api-key"
model = "gpt-4o"

[llm.gpt4o-mini]
# Configuration for a specific purpose
api_key = "your-api-key"
model = "gpt-4o"

[llm.gemini-2-flash]
# Configuration for Google's Gemini model
api_key = "your-gemini-api-key"
model = "gemini-2.0-flash"
provider = "google"
```

### Agent-Specific Configurations

You can customize settings for specific agent types:

```toml
[agent]
# Default agent configuration
enable_browsing = true

[agent.RepoExplorerAgent]
# Use a cheaper model for repository exploration
llm_config = "gpt3"
```

## Environment-Specific Configurations

### Local Development

For local development, you might want to enable debugging:

```toml
[core]
debug = true

[server]
debug = true
```

### Production Deployment

For production, you should disable debugging and secure the server:

```toml
[core]
debug = false

[server]
debug = false
host = "127.0.0.1"  # Only allow local connections

[security]
admin_mode = false  # Disable admin mode
```

### Resource-Constrained Environments

For environments with limited resources:

```toml
[rl]
max_workers = 4  # Reduce worker threads

[sandbox]
enable_gpu = false  # Disable GPU support
```

## Advanced Configuration

### Custom Condenser Configuration

For advanced conversation history management:

```toml
[condenser]
type = "llm"
llm_config = "condenser"
keep_first = 1
max_size = 100

[llm.condenser]
model = "gpt-4o"
temperature = 0.1
max_tokens = 1024
```

### MongoDB Trajectory Storage

For larger deployments, you can use MongoDB:

```toml
[rl]
storage_backend = "mongodb"
mongodb_uri = "mongodb://localhost:27017"
mongodb_db = "vortex"
mongodb_collection = "trajectories"
```

### Custom Runtime Environment

For custom runtime environments:

```toml
[sandbox]
base_container_image = "custom/image:latest"
runtime_extra_deps = "numpy pandas scikit-learn"
runtime_startup_env_vars = { PYTHONPATH = "/app", DEBUG = "1" }
```

## Conclusion

The consolidated configuration system provides a unified way to configure all aspects of Vortex AI. By using a single configuration file, you can easily manage and customize the system to suit your needs.

For more detailed information on specific features, refer to the corresponding documentation:
- [Reinforcement Learning Guide](reinforcement_learning_guide.md)
- [Knowledge Ingestion Guide](knowledge_ingestion_guide.md)
- [Comprehensive Deployment Guide](comprehensive_deployment_guide.md)