"""
Reinforcement Learning agent for OpenHands.

This module implements the reinforcement learning agent that integrates
with OpenHands' LLM system and controller.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union
import torch

from .controller import RLController, Task
from .env import BaseEnvClient, WebEnvClient
from .strategy import IRolloutStrategy, StandardReActStrategy
from .storage import ITrajectoryStorage, FileTrajectoryStorage


@dataclass
class RLAgentConfig:
    """
    Configuration for the reinforcement learning agent.
    
    Attributes:
        max_turns: Maximum number of turns in a conversation
        max_prompt_length: Maximum length of prompt
        max_response_length: Maximum length of response
        max_obs_length: Maximum length of observation
        react_format: Whether to use ReAct format
        env_name: Name of the environment
        env_port: Port number for environment server
        env_server_base: Base URL for environment server
        rollout_strategy: Strategy to use for rollout
        storage_backend: Backend for storing trajectories
        max_workers: Maximum number of worker threads
    """
    max_turns: int = 10
    max_prompt_length: int = 2048
    max_response_length: int = 512
    max_obs_length: int = 1024
    react_format: bool = True
    
    # Environment configuration
    env_name: str = "webshop"
    env_port: int = 8000
    env_server_base: str = "http://127.0.0.1"
    rollout_strategy: str = "StandardReAct"
    storage_backend: str = "file"
    max_workers: int = 10


class RLAgent:
    """
    Reinforcement Learning agent for OpenHands.
    
    This agent integrates with OpenHands' LLM system and controller
    to provide reinforcement learning capabilities.
    """
    
    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        config: RLAgentConfig,
        tool_manager: Optional[Any] = None
    ):
        """
        Initialize the reinforcement learning agent.
        
        Args:
            model: Language model for generating responses
            tokenizer: Tokenizer for the language model
            config: Agent configuration
            tool_manager: Optional tool manager for tool use
        """
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.tool_manager = tool_manager
        
        # Initialize controller and environment
        self._init_controller()
    
    def _init_controller(self):
        """
        Initialize the reinforcement learning controller and environment.
        
        This method:
        1. Creates environment client
        2. Selects rollout strategy
        3. Configures storage backend
        4. Initializes the controller
        """
        # Create environment client
        client = WebEnvClient(
            env_server_base=self.config.env_server_base,
            env_port=self.config.env_port,
            timeout=300,
            data_len=100
        )
        
        # Create task
        task = Task(
            env_name=self.config.env_name,
            clients=[client]
        )
        
        # Select rollout strategy
        if self.config.rollout_strategy == "StandardReAct":
            strategy = StandardReActStrategy()
        elif self.config.rollout_strategy == "ToT":
            from .strategy import ToTStrategy
            strategy = ToTStrategy(num_branches=3, depth=2)
        elif self.config.rollout_strategy == "MCTS":
            from .strategy import MCTSStrategy
            strategy = MCTSStrategy(num_simulations=50, exploration_weight=1.0)
        else:
            raise ValueError(f"Unknown strategy: {self.config.rollout_strategy}")
        
        # Configure storage backend
        if self.config.storage_backend == "mongodb":
            from .storage import MongoDBTrajectoryStorage
            storage = MongoDBTrajectoryStorage()
        elif self.config.storage_backend == "file":
            from .storage import FileTrajectoryStorage
            storage = FileTrajectoryStorage()
        else:
            raise ValueError(f"Unknown storage backend: {self.config.storage_backend}")
        
        # Initialize controller
        self.controller = RLController(
            agent=self,
            tasks=[task],
            strategy=strategy,
            storage=storage,
            max_workers=self.config.max_workers
        )
    
    def create_prompt(self, task_description: str) -> str:
        """
        Create a prompt for the agent.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Formatted prompt string
        """
        if self.tool_manager:
            tools_instructions = self.tool_manager.get_prompt_instructions()
        else:
            tools_instructions = ""
        
        if self.config.react_format:
            prompt = f"""# Task
{task_description}

# Instructions
{tools_instructions}

Let's solve this step by step.

"""
        else:
            prompt = f"""# Task
{task_description}

# Instructions
{tools_instructions}

