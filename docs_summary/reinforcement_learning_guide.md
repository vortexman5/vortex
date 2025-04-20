# Enabling Reinforcement Learning in Vortex

This guide explains how to enable and configure reinforcement learning in Vortex AI for all modes of operation.

## Table of Contents

1. [Introduction](#introduction)
2. [Configuration Options](#configuration-options)
3. [Enabling Reinforcement Learning](#enabling-reinforcement-learning)
   - [Using the Template Configuration](#using-the-template-configuration)
   - [Modifying an Existing Configuration](#modifying-an-existing-configuration)
4. [Reinforcement Learning Components](#reinforcement-learning-components)
5. [Advanced Configuration](#advanced-configuration)
6. [Monitoring and Analysis](#monitoring-and-analysis)
7. [Troubleshooting](#troubleshooting)

## Introduction

Vortex includes a powerful reinforcement learning (RL) system that enables the agent to improve over time through experience. By default, this system may not be enabled in all configurations, but it can be easily activated to enhance the agent's capabilities.

Reinforcement learning in Vortex allows the agent to:

- Learn from past interactions
- Improve response quality over time
- Adapt to user preferences
- Optimize for specific tasks
- Store and analyze interaction trajectories

## Configuration Options

The reinforcement learning system in Vortex is controlled by two main configuration sections:

1. **`[rl]` section**: Controls the core reinforcement learning functionality
2. **`[learning]` section**: Controls broader learning capabilities, including reinforcement learning

Here are the key configuration options for each section:

### RL Section Options

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Whether to enable reinforcement learning | `false` |
| `max_turns` | Maximum number of turns in a conversation | `10` |
| `max_prompt_length` | Maximum length of prompt | `2048` |
| `max_response_length` | Maximum length of response | `512` |
| `max_obs_length` | Maximum length of observation | `1024` |
| `react_format` | Whether to use ReAct format | `true` |
| `rollout_strategy` | Strategy to use for rollout | `"StandardReAct"` |
| `storage_backend` | Backend for storing trajectories | `"file"` |
| `max_workers` | Maximum number of worker threads | `10` |
| `trajectory_path` | Path to store trajectories | `"./rl_trajectories"` |
| `enable_training` | Whether to enable training | `false` |
| `learning_rate` | Learning rate for training | `1e-5` |
| `num_epochs` | Number of training epochs | `3` |
| `batch_size` | Batch size for training | `8` |
| `max_grad_norm` | Maximum gradient norm for clipping | `1.0` |

### Learning Section Options

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Whether learning is enabled | `false` |
| `reinforcement_learning` | Whether reinforcement learning is enabled | `false` |
| `knowledge_acquisition` | Whether knowledge acquisition is enabled | `false` |
| `learn_from_feedback` | Whether to automatically learn from user feedback | `false` |
| `learn_from_errors` | Whether to automatically learn from errors | `false` |
| `knowledge_path` | Path to store learned knowledge | `"./knowledge"` |
| `max_knowledge_size` | Maximum size of knowledge base (in MB) | `1000` |
| `consolidation_frequency` | Frequency of knowledge consolidation (in hours) | `24` |

## Enabling Reinforcement Learning

### Using the Consolidated Template Configuration

The easiest way to enable reinforcement learning is to use the provided consolidated template configuration file:

1. Copy the consolidated template:

```bash
cp config.consolidated.toml config.toml
```

2. Edit the configuration file to set your API keys and other settings:

```bash
nano config.toml
```

3. Start Vortex with the new configuration:

```bash
python start_web_server.py
```

> **Note**: The consolidated template already has reinforcement learning enabled by default.

### Modifying an Existing Configuration

If you already have a configuration file, you can enable reinforcement learning by adding the following sections:

```toml
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
trajectory_path = "./rl_trajectories"
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
knowledge_path = "./knowledge"
```

Also, make sure to add trajectory storage settings to the `[core]` section:

```toml
[core]
# ... other core settings ...
# Path to store trajectories
save_trajectory_path = "./trajectories"
# Whether to save screenshots in the trajectory
save_screenshots_in_trajectory = true
```

## Reinforcement Learning Components

The Vortex reinforcement learning system consists of several key components:

### 1. RLController

The central component that manages the reinforcement learning process. It:
- Organizes RL tasks
- Executes rollout strategies
- Manages trajectory storage
- Supports parallel execution

### 2. Task

Represents a reinforcement learning task with:
- Environment definition
- Client management

### 3. Trajectory Storage

Stores interaction trajectories for learning:
- FileTrajectoryStorage: Stores trajectories in the file system
- MongoDBTrajectoryStorage: Stores trajectories in a MongoDB database

### 4. Rollout Strategies

Define how the agent interacts with environments:
- StandardReActStrategy: Basic strategy following the ReAct paradigm
- Custom strategies for specialized interaction patterns

## Advanced Configuration

### Customizing Rollout Strategies

You can customize the rollout strategy by creating a custom strategy class and specifying it in the configuration:

```toml
[rl]
rollout_strategy = "CustomStrategy"
```

### Using MongoDB for Trajectory Storage

For larger deployments, you can use MongoDB to store trajectories:

```toml
[rl]
storage_backend = "mongodb"
mongodb_uri = "mongodb://localhost:27017"
mongodb_db = "vortex"
mongodb_collection = "trajectories"
```

### Optimizing Worker Threads

Adjust the number of worker threads based on your system's capabilities:

```toml
[rl]
max_workers = 16  # Increase for more powerful systems
```

## Monitoring and Analysis

### Trajectory Analysis

You can analyze stored trajectories to understand agent performance:

```bash
# Create a directory for analysis results
mkdir -p analysis

# Run the trajectory analysis script
python scripts/analyze_trajectories.py --input-dir rl_trajectories --output-dir analysis
```

### Performance Metrics

Monitor key performance metrics:
- Success rate
- Average turns per task
- Learning curve
- Error rate

## Troubleshooting

### Common Issues

1. **Trajectories not being stored**
   - Check that the trajectory path exists and is writable
   - Verify that `save_trajectory_path` is correctly set in the configuration

2. **High memory usage**
   - Reduce `max_workers` to limit parallel execution
   - Set lower values for `max_prompt_length` and `max_response_length`

3. **Slow performance**
   - Use file storage instead of MongoDB for smaller deployments
   - Reduce the frequency of trajectory saving

4. **Training not improving performance**
   - Increase `num_epochs` and `batch_size`
   - Adjust `learning_rate` to find the optimal value
   - Ensure you have enough trajectory data for effective training

### Logs and Debugging

Enable debug logging to troubleshoot reinforcement learning issues:

```toml
[core]
debug = true
```

Check the logs for reinforcement learning-related messages:

```bash
grep -i "reinforcement\|rl\|learning" logs/vortex.log
```

## Conclusion

By enabling reinforcement learning in Vortex, you can significantly enhance the agent's capabilities and performance over time. The system is designed to be flexible and customizable, allowing you to adapt it to your specific needs and use cases.

For more detailed information on the reinforcement learning system, refer to the [Reinforcement Learning System](03_reinforcement_learning.md) documentation.