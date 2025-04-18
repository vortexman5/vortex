# LLM Options for Coding: Commercial APIs and Local Server Setup

This guide provides detailed information on commercial LLM APIs for coding tasks and instructions for setting up a local LLM server optimized for your hardware specifications.

## 1. Commercial LLM APIs for Coding

### 1.1 OpenAI Codex/GPT-4

**API Details:**
- **Provider:** OpenAI
- **Models:** GPT-4o, GPT-4 Turbo
- **Pricing:** $0.01-$0.03 per 1K input tokens, $0.03-$0.06 per 1K output tokens
- **Free Tier:** None currently available
- **API Documentation:** [OpenAI API Docs](https://platform.openai.com/docs/api-reference)

**Example API Call:**
```python
import openai

client = openai.OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a coding assistant specialized in Python."},
        {"role": "user", "content": "Write a function to calculate the Fibonacci sequence."}
    ]
)

print(response.choices[0].message.content)
```

**Integration with Vortex/OpenHands:**
```toml
# In config.toml
[llm]
provider = "openai"
model = "gpt-4o"
api_key = "your-openai-api-key"
```

### 1.2 Anthropic Claude

**API Details:**
- **Provider:** Anthropic
- **Models:** Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- **Pricing:** $0.003-$0.015 per 1K input tokens, $0.015-$0.075 per 1K output tokens
- **Free Tier:** None currently available
- **API Documentation:** [Anthropic API Docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

**Example API Call:**
```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    system="You are a coding assistant specialized in JavaScript.",
    messages=[
        {"role": "user", "content": "Write a function to sort an array of objects by a specific property."}
    ]
)

print(message.content)
```

**Integration with Vortex/OpenHands:**
```toml
# In config.toml
[llm]
provider = "anthropic"
model = "claude-3-sonnet-20240229"
api_key = "your-anthropic-api-key"
```

### 1.3 Google Gemini

**API Details:**
- **Provider:** Google
- **Models:** Gemini 1.5 Pro, Gemini 1.5 Flash
- **Pricing:** $0.0025-$0.0075 per 1K input tokens, $0.0075-$0.0225 per 1K output tokens
- **Free Tier:** Limited free tier available (monthly token quota)
- **API Documentation:** [Google AI Studio](https://ai.google.dev/docs)

**Example API Call:**
```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")

model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(
    "Write a function in Java to check if a string is a palindrome."
)

print(response.text)
```

**Integration with Vortex/OpenHands:**
```toml
# In config.toml
[llm]
provider = "google"
model = "gemini-1.5-pro"
api_key = "your-google-api-key"
```

### 1.4 Cohere

**API Details:**
- **Provider:** Cohere
- **Models:** Command, Command Light, Command R+
- **Pricing:** $0.50-$2.00 per million input tokens, $0.50-$5.00 per million output tokens
- **Free Tier:** Limited free tier available (limited monthly requests)
- **API Documentation:** [Cohere API Docs](https://docs.cohere.com/reference/about)

**Example API Call:**
```python
import cohere

co = cohere.Client('your-api-key')

response = co.generate(
    model='command',
    prompt='Write a function in C++ to find the greatest common divisor of two numbers.',
    max_tokens=500
)

print(response.generations[0].text)
```

**Integration with Vortex/OpenHands:**
```toml
# In config.toml (requires custom adapter)
[llm]
provider = "cohere"
model = "command"
api_key = "your-cohere-api-key"
```

## 2. Local LLM Server Setup for Your Hardware

Based on your hardware specifications (AMD A9-9410 dual-core CPU, 8GB RAM, AMD Radeon R5 Graphics), here are optimized instructions for setting up a local LLM server for coding tasks.

### 2.1 Hardware Assessment

Your system has:
- Dual-core AMD A9-9410 CPU
- 8GB RAM (with 2GB swap)
- AMD Radeon R5 Graphics (not CUDA-compatible)
- 223GB SSD with ~97GB free space

This hardware is suitable for running smaller quantized models (1B-3B parameters). For optimal performance, we'll focus on efficient models that can run on CPU.

### 2.2 Installing Ollama

Ollama is a lightweight tool for running LLMs locally that works well on modest hardware.

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### 2.3 Pulling Optimized Models for Coding

For your hardware, these models are recommended:

```bash
# Pull CodeLlama 7B quantized (most efficient coding model for your hardware)
ollama pull codellama:7b-q4_0

# Pull Phi-3 Mini (excellent performance-to-size ratio)
ollama pull phi3:mini

# Pull TinyLlama (very lightweight option)
ollama pull tinyllama:1.1b-chat-v1.0-q4_0
```

### 2.4 Setting Up Ollama Server

```bash
# Start Ollama server
ollama serve

# In a new terminal, test the server
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "codellama:7b-q4_0",
  "prompt": "Write a Python function to check if a number is prime."
}'
```

### 2.5 Creating a Custom Model with Coding Focus

Create a Modelfile to customize a model for coding:

```bash
# Create a directory for your custom model
mkdir -p ~/ollama-models
cd ~/ollama-models

# Create a Modelfile
cat > Modelfile << 'EOF'
FROM codellama:7b-q4_0

# System prompt to focus on coding
SYSTEM """
You are an expert coding assistant. You write clean, efficient, and well-documented code.
Focus on providing practical solutions with proper error handling.
Explain your code when it would be helpful.
"""

# Set parameters for better performance on your hardware
PARAMETER temperature 0.7
PARAMETER num_ctx 2048
EOF

# Create the custom model
ollama create coding-assistant -f Modelfile

# Test your custom model
ollama run coding-assistant "Write a function to convert a string to camelCase in JavaScript"
```

### 2.6 Setting Up a REST API Server

For integration with Vortex/OpenHands, we'll set up a simple REST API server:

```bash
# Install required packages
pip install fastapi uvicorn pydantic

# Create a server script
cat > ollama_server.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
import json

app = FastAPI(title="Local LLM API Server")

class CompletionRequest(BaseModel):
    model: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 1024

class Message(BaseModel):
    role: str
    content: str

@app.post("/v1/chat/completions")
async def create_completion(request: CompletionRequest):
    try:
        # Convert to Ollama format
        prompt = ""
        for msg in request.messages:
            if msg.role == "system":
                prompt = f"<s>[INST] {msg.content} [/INST]"
            elif msg.role == "user":
                prompt += f"\n\n[INST] {msg.content} [/INST]"
            elif msg.role == "assistant":
                prompt += f"\n{msg.content}"
        
        # Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": request.model,
                    "prompt": prompt,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ollama API error")
            
            result = response.json()
            
            # Format response like OpenAI
            return {
                "id": "local-completion",
                "object": "chat.completion",
                "created": 0,
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result.get("response", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create a systemd service for auto-start
cat > ollama-api.service << 'EOF'
[Unit]
Description=Ollama API Server
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/ollama_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Replace YOUR_USERNAME with your actual username
sed -i "s/YOUR_USERNAME/$USER/g" ollama-api.service

# Install the service
sudo mv ollama-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ollama-api
sudo systemctl start ollama-api

# Check status
sudo systemctl status ollama-api
```

### 2.7 Performance Optimization for Your Hardware

```bash
# Create a script to optimize system for LLM inference
cat > optimize_for_llm.sh << 'EOF'
#!/bin/bash

# Disable unnecessary services
systemctl --user stop tracker-store.service tracker-miner-fs.service tracker-miner-apps.service tracker-extract.service
systemctl --user mask tracker-store.service tracker-miner-fs.service tracker-miner-apps.service tracker-extract.service

# Set CPU governor to performance when running LLMs
sudo cpufreq-set -g performance

# Increase swap if needed
CURRENT_SWAP=$(free -m | awk '/^Swap:/ {print $2}')
if [ $CURRENT_SWAP -lt 4096 ]; then
    echo "Increasing swap space to 4GB..."
    sudo swapoff -a
    sudo dd if=/dev/zero of=/swapfile bs=1G count=4
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
fi

# Set process priority for Ollama
sudo renice -n -10 -p $(pgrep ollama)
sudo ionice -c 2 -n 0 -p $(pgrep ollama)

echo "System optimized for LLM inference"
EOF

# Make the script executable
chmod +x optimize_for_llm.sh

# Run the optimization script
./optimize_for_llm.sh
```

## 3. Integrating with Vortex/OpenHands Framework

### 3.1 Configure Vortex to Use Local LLM Server

Edit your `config.toml` file to use the local LLM server:

```toml
[llm]
provider = "openai"  # We're using the OpenAI-compatible API format
base_url = "http://localhost:8000/v1"  # Point to our local server
api_key = "dummy-key"  # Not used but required
model = "coding-assistant"  # The model name we created in Ollama
```

### 3.2 Testing the Integration

Create a test script to verify the integration:

```bash
# Create a test script
cat > test_local_llm.py << 'EOF'
import requests
import json

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
data = {
    "model": "coding-assistant",
    "messages": [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Write a simple Python function to calculate factorial."}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(json.dumps(response.json(), indent=2))
EOF

# Run the test
python3 test_local_llm.py
```

### 3.3 Monitoring Resource Usage

Create a monitoring script to ensure your system can handle the LLM:

```bash
# Create a monitoring script
cat > monitor_llm.sh << 'EOF'
#!/bin/bash

echo "Monitoring system resources for LLM usage..."
echo "Press Ctrl+C to exit"

while true; do
    clear
    echo "=== CPU Usage ==="
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "CPU Usage: " 100 - $1 "%"}'
    
    echo -e "\n=== Memory Usage ==="
    free -h | grep "Mem:"
    
    echo -e "\n=== Swap Usage ==="
    free -h | grep "Swap:"
    
    echo -e "\n=== Ollama Process ==="
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 2
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep ollama
    
    sleep 2
done
EOF

# Make the script executable
chmod +x monitor_llm.sh
```

## 4. Model Recommendations for Your Hardware

Based on your specific hardware (AMD A9-9410, 8GB RAM), here are the recommended models for coding tasks:

1. **CodeLlama 7B (4-bit quantized)** - Best balance of performance and resource usage
   - Memory usage: ~4GB RAM
   - Disk space: ~4GB
   - Performance: Good for most coding tasks

2. **Phi-3 Mini** - Microsoft's efficient model
   - Memory usage: ~2.5GB RAM
   - Disk space: ~2GB
   - Performance: Surprisingly good for its size

3. **TinyLlama 1.1B** - Ultra-lightweight option
   - Memory usage: ~1GB RAM
   - Disk space: ~600MB
   - Performance: Basic coding assistance, best for simple tasks

4. **StarCoder 1B** - Specialized for coding
   - Memory usage: ~1.5GB RAM
   - Disk space: ~1GB
   - Performance: Good for code completion

## 5. Troubleshooting

### 5.1 Out of Memory Issues

If you encounter out-of-memory errors:

```bash
# Reduce model context length
ollama pull codellama:7b-q4_0
cat > Modelfile << 'EOF'
FROM codellama:7b-q4_0
PARAMETER num_ctx 1024  # Reduced from default
EOF
ollama create coding-assistant-light -f Modelfile
```

### 5.2 Slow Response Times

If responses are too slow:

```bash
# Use a smaller model
ollama pull tinyllama:1.1b-chat-v1.0-q4_0

# Update your config.toml
# [llm]
# model = "tinyllama:1.1b-chat-v1.0-q4_0"
```

### 5.3 API Connection Issues

If Vortex can't connect to the local API:

```bash
# Check if the API server is running
curl http://localhost:8000/health

# Restart the API server
sudo systemctl restart ollama-api

# Check logs for errors
sudo journalctl -u ollama-api -n 50
```

## 6. Conclusion

This guide provides both commercial API options and a local LLM server setup optimized for your specific hardware. The local setup is designed to work within the constraints of your AMD A9-9410 CPU and 8GB RAM while still providing useful coding assistance.

For the best experience on your hardware:
1. Use the CodeLlama 7B 4-bit quantized model for most coding tasks
2. Keep the context window small (1024-2048 tokens)
3. Close other memory-intensive applications when using the LLM
4. Consider increasing your swap space to 4GB

If you need more powerful models, consider using the commercial APIs for specific complex tasks while relying on your local setup for day-to-day coding assistance.