"""
        
        return prompt
    
    def run(
        self,
        task_description: str,
        max_rounds: Optional[int] = None,
        task_indices: Optional[List[int]] = None,
        parallel: bool = True,
        batch_size: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run the agent on tasks.
        
        Args:
            task_description: Description of the task
            max_rounds: Maximum number of interaction rounds
            task_indices: Indices of tasks to run
            parallel: Whether to run tasks in parallel
            batch_size: Batch size for parallel execution
            metadata: Additional metadata
            
        Returns:
            List of results
        """
        # Create generation config
        from transformers import GenerationConfig
        
        generation_config = GenerationConfig(
            max_length=self.config.max_response_length,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        # Set max rounds
        if max_rounds is None:
            max_rounds = self.config.max_turns
        
        # Add task description to metadata
        if metadata is None:
            metadata = {}
        metadata["task_description"] = task_description
        
        # Run rollout
        results = self.controller.rollout(
            generation_config=generation_config,
            max_rounds=max_rounds,
            idxs=task_indices,
            save_to_storage=True,
            parallel=parallel,
            batch_size=batch_size,
            metadata=metadata
        )
        
        # Process results
        processed_results = []
        for result in results:
            processed_result = {
                "conversation": result.conversation,
                "reward": float(result.reward),
                "text": result.text
            }
            processed_results.append(processed_result)
        
        return processed_results
    
    def train(
        self,
        learning_rate: float = 1e-5,
        num_epochs: int = 3,
        batch_size: int = 8,
        max_grad_norm: float = 1.0,
        env_name: Optional[str] = None,
        task_id: Optional[int] = None
    ):
        """
        Train the agent using reinforcement learning.
        
        Args:
            learning_rate: Learning rate for optimization
            num_epochs: Number of training epochs
            batch_size: Batch size for training
            max_grad_norm: Maximum gradient norm for clipping
            env_name: Filter trajectories by environment name
            task_id: Filter trajectories by task ID
        """
        # Get trajectories from storage
        trajectories = self.controller.get_storage().get_trajectories(
            env_name=env_name or self.config.env_name,
            task_id=task_id,
            limit=1000,
            sort_by="reward",
            sort_order="desc"
        )
        
        if not trajectories:
            print("No trajectories found for training.")
            return
        
        # Extract training data
        train_data = []
        for traj in trajectories:
            trajectory = traj["trajectory"]
            conversation = trajectory["conversation"]
            
            # Extract input-output pairs
            for i in range(0, len(conversation) - 1, 2):
                if i + 1 < len(conversation):
                    human_msg = conversation[i]
                    agent_msg = conversation[i + 1]
                    
                    if human_msg["from"] == "human" and agent_msg["from"] == "gpt":
                        train_data.append({
                            "input": human_msg["value"],
                            "output": agent_msg["value"],
                            "reward": trajectory["reward"]
                        })
        
        if not train_data:
            print("No valid training examples found.")
            return
        
        # Set up optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        self.model.train()
        for epoch in range(num_epochs):
            total_loss = 0.0
            
            # Process in batches
            for i in range(0, len(train_data), batch_size):
                batch = train_data[i:i + batch_size]
                
                # Prepare batch
                inputs = [item["input"] for item in batch]
                outputs = [item["output"] for item in batch]
                rewards = torch.tensor([item["reward"] for item in batch], dtype=torch.float)
                
                # Tokenize
                input_ids = self.tokenizer(
                    inputs,
                    padding="longest",
                    return_tensors="pt"
                ).input_ids.to(self.model.device)
                
                output_ids = self.tokenizer(
                    outputs,
                    padding="longest",
                    return_tensors="pt"
                ).input_ids.to(self.model.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    labels=output_ids
                )
                
                # Scale loss by reward
                loss = outputs.loss * rewards.mean()
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                optimizer.step()
                
                total_loss += loss.item()
            
            # Print epoch statistics
            avg_loss = total_loss / (len(train_data) / batch_size)
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")
        
        # Save model
        self.model.save_pretrained("rl_trained_model")
        self.tokenizer.save_pretrained("rl_trained_model")
        print("Training complete. Model saved to 'rl_trained_model'.")