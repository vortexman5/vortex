"""
Simple coding environment server for testing the reinforcement learning module.

This server implements a simple web-based environment for reinforcement learning
with coding tasks. It provides endpoints for resetting the environment and taking actions.
"""

import argparse
import json
import random
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


class ActionRequest(BaseModel):
    """Request model for taking an action."""
    action: str
    idx: int = 0


class ResetRequest(BaseModel):
    """Request model for resetting the environment."""
    idx: int = 0


class CodingEnvironment:
    """
    Simple coding environment for reinforcement learning.
    
    This environment simulates coding tasks where the agent needs to
    analyze, refactor, test, debug, or implement code.
    """
    
    def __init__(self):
        """Initialize the coding environment."""
        self.code_samples = [
            {
                "id": 1,
                "name": "Sorting Algorithm",
                "language": "Python",
                "code": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr""",
                "issues": ["Inefficient algorithm", "No early termination", "No input validation"],
                "complexity": "O(n^2)"
            },
            {
                "id": 2,
                "name": "API Client",
                "language": "Python",
                "code": """import requests

def get_data(url):
    response = requests.get(url)
    return response.json()

def post_data(url, data):
    response = requests.post(url, json=data)
    return response.json()""",
                "issues": ["No error handling", "No timeout", "No authentication"],
                "complexity": "Low"
            },
            {
                "id": 3,
                "name": "Database Connection",
                "language": "Python",
                "code": """import sqlite3

def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def execute_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()""",
                "issues": ["Connection not closed", "SQL injection vulnerability", "No error handling"],
                "complexity": "Medium"
            },
            {
                "id": 4,
                "name": "File Parser",
                "language": "Python",
                "code": """def parse_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            data.append(line.strip().split(','))
    return data""",
                "issues": ["No header handling", "No type conversion", "No error handling for file not found"],
                "complexity": "Low"
            },
            {
                "id": 5,
                "name": "Web Scraper",
                "language": "Python",
                "code": """import requests
from bs4 import BeautifulSoup

def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup""",
                "issues": ["No error handling", "No user-agent", "No rate limiting"],
                "complexity": "Medium"
            }
        ]
        
        self.tasks = [
            {
                "id": 0,
                "description": "Refactor the sorting algorithm to improve efficiency.",
                "target_code": 1,
                "initial_state": "You need to refactor a bubble sort algorithm to improve its efficiency. The current implementation has no early termination check."
            },
            {
                "id": 1,
                "description": "Add error handling to the API client.",
                "target_code": 2,
                "initial_state": "You need to add proper error handling to an API client. The current implementation doesn't handle exceptions or timeouts."
            },
            {
                "id": 2,
                "description": "Fix security issues in the database connection code.",
                "target_code": 3,
                "initial_state": "You need to fix security issues in a database connection module. The current implementation has SQL injection vulnerabilities."
            }
        ]
        
        self.current_task = None
        self.current_state = ""
        self.current_code = None
        self.done = False
        self.steps = 0
    
    def reset(self, idx: int = 0) -> Dict[str, Any]:
        """
        Reset the environment to a specific task.
        
        Args:
            idx: Index of the task to reset to
            
        Returns:
            Dictionary with the initial state
        """
        if idx >= len(self.tasks):
            idx = 0
        
        self.current_task = self.tasks[idx]
        self.current_state = self.current_task["initial_state"]
        self.current_code = None
        self.done = False
        self.steps = 0
        
        return {
            "state": self.current_state,
            "reward": 0.0,
            "done": self.done
        }
    
    def step(self, action: str) -> Dict[str, Any]:
        """
        Take an action in the environment.
        
        Args:
            action: The action to take, as a string
            
        Returns:
            Dictionary with the new state, reward, and done flag
        """
        self.steps += 1
        reward = 0.0
        
        # Parse the action
        action = action.lower()
        
        # Check if the action is to analyze code
        if "analyze" in action:
            # Find the code sample mentioned in the action
            for code in self.code_samples:
                if code["name"].lower() in action.lower():
                    self.current_code = code
                    issues = ", ".join(code["issues"])
                    self.current_state = (
                        f"Code Analysis for {code['name']}:\n\n"
                        f"```{code['language']}\n{code['code']}\n```\n\n"
                        f"Issues identified:\n- {issues}\n"
                        f"Complexity: {code['complexity']}"
                    )
                    reward = 0.2  # Reward for analyzing code
                    break
            else:
                self.current_state = "I couldn't find that code sample. Please try again."
                reward = -0.1  # Penalty for invalid code sample
        
        # Check if the action is to refactor code
        elif "refactor" in action:
            if self.current_code is None:
                # No code selected
                self.current_state = "Please analyze a code sample before trying to refactor it."
                reward = -0.1  # Penalty for invalid action
            else:
                # Check if this is the target code for refactoring
                if self.current_code["id"] == self.current_task["target_code"] and "refactor" in self.current_task["description"].lower():
                    self.current_state = (
                        f"Great job! You've successfully refactored the {self.current_code['name']} code.\n\n"
                        f"Here's a possible refactored version:\n\n"
                    )
                    
                    # Add refactored code based on the current code
                    if self.current_code["id"] == 1:  # Sorting algorithm
                        self.current_state += (
                            "```python\n"
                            "def bubble_sort(arr):\n"
                            "    if not arr or not isinstance(arr, list):\n"
                            "        return arr\n"
                            "    \n"
                            "    n = len(arr)\n"
                            "    for i in range(n):\n"
                            "        swapped = False\n"
                            "        for j in range(0, n - i - 1):\n"
                            "            if arr[j] > arr[j + 1]:\n"
                            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
                            "                swapped = True\n"
                            "        # If no swapping occurred in this pass, array is sorted\n"
                            "        if not swapped:\n"
                            "            break\n"
                            "    return arr\n"
                            "```"
                        )
                    elif self.current_code["id"] == 2:  # API Client
                        self.current_state += (
                            "```python\n"
                            "import requests\n"
                            "from requests.exceptions import RequestException\n"
                            "\n"
                            "def get_data(url, timeout=10, headers=None):\n"
                            "    try:\n"
                            "        response = requests.get(url, timeout=timeout, headers=headers)\n"
                            "        response.raise_for_status()\n"
                            "        return response.json()\n"
                            "    except RequestException as e:\n"
                            "        print(f\"Error fetching data: {e}\")\n"
                            "        return None\n"
                            "\n"
                            "def post_data(url, data, timeout=10, headers=None):\n"
                            "    try:\n"
                            "        response = requests.post(url, json=data, timeout=timeout, headers=headers)\n"
                            "        response.raise_for_status()\n"
                            "        return response.json()\n"
                            "    except RequestException as e:\n"
                            "        print(f\"Error posting data: {e}\")\n"
                            "        return None\n"
                            "```"
                        )
                    elif self.current_code["id"] == 3:  # Database Connection
                        self.current_state += (
                            "```python\n"
                            "import sqlite3\n"
                            "\n"
                            "def connect_db(db_path):\n"
                            "    try:\n"
                            "        conn = sqlite3.connect(db_path)\n"
                            "        return conn\n"
                            "    except sqlite3.Error as e:\n"
                            "        print(f\"Database connection error: {e}\")\n"
                            "        return None\n"
                            "\n"
                            "def execute_query(conn, query, params=()):\n"
                            "    try:\n"
                            "        cursor = conn.cursor()\n"
                            "        cursor.execute(query, params)  # Use parameterized queries to prevent SQL injection\n"
                            "        return cursor.fetchall()\n"
                            "    except sqlite3.Error as e:\n"
                            "        print(f\"Query execution error: {e}\")\n"
                            "        return None\n"
                            "    finally:\n"
                            "        cursor.close()\n"
                            "\n"
                            "def close_connection(conn):\n"
                            "    if conn:\n"
                            "        conn.close()\n"
                            "```"
                        )
                    
                    reward = 1.0  # Big reward for correct refactoring
                    self.done = True
                else:
                    self.current_state = (
                        f"You've attempted to refactor the {self.current_code['name']} code, "
                        f"but this might not be the task you were asked to complete."
                    )
                    reward = 0.3  # Small reward for any refactoring
        
        # Check if the action is to test code
        elif "test" in action:
            if self.current_code is None:
                # No code selected
                self.current_state = "Please analyze a code sample before trying to test it."
                reward = -0.1  # Penalty for invalid action
            else:
                # Generate test cases based on the current code
                self.current_state = f"Here are some test cases for the {self.current_code['name']} code:\n\n"
                
                if self.current_code["id"] == 1:  # Sorting algorithm
                    self.current_state += (
                        "```python\n"
                        "import unittest\n"
                        "\n"
                        "class TestBubbleSort(unittest.TestCase):\n"
                        "    def test_empty_list(self):\n"
                        "        self.assertEqual(bubble_sort([]), [])\n"
                        "    \n"
                        "    def test_sorted_list(self):\n"
                        "        self.assertEqual(bubble_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])\n"
                        "    \n"
                        "    def test_reverse_sorted_list(self):\n"
                        "        self.assertEqual(bubble_sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])\n"
                        "    \n"
                        "    def test_mixed_list(self):\n"
                        "        self.assertEqual(bubble_sort([3, 1, 4, 1, 5, 9, 2, 6, 5]), [1, 1, 2, 3, 4, 5, 5, 6, 9])\n"
                        "\n"
                        "if __name__ == '__main__':\n"
                        "    unittest.main()\n"
                        "```"
                    )
                elif self.current_code["id"] == 2:  # API Client
                    self.current_state += (
                        "```python\n"
                        "import unittest\n"
                        "from unittest.mock import patch, Mock\n"
                        "\n"
                        "class TestAPIClient(unittest.TestCase):\n"
                        "    @patch('requests.get')\n"
                        "    def test_get_data_success(self, mock_get):\n"
                        "        # Setup mock response\n"
                        "        mock_response = Mock()\n"
                        "        mock_response.json.return_value = {'key': 'value'}\n"
                        "        mock_get.return_value = mock_response\n"
                        "        \n"
                        "        # Call the function\n"
                        "        result = get_data('https://api.example.com/data')\n"
                        "        \n"
                        "        # Assert the result\n"
                        "        self.assertEqual(result, {'key': 'value'})\n"
                        "        mock_get.assert_called_once_with('https://api.example.com/data')\n"
                        "    \n"
                        "    @patch('requests.get')\n"
                        "    def test_get_data_failure(self, mock_get):\n"
                        "        # Setup mock to raise an exception\n"
                        "        mock_get.side_effect = requests.exceptions.RequestException('API error')\n"
                        "        \n"
                        "        # Call the function\n"
                        "        result = get_data('https://api.example.com/data')\n"
                        "        \n"
                        "        # Assert the result\n"
                        "        self.assertIsNone(result)\n"
                        "\n"
                        "if __name__ == '__main__':\n"
                        "    unittest.main()\n"
                        "```"
                    )
                
                # Check if this is the target code for testing
                if self.current_code["id"] == self.current_task["target_code"] and "test" in self.current_task["description"].lower():
                    reward = 1.0  # Big reward for correct testing
                    self.done = True
                else:
                    reward = 0.4  # Medium reward for any testing
        
        # Check if the action is to debug code
        elif "debug" in action:
            if self.current_code is None:
                # No code selected
                self.current_state = "Please analyze a code sample before trying to debug it."
                reward = -0.1  # Penalty for invalid action
            else:
                # Generate debugging information based on the current code
                self.current_state = f"Debugging the {self.current_code['name']} code:\n\n"
                
                if self.current_code["id"] == 1:  # Sorting algorithm
                    self.current_state += (
                        "Issues found:\n"
                        "1. No input validation - could crash with None or non-list inputs\n"
                        "2. Inefficient algorithm - always runs O(n^2) even if array is already sorted\n"
                        "3. No early termination check - wastes computation time\n\n"
                        "Debugging steps:\n"
                        "1. Add input validation at the beginning\n"
                        "2. Add a 'swapped' flag to detect when the array is already sorted\n"
                        "3. Break early if no swaps occur in a pass\n"
                    )
                elif self.current_code["id"] == 2:  # API Client
                    self.current_state += (
                        "Issues found:\n"
                        "1. No error handling - will crash on network errors or invalid responses\n"
                        "2. No timeout - could hang indefinitely on slow connections\n"
                        "3. No status code checking - doesn't verify successful responses\n\n"
                        "Debugging steps:\n"
                        "1. Add try-except blocks to catch RequestException\n"
                        "2. Add timeout parameter to requests\n"
                        "3. Use response.raise_for_status() to check for HTTP errors\n"
                    )
                
                # Check if this is the target code for debugging
                if self.current_code["id"] == self.current_task["target_code"] and "debug" in self.current_task["description"].lower():
                    reward = 1.0  # Big reward for correct debugging
                    self.done = True
                else:
                    reward = 0.4  # Medium reward for any debugging
        
        # Check if the action is to implement a feature
        elif "implement" in action:
            # Generate implementation based on the action
            if "authentication" in action:
                self.current_state = (
                    "Here's an implementation of authentication for an API client:\n\n"
                    "```python\n"
                    "import requests\n"
                    "from requests.auth import HTTPBasicAuth\n"
                    "\n"
                    "class APIClient:\n"
                    "    def __init__(self, base_url, api_key=None, username=None, password=None):\n"
                    "        self.base_url = base_url\n"
                    "        self.api_key = api_key\n"
                    "        self.username = username\n"
                    "        self.password = password\n"
                    "        self.session = requests.Session()\n"
                    "    \n"
                    "    def get(self, endpoint, params=None, timeout=10):\n"
                    "        url = f\"{self.base_url}/{endpoint}\"\n"
                    "        headers = {}\n"
                    "        auth = None\n"
                    "        \n"
                    "        # Add API key authentication if provided\n"
                    "        if self.api_key:\n"
                    "            headers['Authorization'] = f'Bearer {self.api_key}'\n"
                    "        \n"
                    "        # Add basic authentication if provided\n"
                    "        if self.username and self.password:\n"
                    "            auth = HTTPBasicAuth(self.username, self.password)\n"
                    "        \n"
                    "        try:\n"
                    "            response = self.session.get(\n"
                    "                url, \n"
                    "                params=params, \n"
                    "                headers=headers, \n"
                    "                auth=auth, \n"
                    "                timeout=timeout\n"
                    "            )\n"
                    "            response.raise_for_status()\n"
                    "            return response.json()\n"
                    "        except requests.exceptions.RequestException as e:\n"
                    "            print(f\"Error: {e}\")\n"
                    "            return None\n"
                    "```"
                )
                reward = 0.5  # Reward for implementation
            elif "database" in action:
                self.current_state = (
                    "Here's an implementation of a secure database connection:\n\n"
                    "```python\n"
                    "import sqlite3\n"
                    "from contextlib import contextmanager\n"
                    "\n"
                    "class Database:\n"
                    "    def __init__(self, db_path):\n"
                    "        self.db_path = db_path\n"
                    "    \n"
                    "    @contextmanager\n"
                    "    def connection(self):\n"
                    "        conn = None\n"
                    "        try:\n"
                    "            conn = sqlite3.connect(self.db_path)\n"
                    "            yield conn\n"
                    "        except sqlite3.Error as e:\n"
                    "            print(f\"Database error: {e}\")\n"
                    "            if conn:\n"
                    "                conn.rollback()\n"
                    "            raise\n"
                    "        finally:\n"
                    "            if conn:\n"
                    "                conn.close()\n"
                    "    \n"
                    "    def execute_query(self, query, params=()):\n"
                    "        with self.connection() as conn:\n"
                    "            cursor = conn.cursor()\n"
                    "            cursor.execute(query, params)  # Parameterized query prevents SQL injection\n"
                    "            return cursor.fetchall()\n"
                    "    \n"
                    "    def execute_update(self, query, params=()):\n"
                    "        with self.connection() as conn:\n"
                    "            cursor = conn.cursor()\n"
                    "            cursor.execute(query, params)\n"
                    "            conn.commit()\n"
                    "            return cursor.rowcount\n"
                    "```"
                )
                reward = 0.5  # Reward for implementation
            else:
                self.current_state = (
                    "Please specify what feature you'd like to implement. "
                    "For example: 'implement authentication' or 'implement database connection'."
                )
                reward = 0.1  # Small reward for attempting implementation
        
        # Default response for other actions
        else:
            self.current_state = (
                "I'm not sure how to respond to that. You can analyze code, refactor code, "
                "test code, debug code, or implement new features."
            )
            reward = 0.0  # No reward for invalid action
        
        # Apply step penalty to encourage efficiency
        reward -= 0.05 * self.steps
        
        # Check if we've reached the maximum number of steps
        if self.steps >= 10:
            self.current_state += "\n\nYou've reached the maximum number of steps. Please complete the task."
            self.done = True
        
        return {
            "state": self.current_state,
            "reward": reward,
            "done": self.done
        }


# Create FastAPI app
app = FastAPI(title="RL Coding Environment Server")

# Create environment
env = CodingEnvironment()


@app.post("/reset")
async def reset_environment(request: ResetRequest):
    """Reset the environment to a specific task."""
    return env.reset(request.idx)


@app.post("/step")
async def take_action(request: ActionRequest):
    """Take an action in the environment."""
    return env.step(request.action)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RL Coding Environment Server is running"}


def main():
    """Run the environment server."""
    parser = argparse.ArgumentParser(description="Run the RL coding environment server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=12000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()