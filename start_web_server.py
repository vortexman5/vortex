#!/usr/bin/env python3
"""
Start the Vortex AI web server.

This script starts the web server for the Vortex AI agent.
"""

import os
import sys
import uvicorn
import argparse

# Add the parent directory to the path to import openhands
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from openhands.server.listen import app

def main():
    """Start the web server."""
    parser = argparse.ArgumentParser(description="Start the Vortex AI web server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=12000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    print(f"Starting Vortex AI web server on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()