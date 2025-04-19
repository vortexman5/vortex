# Microagents System

Microagents are specialized prompts that enhance Vortex with domain-specific knowledge, repository-specific context, and task-specific workflows. They help by providing expert guidance, automating common tasks, and ensuring consistent practices across projects.

## Microagent Categories

Vortex supports three categories of microagents:

1. **Repository Microagents**: Provide repository-specific context and guidelines.
2. **Knowledge Microagents**: Contain domain-specific knowledge triggered by keywords.
3. **Task Microagents**: Guide users through interactive workflows with specific inputs.

## Microagent Format

All microagents use markdown files with YAML frontmatter that specify their behavior, triggers, and capabilities.

### Frontmatter Schema

Every microagent requires a YAML frontmatter section at the beginning of the file, enclosed by triple dashes (`---`). The fields are:

| Field      | Description                                        | Required                 | Used By          |
| ---------- | -------------------------------------------------- | ------------------------ | ---------------- |
| `name`     | Unique identifier for the microagent               | Yes                      | All types        |
| `type`     | Type of microagent: `repo`, `knowledge`, or `task` | Yes                      | All types        |
| `version`  | Version number (Semantic versioning recommended)   | Yes                      | All types        |
| `agent`    | The agent type (typically `CodeActAgent`)          | Yes                      | All types        |
| `author`   | Creator of the microagent                          | No                       | All types        |
| `triggers` | List of keywords that activate the microagent      | Yes for knowledge agents | Knowledge agents |
| `inputs`   | Defines required user inputs for task execution    | Yes for task agents      | Task agents      |

### Core Fields

#### `agent`

**Purpose**: Specifies which agent implementation processes the microagent (typically `CodeActAgent`).

- Defines a single agent responsible for processing the microagent
- Must be available in the Vortex system
- If the specified agent is not active, the microagent will not be used

#### `triggers`

**Purpose**: Defines keywords that activate the `knowledge` microagent.

**Example**:

```yaml
triggers:
  - kubernetes
  - k8s
  - docker
  - security
  - containers cluster
```

**Key points**:

- Can include both single words and multi-word phrases
- Case-insensitive matching is typically used
- More specific triggers (like "docker compose") prevent false activations
- Multiple triggers increase the chance of activation in relevant contexts
- Unique triggers like "flarglebargle" can be used for testing or special functionality

#### `inputs`

**Purpose**: Defines parameters required from the user when a `task` microagent is activated.

**Schema**:

```yaml
inputs:
  - name: INPUT_NAME # Used with {{ INPUT_NAME }}
    description: 'Description of what this input is for'
    required: true # Optional, defaults to true
```

**Key points**:

- The `name` and `description` properties are required for each input
- The `required` property is optional and defaults to `true`
- Input values are referenced in the microagent body using double curly braces (e.g., `{{ INPUT_NAME }}`)
- All inputs defined will be collected from the user before the task microagent executes

## Microagent Types

### Repository Microagent

Repository microagents provide context and guidelines for a specific repository.

- Located at: `.openhands/microagents/repo.md`
- Automatically loaded when working with the repository
- Only one per repository

The `Repository` microagent is loaded specifically from `.openhands/microagents/repo.md` and serves as the main repository-specific instruction file. This single file is automatically loaded whenever Vortex works with that repository without requiring any keyword matching or explicit call from the user.

### Knowledge Microagent

Knowledge microagents provide specialized domain expertise triggered by keywords.

- Located in the global microagents directory or a repository's `.openhands/microagents/` directory
- Activated when their triggers match keywords in the conversation
- Multiple knowledge microagents can be active simultaneously

### Task Microagent

Task microagents guide users through interactive workflows with specific inputs.

- Located in the global microagents directory or a repository's `.openhands/microagents/` directory
- Activated when explicitly requested by the user
- Collect required inputs from the user before execution

## Microagent Loading

Microagents are loaded from two primary locations:

1. **Global Microagents**: Loaded from the global microagents directory, typically containing public knowledge.
2. **User Workspace Microagents**: Loaded from a user's cloned repository or workspace directory.

When Vortex works with a repository, it:

1. Loads **repository-specific** microagents from `.openhands/microagents/` if present in the repository.
2. Loads **public knowledge** microagents triggered by keywords in conversations.
3. Loads **public tasks** microagents when explicitly requested by the user.

## Microagent Activation

Microagents are activated in different ways depending on their type:

1. **Repository Microagents**: Automatically loaded when working with a repository.
2. **Knowledge Microagents**: Activated when their triggers match keywords in the conversation.
3. **Task Microagents**: Activated when explicitly requested by the user.

## Best Practices for Creating Microagents

When creating microagents, follow these best practices:

1. **Clear Purpose**: Keep microagents focused with a clear purpose.
2. **Specific Guidelines**: Provide specific guidelines rather than general advice.
3. **Distinctive Triggers**: Use distinctive triggers for knowledge agents to prevent false activations.
4. **Concise Content**: Keep content concise to minimize context window usage.
5. **Modular Design**: Break large microagents into smaller, focused ones.
6. **Formatting**: Use markdown formatting to enhance readability and comprehension.
7. **Testing**: Test microagents with various inputs to ensure they work as expected.
8. **Documentation**: Document the purpose and usage of each microagent.

## Integration with Memory System

Microagents are tightly integrated with the Vortex Memory system:

1. The Memory system loads and manages microagents.
2. When a RecallAction event is received, the Memory system searches for matching microagent triggers.
3. If matches are found, the Memory system creates a RecallObservation with the microagent knowledge.
4. The RecallObservation is published to the EventStream for use by the agent.