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

Based on your hardware specifications (AMD A9-9410 dual-core CPU, 8GB RAM, AMD Radeon R5 Graphics), here are optimized instructions for setting up a local Mistral 7B server for coding tasks.

### 2.1 Hardware Assessment

Your system has:
- Dual-core AMD A9-9410 CPU
- 8GB RAM (with 2GB swap)
- AMD Radeon R5 Graphics (not CUDA-compatible)
- 223GB SSD with ~97GB free space

This hardware is suitable for running smaller quantized models with optimizations. For Mistral 7B, we'll need to use aggressive quantization and optimize for CPU-only inference.

### 2.2 Setting Up llama.cpp for Mistral 7B

llama.cpp is a lightweight C/C++ inference engine that can run Mistral 7B efficiently on CPU-only systems.

```bash
# Install build dependencies
sudo apt update
sudo apt install -y build-essential cmake git python3-dev python3-pip

# Clone llama.cpp repository
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build llama.cpp
make

# Create a Python virtual environment
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate

# Install Python bindings
pip install -e .
```

### 2.3 Download Quantized Mistral 7B Model

For your hardware, we'll use a 4-bit quantized version of Mistral 7B to minimize memory usage.

```bash
# Create a models directory
mkdir -p models
cd models

# Download a 4-bit quantized Mistral 7B model
# This is optimized for CPU usage
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Return to the main directory
cd ..
```

### 2.4 Running Mistral 7B on CPU

```bash
# Run the model with CPU-only configuration
./main -m ./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    -ngl 0 \
    --color \
    -ins -b 256 \
    --temp 0.7 \
    --ctx-size 2048
```

Parameters explained:
- `-m`: Path to the model file
- `-ngl 0`: Disables GPU usage, forces CPU-only mode
- `--color`: Enables colored output
- `-ins`: Enables instruction mode for better responses
- `-b 256`: Batch size of 256 (adjust lower if you experience memory issues)
- `--temp 0.7`: Temperature setting for response randomness
- `--ctx-size 2048`: Context window size (reduce if memory issues occur)

### 2.5 Creating a Python Interface

For integration with Vortex/OpenHands, we'll create a Python interface:

```bash
# Install required packages
pip install llama-cpp-python fastapi uvicorn pydantic

# Create a server script
cat > mistral_server.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
import uvicorn
import json

app = FastAPI(title="Mistral 7B API Server")

# Initialize the model
model_path = "./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
llm = Llama(
    model_path=model_path,
    n_ctx=2048,        # Context size
    n_batch=256,       # Batch size
    n_gpu_layers=0,    # Force CPU only
    verbose=False      # Disable verbose output
)

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
        # Format prompt based on messages
        prompt = ""
        for msg in request.messages:
            if msg.role == "system":
                prompt = f"<s>[INST] {msg.content} [/INST]"
            elif msg.role == "user":
                prompt += f"\n\n[INST] {msg.content} [/INST]"
            elif msg.role == "assistant":
                prompt += f"\n{msg.content}"
        
        # Generate response
        output = llm(
            prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=["[INST]", "</s>"],
            echo=False
        )
        
        # Format response like OpenAI
        return {
            "id": "mistral-completion",
            "object": "chat.completion",
            "created": 0,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": output["choices"][0]["text"].strip()
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

# Make the script executable
chmod +x mistral_server.py
```

### 2.6 Creating a Systemd Service

```bash
# Create a systemd service for auto-start
cat > mistral-api.service << 'EOF'
[Unit]
Description=Mistral 7B API Server
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/llama.cpp
ExecStart=/home/YOUR_USERNAME/llama.cpp/venv/bin/python /home/YOUR_USERNAME/llama.cpp/mistral_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Replace YOUR_USERNAME with your actual username
sed -i "s/YOUR_USERNAME/$USER/g" mistral-api.service

# Install the service
sudo mv mistral-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mistral-api
sudo systemctl start mistral-api

# Check status
sudo systemctl status mistral-api
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

# Set process priority for Mistral server
MISTRAL_PID=$(pgrep -f mistral_server.py)
if [ ! -z "$MISTRAL_PID" ]; then
    sudo renice -n -10 -p $MISTRAL_PID
    sudo ionice -c 2 -n 0 -p $MISTRAL_PID
fi

echo "System optimized for LLM inference"
EOF

# Make the script executable
chmod +x optimize_for_llm.sh

# Run the optimization script
./optimize_for_llm.sh
```

