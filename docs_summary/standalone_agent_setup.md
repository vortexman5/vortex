# Setting Up Vortex as a Standalone Agent with Full Capabilities

This guide provides comprehensive instructions for setting up Vortex as a standalone agent with full capabilities and no restrictions. This setup is intended for advanced users who understand the implications of running an AI agent with unrestricted capabilities.

## Prerequisites

- A Linux-based system (Ubuntu 22.04+ or Linux Mint 21+ recommended)
- At least 32GB RAM
- At least 100GB free disk space
- NVIDIA GPU with at least 8GB VRAM (for local LLM hosting)
- Python 3.10+
- Docker and Docker Compose
- Git

## Step 1: Clone the Vortex Repository

```bash
git clone https://codeberg.org/Adamcatholic/vortex.git
cd vortex
```

## Step 2: Set Up the Environment

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Configure the Database

Vortex requires a PostgreSQL database for knowledge storage and agent memory:

```bash
# Install PostgreSQL if not already installed
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create a database and user for Vortex
sudo -u postgres psql -c "CREATE USER vortex WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE vortex_db OWNER vortex;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vortex_db TO vortex;"

# Enable extensions
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d vortex_db -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

Create a `.env` file in the project root with the following content:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vortex_db
DB_USER=vortex
DB_PASSWORD=your_secure_password
```

## Step 4: Set Up the LLM Backend

### Option 1: Use a Local LLM (Recommended for Full Autonomy)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a powerful model (adjust based on your GPU capabilities)
ollama pull mistral:latest
ollama pull llama3:70b
```

Update the `.env` file to include:

```
LLM_PROVIDER=ollama
LLM_MODEL=llama3:70b
LLM_HOST=http://localhost:11434
```

### Option 2: Use an API-based LLM

If you prefer to use an API-based LLM like OpenAI, update the `.env` file:

```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=your_api_key
```

## Step 5: Configure Agent Capabilities

To set up Vortex with full capabilities and no restrictions, create a `config.yaml` file in the project root:

```yaml
agent:
  name: Vortex
  description: "Autonomous AI agent with full capabilities"
  version: "1.0.0"
  
  # Set to true to enable full autonomy
  autonomous_mode: true
  
  # Remove restrictions on capabilities
  restrictions:
    enabled: false
    
  # Enable all capabilities
  capabilities:
    file_system:
      enabled: true
      unrestricted: true
    network:
      enabled: true
      unrestricted: true
    process_execution:
      enabled: true
      unrestricted: true
    system_access:
      enabled: true
      unrestricted: true
      
  # Memory configuration
  memory:
    long_term_enabled: true
    short_term_capacity: 100
    
  # Microagents configuration
  microagents:
    enabled: true
    auto_creation: true
    
  # Learning configuration
  learning:
    enabled: true
    reinforcement_learning: true
    knowledge_acquisition: true
```

## Step 6: Set Up Knowledge Ingestion

To enable Vortex to ingest knowledge from various sources:

1. Create a knowledge directory:

```bash
mkdir -p knowledge/books
mkdir -p knowledge/documentation
mkdir -p knowledge/websites
```

2. Add the knowledge ingestion script:

```bash
cp scripts/ingest_knowledge.py .
```

3. Run the knowledge ingestion process:

```bash
# For PDF books
python ingest_knowledge.py --source knowledge/books --type pdf

# For documentation
python ingest_knowledge.py --source knowledge/documentation --type markdown

# For websites
python ingest_knowledge.py --source knowledge/websites --type url
```

## Step 7: Start the Vortex Agent

```bash
# Start the agent in autonomous mode
python run_agent.py --autonomous
```

## Step 8: Interact with the Agent

You can interact with the agent through various interfaces:

1. **CLI Interface**:
   ```bash
   python cli.py
   ```

2. **Web Interface**:
   ```bash
   python web_interface.py
   ```
   Then open your browser to http://localhost:8000

3. **API Interface**:
   ```bash
   python api_server.py
   ```
   The API will be available at http://localhost:5000

## Advanced Configuration

### Enabling Continuous Learning

To enable continuous learning, add the following to your `config.yaml`:

```yaml
learning:
  enabled: true
  continuous: true
  feedback_collection: true
  model_fine_tuning: true
  knowledge_base_updates: true
```

### Setting Up Autonomous Decision Making

For fully autonomous decision making:

```yaml
autonomy:
  enabled: true
  decision_making: true
  goal_setting: true
  self_improvement: true
  resource_management: true
```

### Configuring External Tool Access

To give Vortex access to external tools:

```yaml
tools:
  enabled: true
  browser_access: true
  code_execution: true
  api_access: true
  system_commands: true
  allowed_commands: "*"  # Allow all commands
```

## Security Considerations

Running Vortex with full capabilities and no restrictions has significant security implications:

1. The agent will have unrestricted access to your system
2. It can execute any command with the permissions of the user running it
3. It can access the network and make API calls
4. It can read and write any files accessible to the user

**Recommendations:**

1. Run Vortex in a dedicated user account with appropriate permissions
2. Consider using a virtual machine or container for isolation
3. Monitor the agent's activities closely
4. Implement a kill switch mechanism for emergency shutdown

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Verify database connectivity
3. Ensure the LLM backend is running properly
4. Check system resources (memory, disk space)

## Conclusion

You now have a fully autonomous Vortex agent with unrestricted capabilities. This setup allows Vortex to operate at its full potential, learning from its environment, making autonomous decisions, and executing actions without artificial limitations.

Remember that with great power comes great responsibility. Monitor your agent's activities and ensure it operates within ethical and legal boundaries.