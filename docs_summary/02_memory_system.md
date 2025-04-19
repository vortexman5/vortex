# Memory System

The Vortex Memory System is a sophisticated component responsible for managing knowledge retrieval, storage, and optimization. It enables agents to recall relevant information, maintain context, and efficiently manage their knowledge base.

## Core Components

### Memory Class

The `Memory` class is the central component of the memory system, responsible for:

1. **Event Handling**: Listens to the EventStream for RecallAction events and publishes RecallObservation responses.
2. **Workspace Context Recall**: Provides repository and runtime information when a workspace context recall is requested.
3. **Knowledge Recall**: Retrieves information from microagents based on triggers in user or agent messages.
4. **Microagent Management**: Loads and manages both global and user workspace microagents.

```python
# Key methods in the Memory class
def _on_workspace_context_recall(self, event: RecallAction) -> RecallObservation | None:
    # Collects repository info, runtime info, and microagent knowledge
    
def _on_microagent_recall(self, event: RecallAction) -> RecallObservation | None:
    # Finds and returns knowledge from triggered microagents
    
def _find_microagent_knowledge(self, query: str) -> list[MicroagentKnowledge]:
    # Searches for microagent triggers in the query
    
def load_user_workspace_microagents(self, user_microagents: list[BaseMicroagent]) -> None:
    # Loads microagents from a user's cloned repo or workspace directory
```

### Amortized Forgetting Condenser

The `AmortizedForgettingCondenser` is a specialized component that manages the size of the event history to prevent performance degradation:

1. **Event History Management**: Maintains a condensed history of events, forgetting old events when the history grows too large.
2. **Selective Retention**: Keeps important events (like the first few interactions) while condensing the rest.
3. **Efficient Memory Usage**: Ensures the agent's memory doesn't grow unbounded, which would impact performance.

```python
# Key methods in the AmortizedForgettingCondenser
def get_condensation(self, view: View) -> Condensation:
    # Creates a condensation action that specifies which events to forget
    
def should_condense(self, view: View) -> bool:
    # Determines if the event history needs to be condensed
```

## Microagent System

Microagents are specialized knowledge modules that can be triggered by specific keywords or queries:

### Types of Microagents

1. **Repository Microagents**: Provide repository-specific context and guidelines.
2. **Knowledge Microagents**: Contain domain-specific knowledge triggered by keywords.
3. **Task Microagents**: Guide users through interactive workflows with specific inputs.

### Microagent Loading

Microagents are loaded from two primary locations:

1. **Global Microagents**: Loaded from the global microagents directory, typically containing public knowledge.
2. **User Workspace Microagents**: Loaded from a user's cloned repository or workspace directory.

```python
def _load_global_microagents(self) -> None:
    # Loads microagents from the global microagents directory
    repo_agents, knowledge_agents, _ = load_microagents_from_dir(GLOBAL_MICROAGENTS_DIR)
```

## Knowledge Retrieval Process

The knowledge retrieval process follows these steps:

1. A `RecallAction` event is published to the EventStream.
2. The Memory system receives the event and determines its type (workspace context or knowledge recall).
3. For workspace context recall, repository information, runtime information, and relevant microagent knowledge are collected.
4. For knowledge recall, microagents with triggers matching the query are identified.
5. A `RecallObservation` containing the retrieved information is published back to the EventStream.

## Memory Optimization

To maintain performance, the memory system employs several optimization strategies:

1. **Amortized Forgetting**: Periodically condenses the event history to prevent unbounded growth.
2. **Selective Microagent Activation**: Only activates microagents when their triggers match the current context.
3. **Efficient Storage**: Organizes microagents by type for faster retrieval.

## Integration with Other Components

The Memory system integrates with other Vortex components:

1. **EventStream**: Communicates with other components through events.
2. **Agent**: Provides relevant knowledge to the agent during decision-making.
3. **Runtime**: Receives runtime information to include in workspace context.

## Customization

The Memory system can be customized in several ways:

1. **Custom Microagents**: Create specialized microagents for specific domains or tasks.
2. **Alternative Condensers**: Implement custom condensers with different forgetting strategies.
3. **Extended Repository Information**: Add additional repository-specific information to enhance context.