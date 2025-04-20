# Getting Started with Vortex

This guide will help you get started with the Vortex framework, covering installation, configuration, and basic usage.

## Installation

### Prerequisites

Before installing Vortex, ensure you have the following prerequisites:

- Python 3.12 or higher (as specified in pyproject.toml)
- Poetry (recommended for dependency management)
- Docker (for the runtime environment)
- Git (for version control)

### Installation Methods

#### With Poetry (Recommended)

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone https://codeberg.org/Adamcatholic/vortex.git
   cd vortex
   ```

3. Install the dependencies:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

#### With Pip

1. Clone the repository:
   ```bash
   git clone https://codeberg.org/Adamcatholic/vortex.git
   cd vortex
   ```

2. Generate requirements.txt from Poetry dependencies:
   ```bash
   poetry export -f requirements.txt --output requirements.txt
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### With Docker

1. Pull the Docker image:
   ```bash
   docker pull docker.all-hands.dev/all-hands-ai/openhands:0.33
   ```

2. Set the required environment variables:
   ```bash
   export WORKSPACE_BASE=$(pwd)/workspace
   export LLM_MODEL="anthropic/claude-3-5-sonnet-20241022"
   export LLM_API_KEY="your_api_key_here"
   ```

## Configuration

### LLM Configuration

Configure the LLM integration by setting the following:

1. **LLM Provider**: Choose an LLM provider (e.g., OpenAI, Anthropic, Google).
2. **LLM Model**: Select a specific model (e.g., gpt-4, claude-3).
3. **API Key**: Provide the API key for the chosen provider.

```bash
export LLM_PROVIDER="anthropic"
export LLM_MODEL="anthropic/claude-3-5-sonnet-20241022"
export LLM_API_KEY="your_api_key_here"
```

### Runtime Configuration

Configure the runtime environment by setting the following:

1. **Workspace Base**: Specify the directory for the workspace.
2. **Runtime Container Image**: Choose the Docker image for the runtime.
3. **User ID**: Set the user ID for the runtime container.

```bash
export WORKSPACE_BASE=$(pwd)/workspace
export SANDBOX_RUNTIME_CONTAINER_IMAGE="docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik"
export SANDBOX_USER_ID=$(id -u)
```

## Running Vortex

### CLI Mode

To start an interactive Vortex session via the command line:

```bash
python -m openhands.core.cli
```

With Docker:

```bash
docker run -it \
    --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik \
    -e SANDBOX_USER_ID=$(id -u) \
    -e WORKSPACE_MOUNT_PATH=$WORKSPACE_BASE \
    -e LLM_API_KEY=$LLM_API_KEY \
    -e LLM_MODEL=$LLM_MODEL \
    -v $WORKSPACE_BASE:/opt/workspace_base \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app-$(date +%Y%m%d%H%M%S) \
    docker.all-hands.dev/all-hands-ai/openhands:0.33 \
    python -m openhands.core.cli
```

### GUI Mode

To start the Vortex GUI:

1. Run the Docker container:
   ```bash
   docker run -it \
       --pull=always \
       -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik \
       -e SANDBOX_USER_ID=$(id -u) \
       -e WORKSPACE_MOUNT_PATH=$WORKSPACE_BASE \
       -e LLM_API_KEY=$LLM_API_KEY \
       -e LLM_MODEL=$LLM_MODEL \
       -v $WORKSPACE_BASE:/opt/workspace_base \
       -v /var/run/docker.sock:/var/run/docker.sock \
       -v ~/.openhands-state:/.openhands-state \
       -p 3000:3000 \
       --add-host host.docker.internal:host-gateway \
       --name openhands-app-$(date +%Y%m%d%H%M%S) \
       docker.all-hands.dev/all-hands-ai/openhands:0.33
   ```

