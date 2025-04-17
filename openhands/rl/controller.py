"""
Reinforcement Learning controller for OpenHands.

This module implements the controller for reinforcement learning,
which manages the interaction between agents and environments.
"""

from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import torch

from .env import BaseEnvClient, StepOutput
from .types import ExperienceOutput
from .storage import ITrajectoryStorage, FileTrajectoryStorage

# Forward declaration for type hints
IRolloutStrategy = Any


class Task:
    """
    A reinforcement learning task.
    
    Attributes:
        env_name: Name of the environment
        clients: List of environment clients
    """
    
    def __init__(
        self,
        env_name: str,
        clients: List[BaseEnvClient]
    ):
        self.env_name = env_name
        self.clients = clients


class RLController:
    """
    Controller for reinforcement learning in OpenHands.
    
    This controller manages the interaction between agents and environments,
    executes rollout strategies, and stores trajectories.
    """
    
    def __init__(
        self,
        agent: Any,
        tasks: List[Task],
        strategy: Optional[IRolloutStrategy] = None,
        storage: Optional[ITrajectoryStorage] = None,
        max_workers: int = 10
    ):
        """
        Initialize the reinforcement learning controller.
        
        Args:
            agent: Agent instance with model and tokenizer
            tasks: List of Task instances
            strategy: Rollout strategy to use (defaults to StandardReActStrategy)
            storage: Trajectory storage implementation
            max_workers: Maximum number of worker threads for parallel rollout
        """
        self.agent = agent
        self.tasks = tasks
        self.storage = storage or FileTrajectoryStorage()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Import here to avoid circular imports
        if strategy is None:
            from .strategy import StandardReActStrategy
            self.strategy = StandardReActStrategy()
        else:
            self.strategy = strategy
    
    def set_strategy(self, strategy: IRolloutStrategy):
        """Change the rollout strategy."""
        self.strategy = strategy
    
    def set_storage(self, storage: ITrajectoryStorage):
        """Set or change the trajectory storage."""
        self.storage = storage
    
    def get_storage(self) -> Optional[ITrajectoryStorage]:
        """Get the current trajectory storage instance."""
        return self.storage
    
    def rollout(
        self,
        generation_config: Optional[Any] = None,
        max_rounds: Optional[int] = None,
        idxs: Optional[List[int]] = None,
        save_to_storage: bool = True,
        parallel: bool = True,
        batch_size: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ExperienceOutput]:
        """
        Execute rollout using the selected strategy.
        
        Args:
            generation_config: Configuration for text generation
            max_rounds: Maximum number of interaction rounds
            idxs: List of task indices to run
            save_to_storage: Whether to save trajectories
            parallel: Whether to run tasks in parallel
            batch_size: Batch size for parallel execution
            metadata: Additional metadata to store
            
        Returns:
            List of ExperienceOutput objects
        """
        if not save_to_storage or self.storage is None:
            save_to_storage = False
        
        if idxs is None:
            idxs = []
            for task in self.tasks:
                idxs.append(list(range(len(task.clients[0]))))
        elif isinstance(idxs[0], int):
            idxs = [idxs] + [[] for _ in range(len(self.tasks) - 1)]
        
        task = self.tasks[0]
        task_idxs = idxs[0]
        
        results = []
        
        if parallel:
            # Process in batches
            for i in range(0, len(task_idxs), batch_size):
                batch_idxs = task_idxs[i:i+batch_size]
                
                # Submit tasks to thread pool
                futures = {}
                for idx in batch_idxs:
                    future = self.executor.submit(
                        self._rollout_one,
                        task=task,
                        idx=idx,
                        generation_config=generation_config,
                        max_rounds=max_rounds,
                        save_to_storage=save_to_storage,
                        metadata=metadata
                    )
                    futures[future] = idx
                
                # Collect results
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        exp_outputs = future.result()
                        results.extend(exp_outputs)
                    except Exception as e:
                        print(f"Error in rollout for task {idx}: {e}")
        else:
            # Sequential processing
            for idx in task_idxs:
                try:
                    exp_outputs = self._rollout_one(
                        task=task,
                        idx=idx,
                        generation_config=generation_config,
                        max_rounds=max_rounds,
                        save_to_storage=save_to_storage,
                        metadata=metadata
                    )
                    results.extend(exp_outputs)
                except Exception as e:
                    print(f"Error in rollout for task {idx}: {e}")
        
        return results
    
    def _rollout_one(
        self,
        task: Task,
        idx: int,
        generation_config: Optional[Any],
        max_rounds: Optional[int],
        save_to_storage: bool,
        metadata: Optional[Dict[str, Any]]
    ) -> List[ExperienceOutput]:
        """
        Execute rollout for a single task.
        
        Args:
            task: Task to run
            idx: Task ID
            generation_config: Generation configuration
            max_rounds: Maximum rounds
            save_to_storage: Whether to save trajectories
            metadata: Additional metadata
            
        Returns:
            List of ExperienceOutput objects
        """
        # Get client
        client = task.clients[0]
        
        # Reset environment
        client.reset(idx)
        
        # Get initial observation
        initial_observation = client.observe()
        
        # Execute strategy
        trajectories = self.strategy.execute(
            model=self.agent.model,
            tokenizer=self.agent.tokenizer,
            client=client,
            initial_observation=initial_observation,
            generation_config=generation_config,
            max_rounds=max_rounds
        )
        
        # Save trajectories if requested
        if save_to_storage and self.storage is not None and trajectories:
            self._save_trajectories(task.env_name, idx, trajectories, metadata)
        
        return trajectories
    
    def _save_trajectories(
        self,
        env_name: str,
        task_id: int,
        trajectories: List[ExperienceOutput],
        metadata: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Save trajectories using the storage.
        
        Args:
            env_name: Environment name
            task_id: Task ID
            trajectories: List of ExperienceOutput objects
            metadata: Additional metadata
            
        Returns:
            List of trajectory IDs
        """
        # Convert ExperienceOutput to dict format for storage
        trajectory_dicts = []
        
        for traj in trajectories:
            traj_dict = {
                "reward": float(traj.reward),
                "conversation": [
                    {
                        "from": msg["from"],
                        "value": msg["value"],
                        "loss": msg.get("loss")
                    } for msg in traj.conversation
                ],
                "text": traj.text
            }
            trajectory_dicts.append(traj_dict)
        
        # Save using storage
        trajectory_ids = self.storage.save_trajectories(
            env_name=env_name,
            task_ids=[task_id] * len(trajectories),
            trajectories=trajectory_dicts,
            metadata=metadata
        )
        
        return trajectory_ids