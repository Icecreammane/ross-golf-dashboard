#!/usr/bin/env python3
"""
Helper script to route tasks to local Ollama models
Usage: python3 use_local_model.py <task_type> <prompt>
"""

import sys
import subprocess
import json

# Model routing configuration
MODEL_ROUTING = {
    "code": "qwen2.5:32b-instruct-q4_K_M",  # Best for code generation
    "content": "qwen2.5:32b-instruct-q4_K_M",  # Good for writing
    "research": "qwen2.5:32b-instruct-q4_K_M",  # Summary and analysis
    "chat": "qwen2.5:14b",  # Faster for simple tasks
    "fast": "llama3.1:8b",  # Quickest responses
}

def run_local_model(model, prompt):
    """Run Ollama model with given prompt"""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Error: Model timeout (60s exceeded)"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 use_local_model.py <task_type> <prompt>")
        print(f"Task types: {', '.join(MODEL_ROUTING.keys())}")
        sys.exit(1)
    
    task_type = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    
    if task_type not in MODEL_ROUTING:
        print(f"Unknown task type: {task_type}")
        print(f"Available: {', '.join(MODEL_ROUTING.keys())}")
        sys.exit(1)
    
    model = MODEL_ROUTING[task_type]
    print(f"Using model: {model}")
    print(f"Prompt: {prompt}\n")
    print("=" * 60)
    
    response = run_local_model(model, prompt)
    print(response)

if __name__ == "__main__":
    main()
