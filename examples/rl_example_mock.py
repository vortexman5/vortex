"""
Example script for using the reinforcement learning module in OpenHands with a mock model.

This script demonstrates how to set up and use the reinforcement learning
capabilities in OpenHands using a mock model for testing.
"""

import os
import sys
import torch
import subprocess
import time

# Add the parent directory to the path to import openhands
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openhands.rl import RLAgent, RLAgentConfig
from openhands.rl.env import WebEnvClient
from openhands.rl.strategy import StandardReActStrategy, ToTStrategy


def start_env_server(host: str, port: int):
    """
    Start the environment server in a separate process.
    
    Args:
        host: Host to run the server on
        port: Port to run the server on
    """
    env_server_path = os.path.join(os.path.dirname(__file__), 'rl_env_server.py')
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, env_server_path, '--host', host, '--port', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    return process


def main():
    """Run the reinforcement learning example with a mock model."""
    # Create a mock model and tokenizer for testing
    class MockModel:
        def __init__(self):
            self.device = "cpu"
        
        def generate(self, input_ids, generation_config=None):
            # Simple mock generation
            if "search" not in str(input_ids):
                return [[0, 0, 0] + [1] * 10]  # First response: search for products
            elif "hiking" not in str(input_ids):
                return [[0, 0, 0] + [2] * 10]  # Second response: view hiking backpack
            else:
                return [[0, 0, 0] + [3] * 10]  # Third response: buy the backpack
    
    class MockTokenizer:
        def __init__(self):
            self.pad_token_id = 0
            self.eos_token_id = 0
        
        def encode(self, text, return_tensors=None, add_special_tokens=True):
            # Simple mock encoding
            if return_tensors == "pt":
                import torch
                return torch.tensor([[0, 0, 0]])
            return [0, 0, 0]
        
        def decode(self, ids, skip_special_tokens=True):
            # Simple mock decoding based on the first token
            if ids[0] == 1:
                return "I'll search for backpacks."
            elif ids[0] == 2:
                return "I'll view the Hiking Backpack."
            elif ids[0] == 3:
                return "I'll buy the Hiking Backpack."
            return "I'm not sure what to do."
        
        def batch_decode(self, ids, skip_special_tokens=True):
            # Simple mock batch decoding
            return [self.decode(id_seq, skip_special_tokens) for id_seq in ids]
    
    # Start the environment server
    host = "127.0.0.1"
    port = 8000
    print(f"Starting environment server on {host}:{port}...")
    server_process = start_env_server(host, port)
    
    try:
        # Configure the RL agent
        config = RLAgentConfig(
            max_turns=5,
            max_prompt_length=2048,
            max_response_length=512,
            max_obs_length=1024,
            react_format=True,
            env_name="webshop",
            env_port=port,
            env_server_base=f"http://{host}",
            rollout_strategy="StandardReAct",
            storage_backend="file",
            max_workers=1
        )
        
        # Create the RL agent with mock model and tokenizer
        print("Creating RL agent...")
        agent = RLAgent(
            model=MockModel(),
            tokenizer=MockTokenizer(),
            config=config
        )
        
        # Define a task
        task_description = """
        You are shopping for a gift for your friend who loves hiking.
        Find a suitable backpack that costs less than $100.
        """
        
        # Run the agent
        print("Running RL agent...")
        results = agent.run(
            task_description=task_description,
            max_rounds=5,
            task_indices=[0],  # Run on the first task
            parallel=False
        )
        
        # Print results
        print("\nResults:")
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"Reward: {result['reward']}")
            print("Conversation:")
            for msg in result["conversation"]:
                role = msg["from"]
                content = msg["value"]
                print(f"{role.upper()}: {content}")
            print()
        
        # Try a different strategy
        print("Switching to Tree of Thoughts strategy...")
        from openhands.rl.strategy import ToTStrategy
        agent.controller.set_strategy(ToTStrategy(num_branches=2, depth=2))
        
        # Run again with the new strategy
        results = agent.run(
            task_description=task_description,
            max_rounds=3,  # Fewer rounds for ToT since it explores multiple paths
            task_indices=[0],
            parallel=False
        )
        
        # Print results
        print("\nResults with Tree of Thoughts strategy:")
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"Reward: {result['reward']}")
            print("Conversation:")
            for msg in result["conversation"]:
                role = msg["from"]
                content = msg["value"]
                print(f"{role.upper()}: {content}")
            print()
    
    finally:
        # Stop the server
        print("Stopping environment server...")
        server_process.terminate()
        server_process.wait()
    
    print("Example complete!")


if __name__ == "__main__":
    main()