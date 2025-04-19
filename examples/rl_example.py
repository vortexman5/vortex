"""
Example script for using the reinforcement learning module in OpenHands.

This script demonstrates how to set up and use the reinforcement learning
capabilities in OpenHands.
"""

import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add the parent directory to the path to import openhands
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openhands.rl import RLAgent, RLAgentConfig
from openhands.rl.env import WebEnvClient
from openhands.rl.strategy import StandardReActStrategy, ToTStrategy


def main():
    """Run the reinforcement learning example."""
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    model_name = "meta-llama/Llama-2-7b-chat-hf"  # Replace with your preferred model
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Configure the RL agent
    config = RLAgentConfig(
        max_turns=5,
        max_prompt_length=2048,
        max_response_length=512,
        max_obs_length=1024,
        react_format=True,
        env_name="webshop",
        env_port=8000,
        env_server_base="http://127.0.0.1",
        rollout_strategy="StandardReAct",
        storage_backend="file",
        max_workers=4
    )
    
    # Create the RL agent
    print("Creating RL agent...")
    agent = RLAgent(
        model=model,
        tokenizer=tokenizer,
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
            print(f"{role.upper()}: {content[:100]}...")
        print()
    
    # Try a different strategy
    print("Switching to Tree of Thoughts strategy...")
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
            print(f"{role.upper()}: {content[:100]}...")
        print()
    
    # Train the agent (optional)
    print("\nTraining the agent...")
    agent.train(
        learning_rate=1e-5,
        num_epochs=1,  # Just one epoch for the example
        batch_size=4
    )
    
    print("Example complete!")


if __name__ == "__main__":
    main()