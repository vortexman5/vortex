# Vortex Learning and Knowledge Management

This document explains how Vortex learns from interactions, stores knowledge, and improves over time with each task.

## Table of Contents

1. [Learning Architecture](#learning-architecture)
2. [Knowledge Storage](#knowledge-storage)
3. [Continuous Learning](#continuous-learning)
4. [Memory Systems](#memory-systems)
5. [Feedback Mechanisms](#feedback-mechanisms)
6. [Configuration for Learning](#configuration-for-learning)
7. [Best Practices](#best-practices)

## Learning Architecture

Vortex employs a multi-layered learning architecture that combines several approaches to knowledge acquisition and retention:

### 1. Foundation Model Learning

At its core, Vortex relies on pre-trained large language models (LLMs) like Claude, GPT-4, or Gemini. These models contain broad knowledge acquired during their training. However, Vortex extends this with several custom learning mechanisms:

### 2. Trajectory-Based Learning

Vortex records complete interaction trajectories (sequences of actions and observations) that can be:
- Analyzed to identify successful patterns
- Used to train improved agents
- Replayed to demonstrate successful approaches

### 3. Microagent Knowledge

Specialized microagents maintain domain-specific knowledge that can be updated and refined over time.

### 4. Memory Systems

Multiple memory systems work together to retain and utilize knowledge:
- Short-term memory for immediate context
- Long-term memory for persistent knowledge
- Episodic memory for specific experiences

## Knowledge Storage

Vortex stores knowledge in several formats and locations:

### 1. Trajectory Database

```
/data/vortex/trajectories/
```

This directory contains JSON files of complete interaction sequences, including:
- User inputs
- Agent actions
- System observations
- Final outcomes
- Metadata (timestamps, success metrics, etc.)

Example trajectory structure:
```json
{
  "id": "traj_20250419_001",
  "task": "Create a Python web server",
  "start_time": "2025-04-19T10:15:30Z",
  "end_time": "2025-04-19T10:18:45Z",
  "success": true,
  "events": [
    {"type": "user_message", "content": "Create a Python web server", "timestamp": "2025-04-19T10:15:30Z"},
    {"type": "agent_action", "action": "file_write", "path": "server.py", "content": "...", "timestamp": "2025-04-19T10:16:05Z"},
    {"type": "observation", "source": "cmd_run", "content": "Server started on port 8000", "timestamp": "2025-04-19T10:17:30Z"},
    // Additional events...
  ],
  "feedback": {
    "user_rating": 5,
    "completion_time": 195,
    "token_usage": 4230
  }
}
```

### 2. Knowledge Base

```
/data/vortex/knowledge/
```

This directory contains structured knowledge in various formats:
- Markdown files for conceptual knowledge
- JSON files for structured data
- YAML files for configuration patterns
- Code snippets for common solutions

Example knowledge structure:
```
/data/vortex/knowledge/
  ├── programming/
  │   ├── python/
  │   │   ├── web_frameworks.md
  │   │   ├── common_patterns.json
  │   │   └── snippets/
  │   │       ├── flask_server.py
  │   │       └── fastapi_server.py
  │   └── javascript/
  │       └── ...
  ├── system/
  │   ├── linux_commands.md
  │   └── docker_patterns.yaml
  └── domains/
      ├── web_development.md
      └── data_science.md
```

### 3. Vector Database

For efficient semantic search, Vortex uses a vector database (like Chroma, Pinecone, or FAISS) to store embeddings of:
- Previous solutions
- Code snippets
- Documentation fragments
- User interactions

This enables rapid retrieval of relevant knowledge based on semantic similarity.

### 4. Configuration Storage

```
/data/vortex/configs/
```

Stores successful configuration patterns that can be reused for similar tasks.

## Continuous Learning

Vortex improves over time through several mechanisms:

### 1. Trajectory Analysis

After each task, Vortex can analyze the trajectory to:
- Identify successful action sequences
- Detect inefficient patterns
- Extract reusable components
- Update success metrics

This analysis is performed by the `TrajectoryAnalyzer` component:

```python
# In openhands/learning/trajectory_analyzer.py
class TrajectoryAnalyzer:
    def analyze(self, trajectory):
        """Analyze a trajectory and extract learnings."""
        patterns = self._extract_patterns(trajectory)
        self._update_knowledge_base(patterns)
        self._update_success_metrics(trajectory)
        return patterns
```

### 2. Feedback Integration

User feedback is systematically collected and integrated:
- Explicit ratings and comments
- Implicit signals (corrections, retries)
- Success/failure outcomes

The feedback is stored with the trajectory and used to improve future performance.

### 3. Knowledge Distillation

Periodically, Vortex can distill knowledge from multiple trajectories into:
- Updated prompt templates
- Refined system messages
- New code snippets
- Improved heuristics

### 4. Fine-tuning Support

For advanced deployments, Vortex supports fine-tuning of underlying models:
- Generating training data from successful trajectories
- Creating supervised fine-tuning datasets
- Exporting data for RLHF (Reinforcement Learning from Human Feedback)

## Memory Systems

Vortex implements several memory systems that work together:

### 1. Short-Term Memory

Implemented in the `State` class, this maintains the immediate context of the current task:
- Recent messages and actions
- Current working files
- Active goals and subgoals

```python
# In openhands/core/state.py
class State:
    def __init__(self):
        self.events = []
        self.current_iteration = 0
        self.working_files = {}
        self.goals = []
        # ...
```

### 2. Long-Term Memory

Persistent storage of knowledge that spans across sessions:
- Successful code patterns
- Common error solutions
- User preferences
- Domain knowledge

```python
# In openhands/memory/long_term.py
class LongTermMemory:
    def store(self, key, value, metadata=None):
        """Store information in long-term memory."""
        # ...
    
    def retrieve(self, query, limit=5):
        """Retrieve information from long-term memory."""
        # ...
```

### 3. Episodic Memory

Records of specific interactions that can be recalled when relevant:
- Previous solutions to similar problems
- User-specific interaction patterns
- Contextual preferences

```python
# In openhands/memory/episodic.py
class EpisodicMemory:
    def record_episode(self, episode):
        """Record a complete interaction episode."""
        # ...
    
    def recall_similar(self, current_state, limit=3):
        """Recall episodes similar to the current state."""
        # ...
```

### 4. Memory Condenser

As the context grows, the memory condenser summarizes less relevant information:
- Compresses older interactions
- Prioritizes key insights
- Maintains a balance between detail and context length

## Feedback Mechanisms

Vortex incorporates several feedback mechanisms to improve learning:

### 1. Explicit User Feedback

Users can provide direct feedback:
- Rating system (1-5 stars)
- Text comments
- Correction submissions

```toml
# In config.toml
[feedback]
enable_ratings = true
enable_comments = true
prompt_for_feedback = true
feedback_interval = 5  # Ask every 5 tasks
```

### 2. Implicit Feedback

The system also captures implicit feedback signals:
- Command corrections
- Repeated attempts
- Task completion time
- Resource usage efficiency

### 3. Automated Evaluation

Vortex can automatically evaluate its own performance:
- Code quality metrics
- Task completion verification
- Efficiency analysis
- Security compliance

## Configuration for Learning

To enable and configure learning capabilities, modify your `config.toml`:

```toml
[learning]
# Enable learning features
enable_learning = true

# Trajectory storage
store_trajectories = true
trajectory_path = "/data/vortex/trajectories"

# Knowledge base configuration
knowledge_base_path = "/data/vortex/knowledge"

# Vector database configuration
vector_db_type = "chroma"  # "chroma", "pinecone", "faiss"
vector_db_path = "/data/vortex/vectordb"

# Learning parameters
min_success_threshold = 0.7  # Minimum success rating to learn from
max_trajectories = 1000  # Maximum trajectories to store
analysis_interval = 10  # Analyze after every 10 tasks

# Feedback configuration
[learning.feedback]
enable_ratings = true
enable_comments = true
prompt_for_feedback = true
```

## Best Practices

To maximize learning and improvement over time:

### 1. Enable Trajectory Storage

Always enable trajectory storage to build a corpus of experiences:

```toml
[learning]
store_trajectories = true
```

### 2. Provide Explicit Feedback

After completing tasks, provide feedback on the solution:

```bash
# When using CLI
python -m openhands.cli --feedback "This solution was efficient and well-documented" --rating 5
```

### 3. Create Knowledge Collections

Organize related knowledge into collections:

```bash
# Create a new knowledge collection
python -m openhands.tools.knowledge create --name "python_web_development"

# Add an item to the collection
python -m openhands.tools.knowledge add --collection "python_web_development" --file flask_example.py
```

### 4. Analyze Learning Progress

Periodically review learning metrics:

```bash
# Generate learning report
python -m openhands.tools.learning report --last-days 30
```

### 5. Export and Import Knowledge

Share knowledge between deployments:

```bash
# Export knowledge
python -m openhands.tools.knowledge export --collection "python_web_development" --output knowledge.zip

# Import knowledge
python -m openhands.tools.knowledge import --input knowledge.zip
```

### 6. Configure Memory Parameters

Adjust memory parameters based on your use case:

```toml
[memory]
short_term_capacity = 100  # Number of events to keep in short-term memory
long_term_threshold = 0.7  # Minimum importance score to store in long-term memory
episodic_memory_limit = 500  # Maximum number of episodes to store
```

---

## Example: Learning Workflow

Here's an example of how learning works in practice:

1. **Task Execution**:
   - User submits a task: "Create a Flask API for a todo list"
   - Vortex executes the task, generating a solution
   - All actions and observations are recorded in the trajectory

2. **Feedback Collection**:
   - User provides a 5-star rating and positive comment
   - System records completion time and resource usage

3. **Knowledge Extraction**:
   - `TrajectoryAnalyzer` identifies reusable patterns in the Flask API implementation
   - Code snippets are extracted and stored in the knowledge base
   - Configuration patterns are saved for future use

4. **Memory Update**:
   - Long-term memory is updated with the successful pattern
   - Vector database is updated with embeddings of the solution
   - Episodic memory records the complete interaction

5. **Future Improvement**:
   - When a similar task is received: "Create a Flask API for a blog"
   - Vortex retrieves the relevant knowledge from previous todo list API
   - Solution is adapted and improved based on past experience
   - New trajectory further refines the knowledge

By following this continuous learning cycle, Vortex becomes more efficient and effective with each task it completes.