"""
Rollout strategies for reinforcement learning in OpenHands.

This module implements various rollout strategies for reinforcement learning,
including standard ReAct, Tree of Thoughts (ToT), and Monte Carlo Tree Search (MCTS).
"""

from typing import List, Dict, Any, Optional, TypedDict, Union
from abc import ABC, abstractmethod
import copy
import random
import torch

from .env import BaseEnvClient, StepOutput
from .controller import ExperienceOutput


class ConversationMessage(Dict[str, Any]):
    """A message in a conversation between an agent and an environment."""
    pass


class TrajectoryNode(TypedDict):
    """Node in a trajectory tree/graph."""
    observation: str
    thought: str
    action: str
    reward: float
    done: bool
    children: List['TrajectoryNode']


class IRolloutStrategy(ABC):
    """Interface for rollout strategies."""
    
    @abstractmethod
    def execute(
        self,
        model: Any,
        tokenizer: Any,
        client: BaseEnvClient,
        initial_observation: str,
        generation_config: Optional[Any] = None,
        max_rounds: Optional[int] = None
    ) -> List[ExperienceOutput]:
        """
        Execute the strategy and return trajectories.
        
        Args:
            model: Language model for generating responses
            tokenizer: Tokenizer for the language model
            client: Environment client
            initial_observation: Initial observation from the environment
            generation_config: Configuration for text generation
            max_rounds: Maximum number of interaction rounds
            
        Returns:
            List of ExperienceOutput objects
        """
        pass


class BaseRolloutStrategy(IRolloutStrategy):
    """Base class for rollout strategies with common functionality."""
    
    def __init__(self, name: str):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
    
    def _create_experience_output(
        self,
        conversation: List[ConversationMessage],
        reward: float,
        text: str,
        tokenizer: Any
    ) -> ExperienceOutput:
        """
        Convert conversation to ExperienceOutput format.
        
        Args:
            conversation: List of conversation messages
            reward: Final reward
            text: Full text of the conversation
            tokenizer: Tokenizer for encoding text
            
        Returns:
            ExperienceOutput object
        """
        tokenized = tokenizer.encode(text, add_special_tokens=False)
        return ExperienceOutput(
            conversation=conversation,
            reward=reward,
            text=text,
            seq_ids=tokenized,
            attention_mask=[1] * len(tokenized),
            action_mask=[0] * len(tokenized)  # Simplified; actual mask would be more complex
        )


