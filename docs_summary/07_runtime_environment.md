# Runtime Environment

The Vortex Runtime Environment provides a secure and flexible execution environment for AI agents. It creates a sandboxed environment using Docker, where arbitrary code can be run safely without risking the host system.

## Why a Sandboxed Runtime?

Vortex needs to execute arbitrary code in a secure, isolated environment for several reasons:

1. **Security**: Executing untrusted code can pose significant risks to the host system. A sandboxed environment prevents malicious code from accessing or modifying the host system's resources.
2. **Consistency**: A sandboxed environment ensures that code execution is consistent across different machines and setups, eliminating "it works on my machine" issues.
3. **Resource Control**: Sandboxing allows for better control over resource allocation and usage, preventing runaway processes from affecting the host system.
4. **Isolation**: Different projects or users can work in isolated environments without interfering with each other or the host system.
5. **Reproducibility**: Sandboxed environments make it easier to reproduce bugs and issues, as the execution environment is consistent and controllable.

## Runtime Architecture

The Vortex Runtime system uses a client-server architecture implemented with Docker containers:

```
User-provided Custom Docker Image
        |
        v
   OpenHands Backend
        |
        v
   OH Runtime Image
        |
        v
   Action Executor
        |
   _____|_____
  |     |     |
  v     v     v
Browser Bash Plugins
              |
              v
        Jupyter Server
```

1. **User Input**: The user provides a custom base Docker image.
2. **Image Building**: Vortex builds a new Docker image (the "OH runtime image") based on the user-provided image. This new image includes Vortex-specific code, primarily the "runtime client".
3. **Container Launch**: When Vortex starts, it launches a Docker container using the OH runtime image.
4. **Action Execution Server Initialization**: The action execution server initializes an `ActionExecutor` inside the container, setting up necessary components like a bash shell and loading any specified plugins.
5. **Communication**: The Vortex backend communicates with the action execution server over RESTful API, sending actions and receiving observations.
6. **Action Execution**: The runtime client receives actions from the backend, executes them in the sandboxed environment, and sends back observations.
7. **Observation Return**: The action execution server sends execution results back to the Vortex backend as observations.

## Runtime Client

The runtime client plays a crucial role in the Vortex Runtime system:

1. **Intermediary**: Acts as an intermediary between the Vortex backend and the sandboxed environment.
2. **Action Execution**: Executes various types of actions (shell commands, file operations, Python code, etc.) safely within the container.
3. **State Management**: Manages the state of the sandboxed environment, including the current working directory and loaded plugins.
4. **Observation Formatting**: Formats and returns observations to the backend, ensuring a consistent interface for processing results.

## Image Tagging System

Vortex uses a three-tag system for its runtime images to balance reproducibility with flexibility:

1. **Versioned Tag**: `oh_v{openhands_version}_{base_image}` (e.g., `oh_v0.9.9_nikolaik_s_python-nodejs_t_python3.12-nodejs22`)
2. **Lock Tag**: `oh_v{openhands_version}_{16_digit_lock_hash}` (e.g., `oh_v0.9.9_1234567890abcdef`)
3. **Source Tag**: `oh_v{openhands_version}_{16_digit_lock_hash}_{16_digit_source_hash}` (e.g., `oh_v0.9.9_1234567890abcdef_1234567890abcdef`)

### Build Process

When generating an image, Vortex follows a sophisticated process to optimize build time:

1. **No re-build**: If an image with the same specific source tag exists, no build is performed - the existing image is used.
2. **Fastest re-build**: If an image with the generic lock tag exists, Vortex builds a new image based upon it, bypassing all installation steps except copying the current source code.
3. **Ok-ish re-build**: If neither a source nor lock tag exists, an image will be built based upon the versioned tag image.
4. **Slowest re-build**: If all three tags don't exist, a brand new image is built based upon the base image.

This tagging approach allows Vortex to efficiently manage both development and production environments.

## Runtime Plugin System

The Vortex Runtime supports a plugin system that allows for extending functionality and customizing the runtime environment:

1. **Plugin Definition**: Plugins are defined as Python classes that inherit from a base `Plugin` class.
2. **Plugin Registration**: Available plugins are registered in an `ALL_PLUGINS` dictionary.
3. **Plugin Specification**: Plugins are associated with `Agent.sandbox_plugins: list[PluginRequirement]`. Users can specify which plugins to load when initializing the runtime.
4. **Initialization**: Plugins are initialized asynchronously when the runtime client starts.
5. **Usage**: The runtime client can use initialized plugins to extend its capabilities (e.g., the JupyterPlugin for running IPython cells).

## Access Modes

Vortex provides several access modes for interacting with the runtime:

### CLI Mode

The CLI mode allows users to start an interactive session via the command line:

```bash
poetry run python -m openhands.core.cli
```

This command starts an interactive session where users can input tasks and receive responses from Vortex.

### GUI Mode

The GUI mode provides a graphical user interface for interacting with Vortex:

1. **Chat Panel**: Displays the conversation between the user and Vortex.
2. **Workspace**: Allows browsing project files and directories.
3. **Jupyter**: Shows all Python commands executed by Vortex.
4. **App**: Shows the web server when Vortex runs an application.
5. **Browser**: Used by Vortex to browse websites.
6. **Terminal**: A space for Vortex and users to run terminal commands.

### Headless Mode

The headless mode is non-interactive and better for scripting, allowing Vortex to be integrated into automated workflows.

## Security Considerations

The Vortex Runtime includes several security features:

1. **Container Isolation**: Code execution is isolated within Docker containers.
2. **Resource Limits**: Containers have resource limits to prevent resource exhaustion.
3. **Network Isolation**: Containers have limited network access.
4. **File System Isolation**: Containers have limited access to the host file system.
5. **User Permissions**: Containers run with restricted user permissions.

## Customization

The Runtime environment can be customized in several ways:

1. **Custom Base Images**: Use custom Docker images as the base for the runtime.
2. **Custom Plugins**: Implement custom plugins to extend runtime capabilities.
3. **Resource Configuration**: Configure resource limits for containers.
4. **Network Configuration**: Configure network access for containers.
5. **Volume Mounting**: Configure volume mounting for containers.