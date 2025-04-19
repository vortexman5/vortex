# Reinforcement Learning System

The Vortex Reinforcement Learning (RL) system enables agents to improve over time through experience. It manages the interaction between agents and environments, executes rollout strategies, and stores trajectories for future learning.

## Core Components

### RLController

The `RLController` is the central component of the RL system, responsible for:

1. **Task Management**: Organizes reinforcement learning tasks and their associated environment clients.
2. **Strategy Execution**: Executes rollout strategies to collect experience data.
3. **Trajectory Storage**: Manages the storage of experience trajectories for future learning.
4. **Parallel Execution**: Supports parallel rollout of tasks for efficient data collection.

```python
# Key methods in the RLController
def rollout(
    self,
    generation_config: Optional[Any] = None,
    max_rounds: Optional[int] = None,
    idxs: Optional[List[int]] = None,
    save_to_storage: bool = True,
    parallel: bool = True,
    batch_size: int = 1,
    metadata: Optional[Dict[str, Any]] = None
) -> List[ExperienceOutput]:
    # Executes rollout using the selected strategy
```

### Task

The `Task` class represents a reinforcement learning task:

1. **Environment Definition**: Specifies the environment name and associated clients.
2. **Client Management**: Maintains a list of environment clients for interaction.

```python
class Task:
    def __init__(
        self,
        env_name: str,
        clients: List[BaseEnvClient]
    ):
        self.env_name = env_name
        self.clients = clients
```

### Trajectory Storage

The RL system supports different trajectory storage implementations:

1. **FileTrajectoryStorage**: Stores trajectories in the file system.
2. **MongoDBTrajectoryStorage**: Stores trajectories in a MongoDB database.

These storage implementations allow for:
- Persistent storage of experience data
- Retrieval of past experiences for learning
- Analysis of agent performance over time

## Rollout Strategies

Rollout strategies define how the agent interacts with environments to collect experience:

1. **StandardReActStrategy**: A basic strategy that follows the ReAct (Reasoning and Acting) paradigm.
2. **Custom Strategies**: The system supports custom strategies for specialized interaction patterns.

Strategies control:
- How many interaction rounds to perform
- When to terminate an episode
- How to process environment observations
- How to generate agent actions

## Execution Flow

The RL system's execution flow follows these steps:

1. **Task Setup**: Define tasks with appropriate environments and clients.
2. **Strategy Selection**: Choose or implement a rollout strategy.
3. **Rollout Execution**: Execute the strategy to collect experience data.
4. **Trajectory Storage**: Store the collected trajectories for future learning.
5. **Model Improvement**: Use the stored trajectories to improve the agent's model (typically offline).

```python
# Example execution flow
controller = RLController(agent, tasks, strategy, storage)
experiences = controller.rollout(
    max_rounds=10,
    parallel=True,
    batch_size=4
)
```

## Parallel Execution

The RL system supports parallel execution of tasks for efficient data collection:

1. **Thread Pool**: Uses a thread pool to execute multiple tasks concurrently.
2. **Batch Processing**: Processes tasks in batches to control resource usage.
3. **Result Collection**: Collects and organizes results from parallel executions.

```python
# Parallel execution in RLController
futures = {}
for idx in batch_idxs:
    future = self.executor.submit(
        self._rollout_one,
        task=task,
        idx=idx,
        generation_config=generation_config,
        max_rounds=max_rounds,
        save_to_storage=save_to_storage,
        metadata=metadata
    )
    futures[future] = idx
```

## Integration with Other Components

The RL system integrates with other Vortex components:

1. **Agent**: Uses the agent to generate actions based on environment observations.
2. **Environment**: Interacts with environments to collect experience data.
3. **Storage**: Stores trajectories for future learning and analysis.

## Customization

The RL system can be customized in several ways:

1. **Custom Environments**: Create specialized environments for specific domains or tasks.
2. **Custom Strategies**: Implement custom rollout strategies for specialized interaction patterns.
3. **Custom Storage**: Implement custom trajectory storage for specialized persistence needs.
4. **Extended Metadata**: Add additional metadata to trajectories for richer analysis.