# Vortex Architecture Overview

This document provides a detailed overview of the Vortex (OpenHands AI Framework) architecture, explaining how the various components work together to create a powerful AI agent system.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Event-Driven Communication](#event-driven-communication)
4. [Agent System](#agent-system)
5. [Runtime Environment](#runtime-environment)
6. [Memory System](#memory-system)
7. [LLM Integration](#llm-integration)
8. [Security Framework](#security-framework)
9. [Server Architecture](#server-architecture)
10. [Storage System](#storage-system)

## System Architecture

Vortex follows a modular, event-driven architecture designed to be flexible, extensible, and robust. The system is composed of several key components that communicate through a central event stream.

![System Architecture Diagram](../docs/static/img/system_architecture_overview.png)

The high-level architecture consists of:

1. **Agent Layer**: Responsible for decision-making and generating actions
2. **Controller Layer**: Manages the agent's state and execution flow
3. **Runtime Layer**: Executes actions in sandboxed environments
4. **Event System**: Facilitates communication between components
5. **Memory System**: Handles knowledge storage and retrieval
6. **LLM Layer**: Interfaces with language models
7. **Security Layer**: Enforces safety constraints
8. **Server Layer**: Provides HTTP/WebSocket interfaces for clients

## Core Components

### Agent

The `Agent` class is an abstract base class that defines the interface for all agent implementations. It is responsible for:

- Analyzing the current state
- Generating actions based on the state
- Processing observations from the runtime
- Maintaining execution status

Key methods:
- `step(state)`: Generates the next action based on the current state
- `get_system_message()`: Provides the system message for the agent
- `reset()`: Resets the agent's state

### AgentController

The `AgentController` class manages the agent's execution flow. It:

- Initializes the agent
- Manages the state
- Drives the main execution loop
- Handles errors and exceptions
- Manages delegation to other agents

Key methods:
- `_step()`: Executes a single step of the agent
- `on_event(event)`: Processes incoming events
- `_handle_action(event)`: Handles action events
- `_handle_observation(event)`: Handles observation events

### State

The `State` class represents the current state of the agent's task. It includes:

- History of events
- Current iteration count
- Agent state (RUNNING, FINISHED, ERROR, etc.)
- Metrics (token usage, cost, etc.)
- View of relevant events

### EventStream

The `EventStream` class serves as the central communication hub. It:

- Manages event subscriptions
- Distributes events to subscribers
- Persists events to storage
- Handles event serialization/deserialization

Key methods:
- `add_event(event, source)`: Adds an event to the stream
- `subscribe(subscriber_id, callback, callback_id)`: Registers a subscriber
- `unsubscribe(subscriber_id, callback_id)`: Removes a subscriber
- `get_events(start_id, end_id, reverse, filter_out_type, filter_hidden)`: Retrieves events

### Runtime

The `Runtime` class is responsible for executing actions and returning observations. It:

- Provides a sandboxed environment for execution
- Handles file operations
- Manages command execution
- Interfaces with browsers
- Executes Python code

Key methods:
- `run_action(action)`: Executes an action and returns an observation
- `connect()`: Establishes connection to the runtime environment
- `close()`: Cleans up resources

## Event-Driven Communication

Vortex uses an event-driven architecture where components communicate through events. This design provides:

- Loose coupling between components
- Asynchronous processing
- Extensibility through new event types
- Persistence of execution history

### Event Types

1. **Actions**: Events that represent something the agent wants to do
   - `MessageAction`: Sends a message
   - `CmdRunAction`: Executes a shell command
   - `FileReadAction`: Reads a file
   - `FileWriteAction`: Writes to a file
   - `BrowseURLAction`: Browses a URL
   - `AgentFinishAction`: Indicates task completion

2. **Observations**: Events that represent the results of actions
   - `CmdOutputObservation`: Output from a command
   - `FileReadObservation`: Content of a read file
   - `FileWriteObservation`: Result of a file write
   - `BrowserOutputObservation`: Output from browser interaction
   - `ErrorObservation`: Error information

### Event Flow

The typical event flow is:

1. Agent generates an Action
2. Action is added to the EventStream
3. Runtime subscribes to Actions and executes them
4. Runtime generates an Observation
5. Observation is added to the EventStream
6. Agent Controller processes the Observation
7. Agent Controller updates the State
8. Agent generates the next Action based on the updated State

## Agent System

### Agent Types

Vortex supports multiple agent types, each specialized for different tasks:

1. **Default Agent**: General-purpose agent for most tasks
2. **Browsing Agent**: Specialized for web browsing tasks
3. **Visual Browsing Agent**: Handles visual elements in web browsing
4. **CodeAct Agent**: Specialized for coding tasks

### Agent Registration

Agents are registered in a central registry, allowing dynamic selection:

```python
Agent.register("default", DefaultAgent)
Agent.register("browsing", BrowsingAgent)
```

### Agent Creation

Agents are created through a factory pattern:

```python
def create_agent(config: AppConfig) -> Agent:
    agent_type = config.get_agent_config().type
    agent_cls = Agent.get_cls(agent_type)
    llm = create_llm(config.llm)
    return agent_cls(llm, config.get_agent_config())
```

### Agent Delegation

Agents can delegate tasks to other agents:

1. Parent agent creates a `AgentDelegateAction`
2. Controller creates a delegate controller with the specified agent
3. Delegate agent processes the task
4. Results are returned to the parent agent

## Runtime Environment

### Runtime Types

Vortex supports multiple runtime environments:

1. **Local Runtime**: Executes actions on the local machine
2. **Docker Runtime**: Executes actions in a Docker container
3. **E2B Runtime**: Executes actions in an E2B sandbox

### Runtime Security

The runtime implements several security measures:

1. **Sandboxing**: Isolates execution in containers
2. **Resource Limits**: Restricts CPU, memory, and disk usage
3. **Command Filtering**: Blocks potentially dangerous commands
4. **Timeout Enforcement**: Limits execution time

### Runtime Plugins

The runtime can be extended with plugins:

1. **VSCode Plugin**: Provides code editing capabilities
2. **Jupyter Plugin**: Enables notebook functionality
3. **Browser Plugin**: Adds web browsing capabilities

## Memory System

### Short-Term Memory

The short-term memory system:

1. Filters the event stream for context
2. Provides a view of relevant events
3. Condenses history when context limits are reached

### Memory Condenser

The memory condenser:

1. Summarizes chunks of events
2. Prioritizes earlier events for summarization
3. Maintains a balance between detail and context length

### Microagents

Specialized components for knowledge retrieval:

1. **Knowledge Microagents**: Domain-specific knowledge
2. **Repo Microagents**: Repository-specific information

## LLM Integration

### LLM Abstraction

Vortex uses LiteLLM as an abstraction layer for different LLM providers:

1. **Claude Models**: Anthropic's Claude models
2. **OpenAI Models**: GPT-4, GPT-4o, etc.
3. **Google Models**: Gemini Pro, etc.

### Function Calling

The LLM integration supports function calling for structured outputs:

1. Function definitions are provided to the LLM
2. LLM generates structured function calls
3. Function calls are converted to Actions
4. Actions are executed by the Runtime

### Prompt Management

The system uses a prompt management system:

1. System messages define the agent's role and capabilities
2. Prompt templates are used for consistent formatting
3. Context management ensures efficient token usage

## Security Framework

### Security Analyzers

Vortex includes security analyzers that:

1. Analyze actions before execution
2. Block potentially dangerous operations
3. Enforce security policies

### Admin Mode

For advanced users, an admin mode is available that:

1. Bypasses security restrictions
2. Disables confirmation prompts
3. Allows unrestricted execution

### Confirmation Mode

When enabled, confirmation mode:

1. Prompts for user confirmation before executing certain actions
2. Provides details about the action to be executed
3. Allows rejection of potentially risky actions

## Server Architecture

### HTTP Server

The server component provides:

1. RESTful API endpoints
2. WebSocket connections for real-time updates
3. Static file serving for the frontend
4. Authentication and authorization

### Session Management

The server manages sessions:

1. Creates new sessions for users
2. Maintains session state
3. Cleans up expired sessions
4. Persists sessions to storage

### Conversation Manager

The conversation manager:

1. Creates and manages agent controllers
2. Handles user messages
3. Processes agent responses
4. Manages conversation history

## Storage System

### Storage Backends

Vortex supports multiple storage backends:

1. **Local Storage**: File-based local storage
2. **S3 Storage**: Amazon S3 compatible storage
3. **Google Cloud Storage**: Google Cloud backend
4. **In-Memory Storage**: Temporary storage

### Data Models

The storage system uses structured data models:

1. **Conversation**: Represents a conversation session
2. **Message**: Represents a message in a conversation
3. **File**: Represents a file in the system
4. **Settings**: Represents user or system settings

---

## Component Interaction Example

To illustrate how these components work together, here's a simplified example of the execution flow:

1. User sends a message: "Write a Python function to calculate Fibonacci numbers"
2. Server creates a `MessageAction` and adds it to the `EventStream`
3. `AgentController` receives the event and calls `agent.step(state)`
4. `Agent` analyzes the state and generates a `FileWriteAction` to create a Python file
5. `Runtime` executes the `FileWriteAction` and returns a `FileWriteObservation`
6. `Agent` receives the updated state and generates a `CmdRunAction` to test the code
7. `Runtime` executes the command and returns a `CmdOutputObservation`
8. `Agent` analyzes the output and generates a `MessageAction` with the result
9. Server sends the message to the user

This cycle continues until the task is completed or the user ends the session.

---

## Extending the Architecture

The modular design of Vortex makes it easy to extend:

1. **New Agent Types**: Create new agent classes for specialized tasks
2. **Custom Actions**: Define new action types for specific operations
3. **Runtime Plugins**: Add new runtime capabilities
4. **Microagents**: Create specialized knowledge components
5. **Storage Backends**: Implement new storage solutions

By understanding this architecture, developers can effectively customize and extend Vortex to meet their specific needs.