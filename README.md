# Vortex (OpenHands AI Framework)

## Overview

Vortex is an implementation of the OpenHands AI framework, a powerful and flexible system designed to create, manage, and deploy AI agents. This framework provides a comprehensive set of tools and components for building sophisticated AI applications with state-of-the-art language models.

![OpenHands System Architecture Diagram](docs_summary/static/img/system_architecture_overview.png)

## Key Features

- **Multiple LLM Support**: Seamlessly integrate with various language models including Claude, GPT-4, Gemini, and others
- **Flexible Architecture**: Modular design allows for easy customization and extension
- **Robust Memory System**: Sophisticated knowledge storage and retrieval mechanisms
- **Secure Execution**: Sandboxed runtime environments for safe execution of code
- **Scalable Deployment**: Deploy on custom servers with various configuration options
- **Event-Driven Communication**: Central event stream for efficient component interaction
- **Microagent Support**: Specialized agents for domain-specific knowledge and tasks
- **Admin Mode**: Advanced mode for unrestricted agent capabilities (for personal use only)

## Table of Contents

- [Architecture](#architecture)
- [Models](#models)
- [Knowledge Storage](#knowledge-storage)
- [Pipelines](#pipelines)
- [Restrictions and Security](#restrictions-and-security)
- [Admin Mode](#admin-mode)
- [Deployment](#deployment)
- [Remote Access](#remote-access)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Architecture

The OpenHands framework consists of several key components that work together to create a flexible and powerful AI system:

### Core Components

- **LLM**: Brokers all interactions with large language models, supporting various providers through LiteLLM
- **Agent**: Responsible for analyzing the current State and producing Actions
- **AgentController**: Initializes the Agent, manages State, and drives the main execution loop
- **State**: Represents the current state of the Agent's task, including history and plans
- **EventStream**: Central hub for Events, enabling communication between components
- **Runtime**: Executes Actions and returns Observations
- **Server**: Manages OpenHands sessions over HTTP for frontend interaction

### Control Flow

The basic loop that drives agents follows this pattern:

```python
while True:
  prompt = agent.generate_prompt(state)
  response = llm.completion(prompt)
  action = agent.parse_response(response)
  observation = runtime.run(action)
  state = state.update(action, observation)
```

In practice, this is implemented through message passing via the EventStream, which serves as the backbone for all communication in OpenHands.

## Models

### Supported Language Models

The framework supports multiple language models through a unified interface:

#### Claude Models
- claude-3-7-sonnet-20250219
- claude-3-5-sonnet-20241022
- claude-3-5-sonnet-20240620
- claude-3-5-haiku-20241022
- claude-3-haiku-20240307
- claude-3-opus-20240229

#### OpenAI Models
- gpt-4o-mini
- gpt-4o
- gpt-4.1

#### Anthropic Models
- o1-2024-12-17
- o3-mini-2025-01-31
- o3-mini

#### Google Models
- gemini-2.5-pro

### Model Capabilities

Different models support various capabilities:

1. **Cache Prompt Support**: Some models support caching prompts for efficiency
2. **Function Calling Support**: Models that can use tools through function calling
3. **Reasoning Effort Support**: Models that support explicit reasoning parameters

## Knowledge Storage

### Memory System

The memory system consists of:

1. **Short-Term History**: 
   - Filters the event stream for context
   - Condenses history when context limits are reached

2. **Memory Condenser**:
   - Summarizes chunks of events
   - Prioritizes earlier events for summarization

### Microagents

Specialized components for knowledge retrieval:

1. **Knowledge Microagents**: Domain-specific knowledge
2. **Repo Microagents**: Repository-specific information

### Storage Backends

Multiple storage options for persistence:

1. **Local Storage**: File-based local storage
2. **S3 Storage**: Amazon S3 compatible storage
3. **Google Cloud Storage**: Google Cloud backend
4. **In-Memory Storage**: Temporary storage

## Pipelines

### Event-Driven Architecture

The EventStream enables asynchronous communication between components:

```
Agent --Actions--> AgentController
AgentController --State--> Agent
AgentController --Actions--> EventStream
EventStream --Observations--> AgentController
Runtime --Observations--> EventStream
EventStream --Actions--> Runtime
Frontend --Actions--> EventStream
```

### Key Pipeline Components

1. **Agent Controller Pipeline**: Manages state and drives execution
2. **Runtime Pipeline**: Executes actions in sandboxed environments
3. **Memory Pipeline**: Handles knowledge storage and retrieval
4. **Server Pipeline**: Manages HTTP sessions and frontend communication

## Restrictions and Security

### Runtime Restrictions

- **Sandbox Isolation**: Containerized execution environments
- **Resource Limitations**: Limits on execution time, memory, CPU, and disk space
- **Command Filtering**: Blocks potentially dangerous commands

### LLM Restrictions

- **Token Limits**: Prevents excessive resource usage
- **Content Filtering**: Blocks harmful or inappropriate content
- **Rate Limiting**: Prevents API abuse

### Authentication and Authorization

- User authentication
- Role-based access control
- API key management
- Session management

## Admin Mode

For advanced users who need unrestricted agent capabilities, OpenHands provides an admin mode that bypasses security restrictions. This mode is intended for personal use only and should be used with extreme caution.

### What is Admin Mode?

Admin mode disables the security checks that normally prevent potentially risky operations. When enabled:

- Security analyzers (like the Invariant analyzer) will not block any actions
- Confirmation prompts for potentially dangerous operations are bypassed
- The agent has unrestricted access to execute commands and modify files

### How to Enable Admin Mode

1. **Create a dedicated admin configuration file**:
   ```bash
   cp config.template.toml config.admin.toml
   ```

2. **Edit the configuration file** to enable admin mode:
   ```toml
   [security]
   # Enable admin mode with unrestricted capabilities
   admin_mode = true
   
   # Use the invariant security analyzer (will be bypassed in admin mode)
   security_analyzer = "invariant"
   
   # Disable confirmation mode for convenience
   confirmation_mode = false
   ```

3. **Start OpenHands with the admin configuration**:
   ```bash
   # For CLI mode
   python -m openhands.cli --config config.admin.toml
   
   # For server mode
   python -m openhands.server --config config.admin.toml
   ```

For detailed instructions and security implications, see the [Admin Mode Documentation](docs/admin_mode.md).

## Deployment

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 16GB minimum (32GB+ recommended for production)
- **Storage**: 50GB SSD (100GB+ recommended for production)
- **Network**: Stable internet connection with at least 10Mbps upload/download

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
- **Node.js**: version 20.x or newer

### Installation Steps

1. **System Preparation**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y build-essential curl git python3-pip python3-dev
   # Install Docker, Docker Compose, Node.js
   ```

2. **Clone the Repository**:
   ```bash
   git clone https://codeberg.org/Adamcatholic/vortex.git
   cd vortex
   pip3 install poetry
   poetry install
   ```

3. **Configuration**:
   ```bash
   cp config.template.toml config.toml
   # Edit configuration file as needed
   ```

4. **Docker Deployment**:
   ```bash
   docker-compose up -d
   ```

## Remote Access

### Web Interface

Access from any device with a web browser:
- Navigate to `https://your-domain.com` or `http://your-server-ip:8000`

### API Access

For programmatic access:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{"message": "Hello, OpenHands!"}' \
  https://your-domain.com/api/v1/message
```

### Mobile Access

- Responsive web interface works on mobile browsers
- Create home screen shortcuts for better experience

## Customization

### Extending the Pipeline

1. Create custom Event types
2. Implement custom EventStream subscribers
3. Develop specialized Agents
4. Create custom Runtime environments

### Modifying Restrictions

Adjust restrictions through:
1. Configuration files (config.toml)
2. Environment variables
3. Custom security policies

### Adding Knowledge Databases

1. Create custom microagents in the `microagents` directory
2. Update configuration to include new microagents
3. Implement knowledge retrieval logic

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if the server is running
   - Verify firewall settings

2. **Authentication Failures**
   - Verify auth token configuration
   - Check API request headers

3. **Performance Issues**
   - Monitor system resources
   - Check container resource usage

4. **LLM API Errors**
   - Verify API keys
   - Check provider status

## Contributing

We welcome contributions to the Vortex project! Please see our contributing guidelines for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Documentation

For comprehensive documentation, please refer to the [docs_summary](docs_summary/README.md) directory, which contains:

### Core Documentation
- [Overview](docs_summary/01_overview.md) - Introduction to the Vortex framework
- [Memory System](docs_summary/02_memory_system.md) - Details on the memory system architecture
- [Reinforcement Learning](docs_summary/03_reinforcement_learning.md) - Information on the reinforcement learning capabilities
- [Microagents](docs_summary/04_microagents.md) - Overview of the microagent system
- [LLM Integration](docs_summary/05_llm_integration.md) - Details on LLM integration and capabilities
- [Agent System](docs_summary/06_agent_system.md) - Information on the agent system architecture
- [Runtime Environment](docs_summary/07_runtime_environment.md) - Information on the secure runtime environment
- [Getting Started](docs_summary/08_getting_started.md) - Guide to installing and using the Vortex framework

### Comprehensive Guides
- [Comprehensive CLI Guide](docs_summary/comprehensive_cli_guide.md) - Complete guide to using and extending the Vortex CLI
- [Comprehensive Deployment Guide](docs_summary/comprehensive_deployment_guide.md) - Complete guide to deploying Vortex in various configurations
- [Knowledge Ingestion Guide](docs_summary/knowledge_ingestion_guide.md) - Detailed guide for feeding books, documentation, and other knowledge sources into Vortex

### Additional Resources
- [Admin Mode Guide](docs/admin_mode.md) - Guide to using admin mode for unrestricted capabilities