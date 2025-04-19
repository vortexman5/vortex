# Comprehensive Vortex CLI Guide

This guide provides detailed instructions on how to set up, configure, and use the Vortex CLI, including its learning capabilities and future development roadmap.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Learning Capabilities](#learning-capabilities)
7. [Knowledge Management](#knowledge-management)
8. [Development Roadmap](#development-roadmap)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

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

### 5. Configure Learning Settings (Optional)

To enable learning features:

```toml
[learning]
# Enable learning features
enable_learning = true

# Trajectory storage
store_trajectories = true
trajectory_path = "/path/to/trajectories"
compression_enabled = true
max_trajectories = 1000

# Knowledge extraction
enable_knowledge_extraction = true
extraction_confidence_threshold = 0.7
auto_create_microagents = false

# Memory configuration
[learning.memory]
enable_persistent_memory = true
memory_path = "/path/to/memory"
short_term_capacity = 100
long_term_threshold = 0.7
episodic_memory_enabled = true

# Vector database
[learning.vector_db]
enabled = true
backend = "chroma"  # "chroma", "faiss"
embedding_model = "all-MiniLM-L6-v2"
similarity_threshold = 0.8

# Reinforcement learning
[learning.rl]
enabled = true
strategy = "adaptive"  # "standard", "tot", "adaptive"
reward_function = "default"
training_enabled = false
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

## Learning Capabilities

### Knowledge Storage in CLI Mode

#### 1. Microagent Knowledge

The primary knowledge storage mechanism in CLI mode is through microagents:

- **Knowledge Microagents**: Specialized agents that provide domain-specific knowledge triggered by keywords
- **Repository Microagents**: Agents that contain repository-specific information and guidelines

These microagents are stored in:
- Global microagents directory: `/path/to/vortex/microagents/`
- Repository-specific microagents: `.openhands/microagents/` within each repository

#### 2. Memory System

The CLI mode uses a simplified memory system that includes:

- **Short-term memory**: Maintains the current conversation context
- **Microagent knowledge**: Triggered by specific keywords in user queries

The `Memory` class in `openhands/memory/memory.py` handles:
- Loading microagents from both global and repository-specific locations
- Responding to recall actions with appropriate knowledge
- Maintaining workspace context information

### Learning Mechanisms in CLI Mode

#### 1. Trajectory Storage

While the CLI mode doesn't have built-in trajectory analysis by default, it does support:

- Recording complete interaction sequences
- Storing these trajectories for later analysis

The trajectory storage is implemented in `openhands/rl/storage.py` with two backends:

1. **File-based storage**:
   ```python
   # Trajectories are stored in:
   ~/.openhands/rl_trajectories/{env_name}/{trajectory_id}.json
   ```

2. **MongoDB storage** (optional):
   ```python
   # Requires pymongo installation
   # Stores trajectories in a MongoDB collection
   ```

#### 2. Reinforcement Learning

The CLI mode includes experimental reinforcement learning capabilities:

- **RLAgent**: An agent that can learn from trajectories
- **Strategies**: Different approaches to problem-solving (StandardReAct, ToT)
- **Training**: The ability to fine-tune models based on successful trajectories

Example usage:
```python
from openhands.rl import RLAgent, RLAgentConfig

# Configure the RL agent
config = RLAgentConfig(
    max_turns=5,
    storage_backend="file",  # Use file-based storage
)

# Create and run the agent
agent = RLAgent(model, tokenizer, config)
results = agent.run(task_description="Your task")

# Train the agent on collected trajectories
agent.train(learning_rate=1e-5, num_epochs=1)
```

### Enabling Learning in CLI Mode

To enable learning features in CLI mode, you need to:

1. Configure trajectory storage in your `config.toml`:

```toml
[learning]
enable_learning = true
store_trajectories = true
trajectory_path = "/path/to/store/trajectories"
```

2. Create custom microagents for domain-specific knowledge:

```markdown
---
name: python_best_practices
type: knowledge
triggers:
  - python best practices
  - python style
  - PEP 8
---

# Python Best Practices

Follow these Python best practices:

1. Follow PEP 8 style guidelines
2. Use meaningful variable names
3. Write docstrings for all functions and classes
4. Use type hints for better code clarity
5. Prefer explicit over implicit
```

3. Save this file in `.openhands/microagents/python_best_practices.md` in your repository

### Feedback Collection

The CLI mode includes a feedback collection mechanism that can be used to improve the agent:

```python
# In openhands/server/data_models/feedback.py
class FeedbackDataModel(BaseModel):
    version: str
    email: str
    polarity: Literal['positive', 'negative']
    permissions: Literal['public', 'private']
    trajectory: list[dict[str, Any]] | None
```

This feedback, along with the associated trajectory, can be sent to a central server for analysis.

## Knowledge Management

### Creating Custom Microagents

Here's how to create a custom knowledge microagent for your CLI environment:

1. Create the microagents directory:
   ```bash
   mkdir -p .openhands/microagents
   ```

2. Create a knowledge microagent file:
   ```bash
   nano .openhands/microagents/git_workflow.md
   ```

3. Add content to the file:
   ```markdown
   ---
   name: git_workflow
   type: knowledge
   triggers:
     - git workflow
     - git branching
     - git commit
   ---
   
   # Git Workflow Best Practices
   
   Our team follows these git practices:
   
   1. Create feature branches from `develop`
   2. Use conventional commits (feat:, fix:, docs:, etc.)
   3. Squash commits before merging
   4. Always pull before pushing
   5. Delete branches after merging
   ```

4. Now when you use the CLI and mention "git workflow", this knowledge will be automatically triggered and provided to the agent.

### Managing Knowledge with CLI Commands

```bash
# View learning status
python -m openhands.cli learning status

# Manage trajectories
python -m openhands.cli learning trajectories list
python -m openhands.cli learning trajectories export --id <trajectory_id> --output <file>
python -m openhands.cli learning trajectories analyze --id <trajectory_id>

# Manage knowledge
python -m openhands.cli learning knowledge list
python -m openhands.cli learning knowledge create --name <n> --content <file>
python -m openhands.cli learning knowledge search --query <query>

# Generate reports
python -m openhands.cli learning report --type performance --period 30d
python -m openhands.cli learning report --type knowledge --format markdown
```

## Development Roadmap

The following roadmap outlines planned enhancements to the Vortex CLI, with a focus on learning and knowledge management capabilities.

### 1. Core Learning Infrastructure

#### 1.1 Trajectory Storage System (Priority: High)

- [ ] **Implement configurable trajectory storage**
  - Create a dedicated configuration section in `config.toml` for learning settings
  - Add support for different storage backends (file, database)
  - Implement automatic trajectory compression for efficient storage

- [ ] **Add trajectory metadata collection**
  - Track execution time, token usage, and success metrics
  - Record system information (OS, Python version, etc.)
  - Store user feedback when available

- [ ] **Create trajectory export/import tools**
  - Implement CLI commands for exporting trajectories as JSON
  - Add functionality to import trajectories from JSON
  - Support batch operations for multiple trajectories

#### 1.2 Learning Manager (Priority: High)

- [ ] **Create a central learning manager component**
  - Implement `LearningManager` class to coordinate learning activities
  - Add hooks for trajectory recording, analysis, and knowledge extraction
  - Create interfaces for different learning strategies

- [ ] **Implement learning configuration**
  - Add learning-specific settings to `config.toml`
  - Create validation for learning configuration
  - Implement feature flags for enabling/disabling learning features

#### 1.3 Knowledge Extraction Pipeline (Priority: Medium)

- [ ] **Build automated knowledge extraction**
  - Create a system to identify reusable patterns from trajectories
  - Implement extraction of code snippets and solutions
  - Add metadata tagging for extracted knowledge

- [ ] **Implement knowledge validation**
  - Add verification steps for extracted knowledge
  - Create confidence scoring for extracted patterns
  - Implement conflict resolution for contradictory knowledge

### 2. Knowledge Management Enhancements

#### 2.1 Enhanced Microagent System (Priority: High)

- [ ] **Expand microagent capabilities**
  - Add support for more complex trigger patterns (regex, semantic matching)
  - Implement priority levels for microagents
  - Create hierarchical organization of microagents

- [ ] **Add microagent management commands**
  - Create CLI commands for listing, creating, and editing microagents
  - Implement validation for microagent content
  - Add search functionality for finding relevant microagents

- [ ] **Implement microagent versioning**
  - Add version tracking for microagents
  - Create update mechanism for microagents
  - Implement rollback capability for problematic updates

#### 2.2 Vector Database Integration (Priority: Medium)

- [ ] **Add vector database support**
  - Integrate with Chroma, FAISS, or similar vector database
  - Implement embedding generation for knowledge fragments
  - Create efficient retrieval mechanisms

- [ ] **Implement semantic search**
  - Add natural language querying of knowledge base
  - Create relevance scoring for search results
  - Implement context-aware search capabilities

### 3. Memory System Improvements

#### 3.1 Enhanced Memory Architecture (Priority: High)

- [ ] **Implement multi-level memory system**
  - Create distinct short-term, working, and long-term memory
  - Add memory management policies (retention, pruning)
  - Implement memory persistence across sessions

- [ ] **Add memory indexing**
  - Create efficient indexing for memory retrieval
  - Implement priority-based memory organization
  - Add temporal indexing for time-based retrieval

#### 3.2 Episodic Memory (Priority: Medium)

- [ ] **Implement episodic memory system**
  - Create storage for complete interaction episodes
  - Add metadata and tagging for episodes
  - Implement similarity-based episode retrieval

- [ ] **Add episode summarization**
  - Create automatic summarization of episodes
  - Implement extraction of key insights from episodes
  - Add progressive summarization for older episodes

### 4. Implementation Timeline

#### Phase 1: Foundation (Months 1-2)

- Implement core trajectory storage system
- Create learning manager component
- Enhance microagent system
- Implement basic feedback collection

#### Phase 2: Enhancement (Months 3-4)

- Add knowledge extraction pipeline
- Implement multi-level memory system
- Integrate vector database
- Expand RL framework

#### Phase 3: Advanced Features (Months 5-6)

- Implement episodic memory
- Add automated evaluation
- Create knowledge sharing mechanisms
- Implement strategy optimization

#### Phase 4: Refinement (Months 7-8)

- Add memory visualization
- Implement learning reports
- Create knowledge exploration tools
- Refine and optimize all systems

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