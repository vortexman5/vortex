"""
Common types for reinforcement learning in OpenHands.

This module defines common types used across the reinforcement learning module.
"""

from typing import Dict, List, Any, Optional


class ExperienceOutput:
    """
    Output from a reinforcement learning experience.
    
    Attributes:
        conversation: List of conversation messages
        reward: Final reward received
        text: Full text of the conversation
        seq_ids: Tokenized sequence IDs
        attention_mask: Attention mask for the sequence
        action_mask: Mask indicating action positions
    """
    
    def __init__(
        self,
        conversation: List[Dict[str, Any]],
        reward: float,
        text: str,
        seq_ids: List[int] = None,
        attention_mask: List[int] = None,
        action_mask: List[int] = None
    ):
        self.conversation = conversation
        self.reward = reward
        self.text = text
        self.seq_ids = seq_ids or []
        self.attention_mask = attention_mask or []
        self.action_mask = action_mask or []


class ConversationMessage(Dict[str, Any]):
    """A message in a conversation between an agent and an environment."""
    pass