"""
Example script for using the reinforcement learning module with a mock model.

This script demonstrates how to use the RL module with a mock model for coding tasks.
"""

import os
import sys
import random
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to import openhands
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openhands.rl.agent import RLAgent
from openhands.rl.controller import RLController
from openhands.rl.env import Environment
from openhands.rl.strategy import StandardReActStrategy


class MockModel:
    """Mock model for testing the RL module."""
    
    def __init__(self, name: str = "MockModel"):
        """Initialize the mock model."""
        self.name = name
    
    def generate(self, prompt: str) -> str:
        """Generate a response to a prompt."""
        # Simple mock responses based on the prompt
        if "analyze" in prompt.lower():
            return "I'll analyze this code. It looks like it has some issues with efficiency and error handling."
        elif "refactor" in prompt.lower():
            return "I'll refactor this code to improve efficiency by adding early termination and input validation."
        elif "test" in prompt.lower():
            return "I'll write tests for this code. We should test with empty inputs, normal cases, and edge cases."
        elif "debug" in prompt.lower():
            return "I'll debug this code. The main issues are lack of error handling and potential edge cases."
        elif "implement" in prompt.lower():
            return "I'll implement this feature. We'll need to add proper authentication and error handling."
        else:
            return "I'm not sure what to do with this prompt. Could you clarify?"


class SimpleCodingEnvironment(Environment):
    """Simple coding environment for testing the RL module."""
    
    def __init__(self):
        """Initialize the environment."""
        self.state = "You need to refactor a bubble sort algorithm to improve its efficiency."
        self.done = False
        self.reward = 0.0
        self.step_count = 0
    
    def reset(self) -> str:
        """Reset the environment."""
        self.state = "You need to refactor a bubble sort algorithm to improve its efficiency."
        self.done = False
        self.reward = 0.0
        self.step_count = 0
        return self.state
    
    def step(self, action: str) -> Dict[str, Any]:
        """Take a step in the environment."""
        self.step_count += 1
        
        # Parse the action
        action = action.lower()
        
        if "analyze" in action and "sort" in action:
            self.state = """
Code Analysis for Sorting Algorithm:

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

Issues identified:
- Inefficient algorithm
- No early termination
- No input validation
Complexity: O(n^2)
"""
            self.reward = 0.2
        
        elif "refactor" in action and "sort" in action:
            self.state = """
Great job! You've successfully refactored the Sorting Algorithm code.

Here's a possible refactored version:

```python
def bubble_sort(arr):
    if not arr or not isinstance(arr, list):
        return arr
    
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        # If no swapping occurred in this pass, array is sorted
        if not swapped:
            break
    return arr
```
"""
            self.reward = 1.0
            self.done = True
        
        elif "test" in action and "sort" in action:
            self.state = """
Here are some test cases for the Sorting Algorithm code:

```python
import unittest

class TestBubbleSort(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(bubble_sort([]), [])
    
    def test_sorted_list(self):
        self.assertEqual(bubble_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])
    
    def test_reverse_sorted_list(self):
        self.assertEqual(bubble_sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])
    
    def test_mixed_list(self):
        self.assertEqual(bubble_sort([3, 1, 4, 1, 5, 9, 2, 6, 5]), [1, 1, 2, 3, 4, 5, 5, 6, 9])

if __name__ == '__main__':
    unittest.main()
```
"""
            self.reward = 0.4
        
        elif "debug" in action and "sort" in action:
            self.state = """
Debugging the Sorting Algorithm code:

Issues found:
1. No input validation - could crash with None or non-list inputs
2. Inefficient algorithm - always runs O(n^2) even if array is already sorted
3. No early termination check - wastes computation time

Debugging steps:
1. Add input validation at the beginning
2. Add a 'swapped' flag to detect when the array is already sorted
3. Break early if no swaps occur in a pass
"""
            self.reward = 0.4
        
        else:
            self.state = "I'm not sure how to respond to that. You can analyze code, refactor code, test code, debug code, or implement new features."
            self.reward = 0.0
        
        # Apply step penalty
        self.reward -= 0.05 * self.step_count
        
        # Check if we've reached the maximum number of steps
        if self.step_count >= 5:
            self.state += "\n\nYou've reached the maximum number of steps. Please complete the task."
            self.done = True
        
        return {
            "state": self.state,
            "reward": self.reward,
            "done": self.done
        }


def main():
    """Run the example."""
    # Create a mock model
    model = MockModel()
    
    # Create an agent
    agent = RLAgent(model=model)
    
    # Create an environment
    env = SimpleCodingEnvironment()
    
    # Create a strategy
    strategy = StandardReActStrategy()
    
    # Create a controller
    controller = RLController(agent=agent, env=env, strategy=strategy)
    
    # Run the controller
    trajectory = controller.run()
    
    # Print the trajectory
    print("\nTrajectory:")
    for i, (state, action, reward, next_state, done) in enumerate(trajectory):
        print(f"\nStep {i+1}:")
        print(f"State: {state}")
        print(f"Action: {action}")
        print(f"Reward: {reward}")
        print(f"Next State: {next_state}")
        print(f"Done: {done}")
    
    # Print the total reward
    total_reward = sum(reward for _, _, reward, _, _ in trajectory)
    print(f"\nTotal Reward: {total_reward}")


if __name__ == "__main__":
    main()