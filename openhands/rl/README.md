# Reinforcement Learning for OpenHands

This module implements reinforcement learning capabilities for OpenHands agents, allowing them to learn from interactions with environments and improve over time.

## Overview

The reinforcement learning module provides:

- Environment interfaces for agent-environment interaction
- Rollout strategies for exploring environment states
- Trajectory storage for saving and retrieving experiences
- Training capabilities for improving agent performance

## Components

### Environment Interface

The environment interface defines how agents interact with environments:

- `BaseEnvClient`: Abstract base class for environment clients
- `WebEnvClient`: Implementation for web-based environments

### Rollout Strategies

Rollout strategies determine how agents explore the environment:

- `StandardReActStrategy`: Basic ReAct strategy for sequential decision-making
- `ToTStrategy`: Tree of Thoughts strategy for exploring multiple paths
- `MCTSStrategy`: Monte Carlo Tree Search for optimizing actions

### Trajectory Storage

Trajectory storage backends save and retrieve agent experiences:

- `FileTrajectoryStorage`: File-based storage for trajectories
- `MongoDBTrajectoryStorage`: MongoDB-based storage for trajectories

### RL Agent

The RL agent integrates with OpenHands' LLM system:

- `RLAgent`: Main agent class for reinforcement learning
- `RLAgentConfig`: Configuration for the RL agent

## Usage

### Basic Usage

```python
from openhands.rl import RLAgent, RLAgentConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Configure the RL agent
config = RLAgentConfig(
    max_turns=5,
    env_name="webshop",
    rollout_strategy="StandardReAct"
)

# Create the RL agent
agent = RLAgent(
    model=model,
    tokenizer=tokenizer,
    config=config
)

# Define a task and run the agent
task_description = "Find a suitable backpack that costs less than $100."
results = agent.run(task_description=task_description)
```

### Training

```python
# Train the agent on collected trajectories
agent.train(
    learning_rate=1e-5,
    num_epochs=3,
    batch_size=8
)
```

## Configuration

The RL module can be configured in the OpenHands config file:

```toml
[rl]
max_turns = 10
max_prompt_length = 2048
max_response_length = 512
max_obs_length = 1024
react_format = true
env_name = "webshop"
env_port = 8000
env_server_base = "http://127.0.0.1"
rollout_strategy = "StandardReAct"
storage_backend = "file"
max_workers = 10
```

## Environment Setup

To use the RL module, you need to set up an environment server that implements the expected API:

- `/reset`: Reset the environment to a specific state
- `/step`: Take an action in the environment and return the result

The environment server should return responses in the following format:

```json
{
  "state": "Description of the current state",
  "reward": 0.5,
  "done": false
}
```