# Vortex Learning in CLI Mode

This document explains how learning and knowledge management work specifically in the CLI mode of Vortex.

## Overview

In CLI mode, Vortex uses the same core learning and knowledge management systems as described in the [Learning and Knowledge Management](learning_and_knowledge.md) document, but with some specific implementations and limitations.

## Knowledge Storage in CLI Mode

### 1. Microagent Knowledge

The primary knowledge storage mechanism in CLI mode is through microagents:

- **Knowledge Microagents**: Specialized agents that provide domain-specific knowledge triggered by keywords
- **Repository Microagents**: Agents that contain repository-specific information and guidelines

These microagents are stored in:
- Global microagents directory: `/path/to/vortex/microagents/`
- Repository-specific microagents: `.openhands/microagents/` within each repository

### 2. Memory System

The CLI mode uses a simplified memory system that includes:

- **Short-term memory**: Maintains the current conversation context
- **Microagent knowledge**: Triggered by specific keywords in user queries

The `Memory` class in `openhands/memory/memory.py` handles:
- Loading microagents from both global and repository-specific locations
- Responding to recall actions with appropriate knowledge
- Maintaining workspace context information

## Learning Mechanisms in CLI Mode

### 1. Trajectory Storage

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

### 2. Reinforcement Learning

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

## Enabling Learning in CLI Mode

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

## Feedback Collection

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

## Limitations in CLI Mode

The CLI mode has some limitations compared to the server mode:

1. **No built-in trajectory analysis**: While trajectories can be stored, there's no automatic analysis
2. **Limited memory persistence**: Memory is primarily session-based
3. **No automatic knowledge distillation**: Knowledge must be manually created as microagents

## Best Practices for Learning in CLI Mode

1. **Create repository-specific microagents**:
   ```bash
   mkdir -p .openhands/microagents
   touch .openhands/microagents/repo.md
   ```

2. **Add domain-specific knowledge microagents**:
   ```bash
   # Create a knowledge microagent for your domain
   nano .openhands/microagents/domain_knowledge.md
   ```

3. **Enable trajectory storage**:
   ```toml
   # In config.toml
   [learning]
   enable_learning = true
   store_trajectories = true
   ```

4. **Analyze stored trajectories**:
   ```bash
   # List stored trajectories
   ls ~/.openhands/rl_trajectories/
   
   # Analyze a specific trajectory
   python -m openhands.tools.analyze_trajectory ~/.openhands/rl_trajectories/example/123.json
   ```

5. **Provide feedback after tasks**:
   ```bash
   # When using CLI
   python -m openhands.cli --feedback "This solution was efficient" --rating 5
   ```

## Example: Creating a Custom Knowledge Microagent

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

## Conclusion

While the CLI mode has a more simplified learning system compared to the full server deployment, it still provides powerful mechanisms for knowledge management through microagents and experimental reinforcement learning capabilities. By creating custom microagents and enabling trajectory storage, you can enhance the agent's knowledge and potentially improve its performance over time.