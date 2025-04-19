"""
Environment interface for reinforcement learning in OpenHands.

This module defines the base environment client interface and related classes
for interacting with environments in reinforcement learning scenarios.
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class StepOutput:
    """
    Output from an environment step.
    
    Attributes:
        state: The new state observation as a string
        reward: The reward received for the action
        done: Whether the episode is complete
    """
    state: str
    reward: float
    done: bool


class BaseEnvClient(metaclass=ABCMeta):
    """
    Base class for environment clients in reinforcement learning.
    
    This abstract class defines the interface for environment clients
    that agents can interact with during reinforcement learning.
    """
    
    conversation_start = ()
    
    @abstractmethod
    def __len__(self) -> int:
        """
        Return the total size of the environment.
        
        Returns:
            The number of tasks or episodes available in the environment
        """
        pass
    
    @abstractmethod
    def observe(self) -> str:
        """
        Parse environment response and provide a text observation.
        
        Returns:
            A text message describing the current state of the environment
        """
        pass
    
    @abstractmethod
    def step(self, action: str) -> StepOutput:
        """
        Take an action in the environment and return the result.
        
        Args:
            action: The action to take, as a string
            
        Returns:
            A StepOutput containing the new state, reward, and done flag
        """
        pass
    
    @abstractmethod
    def reset(self, idx: int) -> None:
        """
        Reset the environment to a specific state.
        
        Args:
            idx: The index of the task or episode to reset to
        """
        pass


class WebEnvClient(BaseEnvClient):
    """
    Environment client for web-based environments.
    
    This client connects to a web server that hosts the environment
    and communicates with it via HTTP requests.
    """
    
    def __init__(
        self, 
        env_server_base: str = "http://127.0.0.1",
        env_port: int = 8000,
        timeout: int = 60,
        data_len: int = 100
    ):
        """
        Initialize the web environment client.
        
        Args:
            env_server_base: Base URL for the environment server
            env_port: Port number for the environment server
            timeout: Timeout for HTTP requests in seconds
            data_len: Number of tasks or episodes available
        """
        import requests
        
        self.base_url = f"{env_server_base}:{env_port}"
        self.timeout = timeout
        self.data_len = data_len
        self.session = requests.Session()
        self.current_state = ""
        self.current_idx = 0
    
    def __len__(self) -> int:
        """Return the number of available tasks."""
        return self.data_len
    
    def observe(self) -> str:
        """Return the current state observation."""
        return self.current_state
    
    def step(self, action: str) -> StepOutput:
        """
        Take an action in the environment.
        
        Args:
            action: The action to take, as a string
            
        Returns:
            A StepOutput with the new state, reward, and done flag
        """
        try:
            response = self.session.post(
                f"{self.base_url}/step",
                json={"action": action, "idx": self.current_idx},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            self.current_state = data["state"]
            reward = data.get("reward", 0.0)
            done = data.get("done", False)
            
            return StepOutput(state=self.current_state, reward=reward, done=done)
        except Exception as e:
            # Log the error and return a default response
            print(f"Error in environment step: {e}")
            return StepOutput(
                state=f"Error: {str(e)}",
                reward=0.0,
                done=True
            )
    
    def reset(self, idx: int) -> None:
        """
        Reset the environment to a specific task.
        
        Args:
            idx: The index of the task to reset to
        """
        try:
            self.current_idx = idx
            response = self.session.post(
                f"{self.base_url}/reset",
                json={"idx": idx},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            self.current_state = data["state"]
        except Exception as e:
            # Log the error and set a default state
            print(f"Error resetting environment: {e}")
            self.current_state = f"Error: {str(e)}"