class StandardReActStrategy(BaseRolloutStrategy):
    """Standard ReAct strategy for reinforcement learning."""
    
    def __init__(self):
        """Initialize the StandardReAct strategy."""
        super().__init__("StandardReAct")
    
    def execute(
        self,
        model: Any,
        tokenizer: Any,
        client: BaseEnvClient,
        initial_observation: str,
        generation_config: Optional[Any] = None,
        max_rounds: Optional[int] = None
    ) -> List[ExperienceOutput]:
        """
        Execute standard ReAct strategy.
        
        Args:
            model: Language model for generating responses
            tokenizer: Tokenizer for the language model
            client: Environment client
            initial_observation: Initial observation from the environment
            generation_config: Configuration for text generation
            max_rounds: Maximum number of interaction rounds
            
        Returns:
            List of ExperienceOutput objects
        """
        # Initialize conversation
        conversation = list(client.conversation_start)
        conversation.append(
            ConversationMessage({"from": "human", "loss": None, "value": initial_observation})
        )
        
        # Build initial text
        text = ""
        for msg in conversation:
            if msg["from"] == "human":
                text += f"\nHuman: {msg['value']}"
            else:
                text += f"\nAssistant: {msg['value']}"
        
        rounds = 0
        reward = 0.0
        done = False
        
        # Main interaction loop
        while not done:
            if max_rounds is not None and rounds >= max_rounds:
                break
            
            # Generate agent's response
            input_ids = tokenizer.encode(text, return_tensors="pt").to(model.device)
            output = model.generate(
                input_ids,
                generation_config=generation_config
            )
            
            # Decode response
            generated_text = tokenizer.decode(
                output[0][input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            # Add to conversation
            conversation.append(
                ConversationMessage({"from": "gpt", "loss": True, "value": generated_text})
            )
            text += f"\nAssistant: {generated_text}"
            
            # Take action in environment
            step_output = client.step(generated_text)
            state, reward, done = step_output.state, step_output.reward, step_output.done
            
            # Add environment feedback to conversation
            conversation.append(
                ConversationMessage({"from": "human", "loss": None, "value": state})
            )
            text += f"\nHuman: {state}"
            
            rounds += 1
        
        # Create and return a single trajectory
        experience = self._create_experience_output(
            conversation=conversation,
            reward=reward,
            text=text,
            tokenizer=tokenizer
        )
        
        return [experience]


class ToTStrategy(BaseRolloutStrategy):
    """Tree of Thoughts strategy for reinforcement learning."""
    
    def __init__(self, num_branches: int = 3, depth: int = 2):
        """
        Initialize the Tree of Thoughts strategy.
        
        Args:
            num_branches: Number of branches to explore at each node
            depth: Maximum depth of the tree
        """
        super().__init__("ToT")
        self.num_branches = num_branches
        self.depth = depth
    
    def execute(
        self,
        model: Any,
        tokenizer: Any,
        client: BaseEnvClient,
        initial_observation: str,
        generation_config: Optional[Any] = None,
        max_rounds: Optional[int] = None
    ) -> List[ExperienceOutput]:
        """
        Execute Tree of Thoughts strategy.
        
        Args:
            model: Language model for generating responses
            tokenizer: Tokenizer for the language model
            client: Environment client
            initial_observation: Initial observation from the environment
            generation_config: Configuration for text generation
            max_rounds: Maximum number of interaction rounds
            
        Returns:
            List of ExperienceOutput objects
        """
        # Generate trajectory tree
        tree = self._generate_tree(
            model=model,
            tokenizer=tokenizer,
            client=client,
            observation=initial_observation,
            conversation=[
                *list(client.conversation_start),
                ConversationMessage({"from": "human", "loss": None, "value": initial_observation})
            ],
            depth=self.depth,
            generation_config=generation_config,
            max_rounds=max_rounds
        )
        
        # Extract all paths from tree
        trajectories = self._extract_paths(tree, tokenizer)
        
        return trajectories
    
    def _generate_tree(
        self,
        model: Any,
        tokenizer: Any,
        client: BaseEnvClient,
        observation: str,
        conversation: List[ConversationMessage],
        depth: int,
        generation_config: Optional[Any] = None,
        max_rounds: Optional[int] = None,
        current_round: int = 0
    ) -> TrajectoryNode:
        """
        Generate a trajectory tree node and its children recursively.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            client: Environment client
            observation: Current observation
            conversation: Conversation history
            depth: Remaining depth
            generation_config: Generation configuration
            max_rounds: Maximum rounds
            current_round: Current round
            
        Returns:
            TrajectoryNode representing the current node and its children
        """
        # Clone the client to avoid altering the original
        client_copy = copy.deepcopy(client)
        
        # Build text from conversation
        text = ""
        for msg in conversation:
            if msg["from"] == "human":
                text += f"\nHuman: {msg['value']}"
            else:
                text += f"\nAssistant: {msg['value']}"
        
        # Generate agent's response
        input_ids = tokenizer.encode(text, return_tensors="pt").to(model.device)
        
        # Create the current node
        node = {
            "observation": observation,
            "thought": "",
            "action": "",
            "reward": 0.0,
            "done": False,
            "children": []
        }
        
        # Check if we've reached max rounds
        if max_rounds is not None and current_round >= max_rounds:
            return node
        
        # Generate multiple branches
        for _ in range(self.num_branches):
            # Add temperature to promote diversity
            branch_generation_config = copy.deepcopy(generation_config)
            if hasattr(branch_generation_config, "temperature"):
                branch_generation_config.temperature = 0.7  # Adjust as needed
            
            output = model.generate(
                input_ids,
                generation_config=branch_generation_config
            )
            
            # Decode response
            generated_text = tokenizer.decode(
                output[0][input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            # Create branch conversation
            branch_conversation = copy.deepcopy(conversation)
            branch_conversation.append(
                ConversationMessage({"from": "gpt", "loss": True, "value": generated_text})
            )
            
            # Take action in environment
            branch_client = copy.deepcopy(client_copy)
            step_output = branch_client.step(generated_text)
            state, reward, done = step_output.state, step_output.reward, step_output.done
            
            # Add environment feedback
            branch_conversation.append(
                ConversationMessage({"from": "human", "loss": None, "value": state})
            )
            
            # Create child node
            child_node = {
                "observation": observation,
                "thought": "",  # Could extract a thought if using a specific format
                "action": generated_text,
                "reward": reward,
                "done": done,
                "children": []
            }
            
            # Recursively generate children if not at max depth and not done
            if depth > 1 and not done:
                child_children = self._generate_tree(
                    model=model,
                    tokenizer=tokenizer,
                    client=branch_client,
                    observation=state,
                    conversation=branch_conversation,
                    depth=depth-1,
                    generation_config=generation_config,
                    max_rounds=max_rounds,
                    current_round=current_round+1
                )
                child_node["children"] = [child_children]
            
            node["children"].append(child_node)
        
        return node
    
    def _extract_paths(
        self,
        tree: TrajectoryNode,
        tokenizer: Any,
        path: Optional[List[Dict[str, Any]]] = None
    ) -> List[ExperienceOutput]:
        """
        Extract all paths from tree and convert to ExperienceOutput.
        
        Args:
            tree: Trajectory tree node
            tokenizer: Tokenizer
            path: Current path (for recursion)
            
        Returns:
            List of ExperienceOutput objects
        """
        if path is None:
            path = []
        
        # Add current node to path
        current_path = path + [{
            "observation": tree["observation"],
            "action": tree["action"]
        }]
        
        # If leaf node, convert path to ExperienceOutput
        if not tree["children"]:
            # Build conversation from path
            conversation = []
            for step in current_path:
                if step["observation"]:
                    conversation.append(
                        ConversationMessage({"from": "human", "loss": None, "value": step["observation"]})
                    )
                if step["action"]:
                    conversation.append(
                        ConversationMessage({"from": "gpt", "loss": True, "value": step["action"]})
                    )
            
            # Build text from conversation
            text = ""
            for msg in conversation:
                if msg["from"] == "human":
                    text += f"\nHuman: {msg['value']}"
                else:
                    text += f"\nAssistant: {msg['value']}"
            
            # Create ExperienceOutput
            experience = self._create_experience_output(
                conversation=conversation,
                reward=tree["reward"],
                text=text,
                tokenizer=tokenizer
            )
            
            return [experience]
        
        # Recursively extract paths from children
        trajectories = []
        for child in tree["children"]:
            trajectories.extend(self._extract_paths(child, tokenizer, current_path))
        
        return trajectories


class MCTSStrategy(BaseRolloutStrategy):
    """Monte Carlo Tree Search strategy for reinforcement learning."""
    
    def __init__(self, num_simulations: int = 50, exploration_weight: float = 1.0):
        """
        Initialize the MCTS strategy.
        
        Args:
            num_simulations: Number of simulations to run
            exploration_weight: Exploration weight for UCB1 formula
        """
        super().__init__("MCTS")
        self.num_simulations = num_simulations
        self.exploration_weight = exploration_weight
    
    def execute(
        self,
        model: Any,
        tokenizer: Any,
        client: BaseEnvClient,
        initial_observation: str,
        generation_config: Optional[Any] = None,
        max_rounds: Optional[int] = None
    ) -> List[ExperienceOutput]:
        """
        Execute Monte Carlo Tree Search strategy.
        
        Args:
            model: Language model for generating responses
            tokenizer: Tokenizer for the language model
            client: Environment client
            initial_observation: Initial observation from the environment
            generation_config: Configuration for text generation
            max_rounds: Maximum number of interaction rounds
            
        Returns:
            List of ExperienceOutput objects
        """
        # Initialize conversation
        conversation = list(client.conversation_start)
        conversation.append(
            ConversationMessage({"from": "human", "loss": None, "value": initial_observation})
        )
        
        # Build initial text
        text = ""
        for msg in conversation:
            if msg["from"] == "human":
                text += f"\nHuman: {msg['value']}"
            else:
                text += f"\nAssistant: {msg['value']}"
        
        rounds = 0
        reward = 0.0
        done = False
        
        # Main interaction loop
        while not done:
            if max_rounds is not None and rounds >= max_rounds:
                break
            
            # Run MCTS to find the best action
            best_action = self._run_mcts(
                model=model,
                tokenizer=tokenizer,
                client=copy.deepcopy(client),
                text=text,
                generation_config=generation_config
            )
            
            # Add to conversation
            conversation.append(
                ConversationMessage({"from": "gpt", "loss": True, "value": best_action})
            )
            text += f"\nAssistant: {best_action}"
            
            # Take action in environment
            step_output = client.step(best_action)
            state, reward, done = step_output.state, step_output.reward, step_output.done
            
            # Add environment feedback to conversation
            conversation.append(
                ConversationMessage({"from": "human", "loss": None, "value": state})
            )
            text += f"\nHuman: {state}"
            
            rounds += 1
        
        # Create and return a single trajectory
        experience = self._create_experience_output(
            conversation=conversation,
            reward=reward,
            text=text,
            tokenizer=tokenizer
        )
        
        return [experience]
    
    def _run_mcts(
        self,
        model: Any,
        tokenizer: Any,
        client: BaseEnvClient,
        text: str,
        generation_config: Optional[Any] = None
    ) -> str:
        """
        Run Monte Carlo Tree Search to find the best action.
        
        Args:
            model: Language model
            tokenizer: Tokenizer
            client: Environment client
            text: Current conversation text
            generation_config: Generation configuration
            
        Returns:
            Best action as a string
        """
        # Generate candidate actions
        input_ids = tokenizer.encode(text, return_tensors="pt").to(model.device)
        
        # Generate multiple candidate actions
        candidate_actions = []
        for _ in range(5):  # Generate 5 candidate actions
            branch_generation_config = copy.deepcopy(generation_config)
            if hasattr(branch_generation_config, "temperature"):
                branch_generation_config.temperature = 0.7  # Adjust as needed
            
            output = model.generate(
                input_ids,
                generation_config=branch_generation_config
            )
            
            # Decode response
            generated_text = tokenizer.decode(
                output[0][input_ids.shape[1]:],
                skip_special_tokens=True
            )
            candidate_actions.append(generated_text)
        
        # Run simulations for each candidate action
        action_scores = {}
        for action in candidate_actions:
            total_reward = 0
            
            # Run multiple simulations for this action
            for _ in range(self.num_simulations // len(candidate_actions)):
                # Clone client for simulation
                sim_client = copy.deepcopy(client)
                
                # Take action
                step_output = sim_client.step(action)
                state, reward, done = step_output.state, step_output.reward, step_output.done
                
                # If not done, simulate random actions until done or limit reached
                sim_rounds = 0
                sim_reward = reward
                
                while not done and sim_rounds < 5:  # Limit simulation depth
                    # Generate a random action
                    sim_text = text + f"\nAssistant: {action}\nHuman: {state}"
                    sim_input_ids = tokenizer.encode(sim_text, return_tensors="pt").to(model.device)
                    
                    sim_output = model.generate(
                        sim_input_ids,
                        generation_config=generation_config
                    )
                    
                    sim_action = tokenizer.decode(
                        sim_output[0][sim_input_ids.shape[1]:],
                        skip_special_tokens=True
                    )
                    
                    # Take action in simulation
                    sim_step_output = sim_client.step(sim_action)
                    state, sim_reward, done = sim_step_output.state, sim_step_output.reward, sim_step_output.done
                    
                    sim_rounds += 1
                
                total_reward += sim_reward
            
            # Average reward across simulations
            action_scores[action] = total_reward / (self.num_simulations // len(candidate_actions))
        
        # Return action with highest score
        best_action = max(action_scores.items(), key=lambda x: x[1])[0]
        return best_action