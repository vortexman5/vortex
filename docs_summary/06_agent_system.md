# Agent System

The Agent system is the core of the Vortex framework, providing the foundation for creating intelligent agents that can understand, learn, and improve over time. It defines the structure and behavior of agents, manages their execution, and coordinates their interaction with other components.

## Agent Architecture

The Agent architecture in Vortex follows an abstract base class pattern with a registry system for different agent types:

1. **Abstract Base Class**: Defines the common interface and behavior for all agents.
2. **Registry System**: Allows for registration and retrieval of different agent types.
3. **Execution Management**: Maintains execution status and history of interactions.
4. **Tool Management**: Provides methods for system message generation and tool management.

## CodeActAgent

The primary agent implementation in Vortex is the CodeActAgent, which implements the CodeAct idea that consolidates LLM agents' actions into a unified code action space for both simplicity and performance.

### Key Capabilities

The CodeActAgent can:

1. **Converse**: Communicate with humans in natural language to ask for clarification, confirmation, etc.
2. **CodeAct**: Choose to perform tasks by executing code:
   - Execute any valid Linux `bash` command
   - Execute any valid `Python` code with an interactive Python interpreter

### Implementation

The CodeActAgent is implemented as a subclass of the Agent abstract base class, with specialized methods for handling code execution and conversation:

```python
class CodeActAgent(Agent):
    def __init__(self, ...):
        # Initialize the agent with the specified parameters
        
    def generate_system_message(self):
        # Generate the system message for the agent
        
    async def step(self, input_message):
        # Process an input message and generate a response
        
    async def execute_code(self, code):
        # Execute code and return the result
```

## Agent Registry

The Agent registry system allows for registration and retrieval of different agent types:

1. **Registration**: Agents register themselves with the registry using a decorator or explicit registration method.
2. **Retrieval**: Agents can be retrieved from the registry by name or other criteria.
3. **Discovery**: The registry can discover available agents based on their capabilities.

```python
# Example of agent registration and retrieval
@Agent.register("code_act")
class CodeActAgent(Agent):
    # Agent implementation
    
# Retrieving an agent from the registry
agent = Agent.get_agent("code_act")
```

## Agent Execution

The Agent execution system manages the execution of agents:

1. **Initialization**: Agents are initialized with the necessary parameters.
2. **Step Execution**: Agents process input messages and generate responses through the `step` method.
3. **Status Tracking**: The execution status of agents is tracked to monitor their progress.
4. **History Management**: The history of interactions is maintained for context and debugging.

```python
# Example of agent execution
agent = Agent.get_agent("code_act")
response = await agent.step(input_message)
```

## Tool Management

Agents can use tools to extend their capabilities:

1. **Tool Registration**: Tools are registered with the agent during initialization.
2. **Tool Execution**: Agents can execute tools as part of their response generation.
3. **Tool Results**: The results of tool execution are incorporated into the agent's response.

```python
# Example of tool registration and execution
agent = Agent.get_agent("code_act")
agent.register_tool("calculator", calculator_tool)
response = await agent.step("Calculate 2 + 2")
```

## Integration with Other Components

The Agent system integrates with other Vortex components:

1. **Memory**: Agents can access and update memory to maintain context.
2. **LLM**: Agents use LLMs for reasoning and response generation.
3. **Reinforcement Learning**: Agents can improve through reinforcement learning.
4. **EventStream**: Agents communicate with other components through the EventStream.

## Agent Controller

The AgentController manages the execution of agents and coordinates their interaction with other components:

1. **Initialization**: Initializes agents with the necessary parameters.
2. **Execution**: Manages the execution of agents, including step execution and status tracking.
3. **Coordination**: Coordinates the interaction between agents and other components.
4. **Error Handling**: Handles errors that occur during agent execution.

```python
# Example of agent controller usage
controller = AgentController(agent)
response = await controller.process_message(input_message)
```

## Customization

The Agent system can be customized in several ways:

1. **Custom Agents**: Create specialized agents for specific domains or tasks.
2. **Custom Tools**: Implement custom tools to extend agent capabilities.
3. **Custom Execution**: Customize the execution flow for specialized use cases.
4. **Extended Registry**: Enhance the registry system with additional features.

## Best Practices

When working with the Agent system, follow these best practices:

1. **Agent Design**: Design agents with clear responsibilities and capabilities.
2. **Tool Integration**: Integrate tools that enhance the agent's capabilities.
3. **Error Handling**: Implement robust error handling for agent execution.
4. **Performance Optimization**: Optimize agent execution for performance.
5. **Testing**: Test agents with various inputs to ensure they work as expected.