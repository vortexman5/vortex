# Vortex Documentation

Welcome to the Vortex (OpenHands AI Framework) documentation. This collection of documents provides comprehensive information on how to set up, configure, and use Vortex in various deployment scenarios.

## Available Documentation

### Getting Started

- [CLI Tool Guide](cli_tool_guide.md) - Detailed instructions on how to set up and run Vortex as a command-line tool
- [Server Deployment Guide](server_deployment_guide.md) - Comprehensive guide for deploying Vortex as a server for multi-user access

### Technical Documentation

- [Architecture Overview](architecture_overview.md) - Detailed explanation of the Vortex architecture and how components interact
- [Learning and Knowledge Management](learning_and_knowledge.md) - How Vortex learns, stores knowledge, and improves over time

## External Resources

- [Original Repository](https://codeberg.org/Adamcatholic/vortex) - The official Vortex repository on Codeberg
- [README](../README.md) - The main README file for the Vortex project

## Quick Start

To quickly get started with Vortex as a CLI tool:

```bash
# Clone the repository
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex

# Install dependencies
pip install poetry
poetry install
poetry shell

# Create a configuration file
cp config.template.toml config.toml

# Edit the configuration file to add your API keys
# nano config.toml

# Run a simple task
python -m openhands.cli -t "Write a hello world program in Python"
```

For more detailed instructions, please refer to the specific documentation files linked above.

## Contributing to Documentation

If you find any issues or have suggestions for improving this documentation, please feel free to contribute by:

1. Creating an issue in the repository
2. Submitting a pull request with your changes
3. Contacting the maintainers directly

We appreciate your help in making this documentation more comprehensive and user-friendly!