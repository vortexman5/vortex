"""
Simple environment server for testing the reinforcement learning module.

This server implements a simple web-based environment for reinforcement learning.
It provides endpoints for resetting the environment and taking actions.
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


class ShoppingEnvironment:
    """
    Simple shopping environment for reinforcement learning.
    
    This environment simulates a shopping task where the agent needs to
    find a product that matches certain criteria.
    """
    
    def __init__(self):
        """Initialize the shopping environment."""
        self.products = [
            {
                "id": 1,
                "name": "Hiking Backpack",
                "price": 89.99,
                "description": "A durable backpack for hiking with multiple compartments.",
                "category": "Outdoor",
                "rating": 4.5,
                "in_stock": True
            },
            {
                "id": 2,
                "name": "Laptop Backpack",
                "price": 59.99,
                "description": "A sleek backpack designed for laptops up to 15 inches.",
                "category": "Electronics",
                "rating": 4.2,
                "in_stock": True
            },
            {
                "id": 3,
                "name": "Premium Hiking Backpack",
                "price": 129.99,
                "description": "A premium backpack for serious hikers with advanced features.",
                "category": "Outdoor",
                "rating": 4.8,
                "in_stock": True
            },
            {
                "id": 4,
                "name": "School Backpack",
                "price": 39.99,
                "description": "A simple backpack for school or casual use.",
                "category": "School",
                "rating": 3.9,
                "in_stock": True
            },
            {
                "id": 5,
                "name": "Travel Backpack",
                "price": 79.99,
                "description": "A versatile backpack for travel with expandable compartments.",
                "category": "Travel",
                "rating": 4.3,
                "in_stock": False
            }
        ]
        
        self.tasks = [
            {
                "id": 0,
                "description": "Find a hiking backpack under $100.",
                "target_product": 1,
                "initial_state": "You are shopping for a hiking backpack. You need to find one that costs less than $100."
            },
            {
                "id": 1,
                "description": "Find a laptop backpack with good ratings.",
                "target_product": 2,
                "initial_state": "You are shopping for a laptop backpack. You need to find one with a rating of at least 4.0."
            },
            {
                "id": 2,
                "description": "Find a backpack for school use.",
                "target_product": 4,
                "initial_state": "You are shopping for a school backpack. You need to find one that is suitable for daily school use."
            }
        ]
        
        self.current_task = None
        self.current_state = ""
        self.current_product = None
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
        self.current_product = None
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
        
        # Check if the action is to search for products
        if "search" in action or "find" in action or "look" in action:
            # Return a list of products
            product_list = "\n".join([
                f"- {p['name']}: ${p['price']:.2f}, {p['description']}" 
                for p in self.products if p["in_stock"]
            ])
            
            self.current_state = f"Here are the available products:\n{product_list}"
            reward = 0.1  # Small reward for searching
        
        # Check if the action is to view a specific product
        elif "view" in action or "details" in action or "info" in action:
            # Extract product name from action
            for product in self.products:
                if product["name"].lower() in action:
                    self.current_product = product
                    self.current_state = (
                        f"Product: {product['name']}\n"
                        f"Price: ${product['price']:.2f}\n"
                        f"Description: {product['description']}\n"
                        f"Category: {product['category']}\n"
                        f"Rating: {product['rating']}/5.0\n"
                        f"In Stock: {'Yes' if product['in_stock'] else 'No'}"
                    )
                    reward = 0.2  # Reward for viewing a product
                    break
            else:
                self.current_state = "I couldn't find that product. Please try again."
                reward = -0.1  # Penalty for invalid product
        
        # Check if the action is to purchase a product
        elif "buy" in action or "purchase" in action or "add to cart" in action or "select" in action:
            if self.current_product is None:
                # No product selected
                self.current_state = "Please view a product before trying to purchase it."
                reward = -0.1  # Penalty for invalid action
            else:
                # Check if this is the target product
                if self.current_product["id"] == self.current_task["target_product"]:
                    self.current_state = f"Great choice! You've purchased the {self.current_product['name']}."
                    reward = 1.0  # Big reward for correct purchase
                    self.done = True
                else:
                    self.current_state = f"You've purchased the {self.current_product['name']}, but it might not be the best choice for your needs."
                    reward = 0.3  # Small reward for any purchase
                    self.done = True
        
        # Check if the action is to filter products
        elif "filter" in action or "category" in action or "price" in action:
            category = None
            max_price = None
            
            # Extract category
            if "outdoor" in action:
                category = "Outdoor"
            elif "electronics" in action or "laptop" in action:
                category = "Electronics"
            elif "school" in action:
                category = "School"
            elif "travel" in action:
                category = "Travel"
            
            # Extract price
            if "under" in action or "less than" in action:
                if "$100" in action or "100" in action:
                    max_price = 100.0
                elif "$50" in action or "50" in action:
                    max_price = 50.0
                elif "$75" in action or "75" in action:
                    max_price = 75.0
            
            # Filter products
            filtered_products = self.products
            
            if category:
                filtered_products = [p for p in filtered_products if p["category"] == category]
            
            if max_price:
                filtered_products = [p for p in filtered_products if p["price"] < max_price]
            
            # Return filtered products
            if filtered_products:
                product_list = "\n".join([
                    f"- {p['name']}: ${p['price']:.2f}, {p['description']}" 
                    for p in filtered_products if p["in_stock"]
                ])
                
                self.current_state = f"Here are the filtered products:\n{product_list}"
                reward = 0.3  # Reward for good filtering
            else:
                self.current_state = "No products match your filters."
                reward = 0.1  # Small reward for filtering
        
        # Default response for other actions
        else:
            self.current_state = "I'm not sure how to respond to that. You can search for products, view details, filter by category or price, or make a purchase."
            reward = 0.0  # No reward for invalid action
        
        # Apply step penalty to encourage efficiency
        reward -= 0.05 * self.steps
        
        # Check if we've reached the maximum number of steps
        if self.steps >= 10:
            self.current_state += "\n\nYou've reached the maximum number of steps. Please make a decision."
            self.done = True
        
        return {
            "state": self.current_state,
            "reward": reward,
            "done": self.done
        }


# Create FastAPI app
app = FastAPI(title="RL Environment Server")

# Create environment
env = ShoppingEnvironment()


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
    return {"message": "RL Environment Server is running"}


def main():
    """Run the environment server."""
    parser = argparse.ArgumentParser(description="Run the RL environment server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()