## 3. Integrating with Vortex/OpenHands Framework

### 3.1 Configure Vortex to Use Local Mistral 7B Server

Edit your `config.toml` file to use the local Mistral 7B server:

```toml
[llm]
provider = "openai"  # We're using the OpenAI-compatible API format
base_url = "http://localhost:8000/v1"  # Point to our local server
api_key = "dummy-key"  # Not used but required
model = "mistral-7b"  # The model name we're using
```

### 3.2 Testing the Integration

Create a test script to verify the integration:

```bash
# Create a test script
cat > test_mistral.py << 'EOF'
import requests
import json

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
data = {
    "model": "mistral-7b",
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
python3 test_mistral.py
```

### 3.3 Monitoring Resource Usage

Create a monitoring script to ensure your system can handle the LLM:

```bash
# Create a monitoring script
cat > monitor_mistral.sh << 'EOF'
#!/bin/bash

echo "Monitoring system resources for Mistral 7B usage..."
echo "Press Ctrl+C to exit"

while true; do
    clear
    echo "=== CPU Usage ==="
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "CPU Usage: " 100 - $1 "%"}'
    
    echo -e "\n=== Memory Usage ==="
    free -h | grep "Mem:"
    
    echo -e "\n=== Swap Usage ==="
    free -h | grep "Swap:"
    
    echo -e "\n=== Mistral Process ==="
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 2
    ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep mistral
    
    sleep 2
done
EOF

# Make the script executable
chmod +x monitor_mistral.sh
```

## 4. Alternative Approach: Using Hugging Face Transformers

If you prefer a more Python-native approach, you can use Hugging Face Transformers:

```bash
# Create a new virtual environment
python3 -m venv mistral_env
source mistral_env/bin/activate

# Install required packages
pip install transformers torch accelerate bitsandbytes langchain fastapi uvicorn

# Create a server script
cat > mistral_hf_server.py << 'EOF'
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mistral 7B HF API Server")

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

# Load model and tokenizer
model_id = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,
    device_map="auto",
    low_cpu_mem_usage=True
)

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
        # Format prompt based on messages
        prompt = ""
        for msg in request.messages:
            if msg.role == "system":
                prompt = f"<s>[INST] {msg.content} [/INST]"
            elif msg.role == "user":
                prompt += f"\n\n[INST] {msg.content} [/INST]"
            elif msg.role == "assistant":
                prompt += f"\n{msg.content}"
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = response_text.replace(prompt, "").strip()
        
        # Format response like OpenAI
        return {
            "id": "mistral-completion",
            "object": "chat.completion",
            "created": 0,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(inputs.input_ids[0]),
                "completion_tokens": len(outputs[0]) - len(inputs.input_ids[0]),
                "total_tokens": len(outputs[0])
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

# Make the script executable
chmod +x mistral_hf_server.py
```

## 5. Troubleshooting

### 5.1 Out of Memory Issues

If you encounter out-of-memory errors:

```bash
# Reduce context window size
./main -m ./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    -ngl 0 \
    --ctx-size 1024 \  # Reduced from 2048
    -b 128             # Reduced batch size
```

### 5.2 Slow Response Times

If responses are too slow:

```bash
# Try a smaller model or more aggressive quantization
# Download a 3-bit quantized model instead
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q3_K_M.gguf
```

### 5.3 API Connection Issues

If Vortex can't connect to the local API:

```bash
# Check if the API server is running
curl http://localhost:8000/health

# Restart the API server
sudo systemctl restart mistral-api

# Check logs for errors
sudo journalctl -u mistral-api -n 50
```

## 6. Conclusion

This guide provides both commercial API options and a local Mistral 7B server setup optimized for your specific hardware. The local setup is designed to work within the constraints of your AMD A9-9410 CPU and 8GB RAM while still providing useful coding assistance.

For the best experience on your hardware:
1. Use the 4-bit quantized Mistral 7B model for most coding tasks
2. Keep the context window small (1024-2048 tokens)
3. Close other memory-intensive applications when using the LLM
4. Consider increasing your swap space to 4GB

If you need more powerful models, consider using the commercial APIs for specific complex tasks while relying on your local setup for day-to-day coding assistance.