2. Access the GUI at [http://localhost:3000](http://localhost:3000).

## Basic Usage

### Interacting with Vortex

Once Vortex is running, you can interact with it by:

1. **Asking Questions**: Ask Vortex questions about code, programming concepts, or general knowledge.
2. **Requesting Code**: Ask Vortex to write code for specific tasks.
3. **Debugging Code**: Ask Vortex to help debug code issues.
4. **Exploring Repositories**: Ask Vortex to explore and explain code repositories.

### Example Interactions

#### Asking Questions

```
User: What is the difference between a list and a tuple in Python?
Vortex: Lists and tuples in Python are both sequence data types that can store collections of items, but they have key differences:

1. Mutability:
   - Lists are mutable (can be changed after creation)
   - Tuples are immutable (cannot be modified after creation)

2. Syntax:
   - Lists use square brackets: my_list = [1, 2, 3]
   - Tuples use parentheses: my_tuple = (1, 2, 3)

3. Methods:
   - Lists have more built-in methods (append, insert, remove, etc.)
   - Tuples have fewer methods due to immutability

4. Performance:
   - Tuples are slightly faster and use less memory
   - Lists have more overhead due to supporting mutation

5. Use cases:
   - Lists: when you need a collection that might change
   - Tuples: when you need an unchangeable collection, like coordinates or RGB values

6. Hashability:
   - Tuples (if they contain only immutable elements) can be used as dictionary keys
   - Lists cannot be used as dictionary keys

Example:
```python
# List - mutable
my_list = [1, 2, 3]
my_list[0] = 10  # Valid
my_list.append(4)  # Valid

# Tuple - immutable
my_tuple = (1, 2, 3)
my_tuple[0] = 10  # Error! Tuples cannot be modified
```
```

#### Requesting Code

```
User: Can you write a Python function to calculate the Fibonacci sequence up to n terms?
Vortex: Here's a Python function to calculate the Fibonacci sequence up to n terms:

```python
def fibonacci_sequence(n):
    """
    Generate the Fibonacci sequence up to n terms.
    
    Args:
        n (int): Number of terms to generate
        
    Returns:
        list: Fibonacci sequence with n terms
    """
    # Handle edge cases
    if n <= 0:
        return []
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]
    
    # Initialize the sequence with the first two terms
    fib_sequence = [0, 1]
    
    # Generate the remaining terms
    for i in range(2, n):
        # Next number is the sum of the previous two
        next_number = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_number)
    
    return fib_sequence

# Example usage
if __name__ == "__main__":
    n_terms = 10
    result = fibonacci_sequence(n_terms)
    print(f"Fibonacci sequence with {n_terms} terms:")
    print(result)
```

This function:
1. Handles edge cases (n ≤ 0, n = 1, n = 2)
2. Initializes the sequence with the first two Fibonacci numbers (0 and 1)
3. Iteratively calculates each subsequent number by adding the previous two
4. Returns the complete sequence as a list

The time complexity is O(n) and space complexity is also O(n).

You can test it with different values of n to generate Fibonacci sequences of different lengths.
```

## Working with Microagents

Vortex supports microagents for specialized knowledge and tasks:

### Using Knowledge Microagents

Knowledge microagents are automatically triggered by keywords in your conversation:

```
User: What are the best practices for Kubernetes security?
Vortex: [Triggered by "kubernetes" and "security" keywords]

# Kubernetes Security Best Practices

Here are key security best practices for Kubernetes deployments:

## Pod Security
- Use Pod Security Standards (PSS) or Pod Security Policies (PSP)
- Limit pod capabilities with securityContext
- Run containers as non-root users
- Use read-only root filesystems
- Implement pod security admission controllers

## Authentication & Authorization
- Use RBAC (Role-Based Access Control) for all access
- Follow principle of least privilege
- Implement strong authentication mechanisms
- Regularly audit and rotate credentials
- Use service accounts with minimal permissions

## Network Security
- Implement network policies to restrict pod-to-pod communication
- Use TLS for all communication
- Consider service mesh for advanced traffic management
- Isolate sensitive workloads in dedicated namespaces

## Image Security
- Use minimal, trusted base images
- Scan images for vulnerabilities
- Implement image signing and verification
- Use private registries with access controls
- Never use :latest tags in production

## Cluster Configuration
- Enable audit logging
- Encrypt etcd data at rest
- Regularly update and patch Kubernetes
- Use separate clusters for different security domains
- Implement node security hardening

## Secrets Management
- Never store secrets in ConfigMaps or environment variables
- Use a dedicated secrets management solution
- Encrypt secrets at rest
- Limit access to secrets
- Rotate secrets regularly

Would you like me to elaborate on any specific area of Kubernetes security?
```

### Using Task Microagents

Task microagents are explicitly requested and guide you through specific workflows:

```
User: Can you help me set up a CI/CD pipeline for my project?
Vortex: I'd be happy to help you set up a CI/CD pipeline for your project. I'll use the CI/CD Setup microagent to guide you through the process.

# CI/CD Pipeline Setup

To set up an effective CI/CD pipeline, I'll need some information about your project:

1. What is your project's programming language or framework?
2. Which version control system are you using (GitHub, GitLab, Bitbucket, etc.)?
3. What kind of deployment environment are you targeting (cloud provider, on-premises, etc.)?
4. Do you have any specific CI/CD tools in mind (Jenkins, GitHub Actions, GitLab CI, CircleCI, etc.)?
5. What testing requirements do you have (unit tests, integration tests, etc.)?

Once you provide this information, I can help you create a customized CI/CD pipeline configuration.
```

## Next Steps

After getting started with Vortex, you can explore more advanced features:

1. **Custom Microagents**: Create your own microagents for specialized knowledge and tasks.
2. **Reinforcement Learning**: Use the RL system to improve agent performance over time.
3. **Custom Runtime**: Configure a custom runtime environment for specific needs.
4. **Integration**: Integrate Vortex with other systems and workflows.

For more information, refer to the detailed documentation on each component of the Vortex framework.