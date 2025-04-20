#!/usr/bin/env python3
"""
Vortex Agent Runner

This script provides a convenient way to run the Vortex agent in autonomous mode.
It uses the OpenHands CLI module to start an interactive Vortex session.
"""

import argparse
import sys
import os
import asyncio
from openhands.core.config.utils import get_parser, setup_config_from_args
from openhands.core.cli import main


def parse_arguments():
    """Parse command line arguments specific to the Vortex agent."""
    # Get the base parser from OpenHands
    parser = get_parser()
    
    # Add Vortex-specific arguments
    parser.add_argument(
        '--autonomous',
        action='store_true',
        help='Run the agent in autonomous mode without user interaction'
    )
    parser.add_argument(
        '--knowledge-dir',
        type=str,
        default='knowledge',
        help='Directory containing knowledge files for the agent'
    )
    parser.add_argument(
        '--memory-file',
        type=str,
        default=None,
        help='Path to a memory file to load for the agent'
    )
    
    return parser.parse_args()


def print_welcome_message():
    """Print a welcome message for the Vortex agent."""
    print("""
    __      __        _            
    \ \    / /       | |           
     \ \  / /__  _ __| |_ _____  __
      \ \/ / _ \| '__| __/ _ \ \/ /
       \  / (_) | |  | ||  __/>  < 
        \/ \___/|_|   \__\___/_/\_\\
                                   
    Vortex AI Agent v1.0.0
    
    Welcome to Vortex AI, your autonomous agent for knowledge processing.
    
    This agent can:
    - Process and ingest knowledge from various sources
    - Answer questions based on its knowledge base
    - Perform tasks autonomously
    - Learn and adapt to new information
    
    Type 'help' for a list of commands or 'exit' to quit.
    """)


def run_simple_agent(task):
    """Run a simple agent that responds to basic commands."""
    print_welcome_message()
    
    if task:
        print(f"\nTask: {task}\n")
        print("Response: I'm a Vortex AI agent that can help you with knowledge processing and autonomous tasks.")
        print("Currently, I'm running in a simplified mode without Docker support.")
        print("To use my full capabilities, please ensure Docker is installed and running.")
        print("\nFor now, I can demonstrate basic functionality and help you understand how to use the Vortex system.")
        print("You can find more information in the documentation directory.")
    
    print("\nExiting Vortex agent...")


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()
    
    # Check if Docker is available
    docker_available = False
    try:
        import docker
        client = docker.from_env()
        docker_available = True
    except:
        docker_available = False
    
    if docker_available:
        # Set up configuration
        config = setup_config_from_args(args)
        
        # If autonomous mode is enabled, set appropriate flags
        if args.autonomous:
            config.cli_auto_continue = True
            config.cli_headless = True
        
        # Run the agent
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main(loop))
        except KeyboardInterrupt:
            print("\nExiting Vortex agent...")
            sys.exit(0)
    else:
        # Run a simple version of the agent without Docker
        run_simple_agent(args.task)