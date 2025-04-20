#!/usr/bin/env python3
"""
Vortex AI Web Interface

This script provides a web interface for the Vortex AI agent.
"""

import os
import sys
import subprocess
import threading
import time
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Store conversation history
conversation_history = []

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message and return a response."""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Add user message to conversation history
    conversation_history.append({'role': 'user', 'content': user_message})
    
    # Process the message using the Vortex agent
    response = process_message(user_message)
    
    # Add agent response to conversation history
    conversation_history.append({'role': 'assistant', 'content': response})
    
    return jsonify({
        'response': response,
        'history': conversation_history
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get the conversation history."""
    return jsonify({'history': conversation_history})

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear the conversation history."""
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'success'})

def process_message(message):
    """Process a message using the Vortex agent."""
    try:
        # Run the Vortex agent with the message as a task
        result = subprocess.run(
            ['python', 'run_agent.py', '-t', message],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract the response from the output
        output = result.stdout
        
        # Parse the output to extract just the response part
        response_lines = []
        capture = False
        for line in output.split('\n'):
            if line.startswith('Response:'):
                capture = True
                # Skip the "Response:" part
                response_lines.append(line[9:].strip())
            elif line.startswith('Exiting Vortex agent...'):
                capture = False
            elif capture:
                response_lines.append(line.strip())
        
        response = '\n'.join(response_lines)
        return response.strip() or "I couldn't generate a response. Please try again."
    
    except subprocess.CalledProcessError as e:
        print(f"Error running Vortex agent: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return "An error occurred while processing your request. Please try again."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again."

if __name__ == '__main__':
    # Create the templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Create the static directory
    os.makedirs('static', exist_ok=True)
    
    # Get the port from the environment or use default
    port = int(os.environ.get('PORT', 12000))
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=True)