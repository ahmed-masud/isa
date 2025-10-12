#!/usr/bin/env python3
"""
ISA-Ollama Integration - Pure Python Client
Replaces the shell-based ollama_query function with a more reliable Python implementation
"""

import json
import sys
import requests
import argparse
from typing import Optional, Dict, Any
import os

# Configuration - matches the shell script defaults
DEFAULT_HOST = "http://192.168.1.161:11434"
DEFAULT_MODEL = "phi3:mini"
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_TOKENS = 1000


class OllamaClient:
    def __init__(self, host: str = None, model: str = None, timeout: int = None):
        # Use environment variables or defaults
        self.host = host or os.environ.get('OLLAMA_HOST', DEFAULT_HOST)
        self.model = model or os.environ.get('AI_MODEL', DEFAULT_MODEL)
        self.timeout = timeout or int(os.environ.get('AI_TIMEOUT', DEFAULT_TIMEOUT))
        
        # Ensure host has proper format
        if not self.host.startswith('http'):
            self.host = f'http://{self.host}'
        if not self.host.endswith(':11434'):
            if ':' not in self.host.replace('http://', '').replace('https://', ''):
                self.host = f'{self.host}:11434'
    
    def health_check(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException:
            return []
    
    def query(self, prompt: str, model: str = None, stream: bool = False) -> Optional[str]:
        """Query Ollama with a prompt"""
        if not prompt:
            raise ValueError("No prompt provided")
        
        if not self.health_check():
            raise ConnectionError(f"Cannot connect to Ollama at {self.host}")
        
        # Prepare request
        model_to_use = model or self.model
        payload = {
            "model": model_to_use,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            return data.get('response', '')
            
        except requests.Timeout:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        except requests.RequestException as e:
            raise ConnectionError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def context_query(self, query: str, context_file: str = None, model: str = None) -> Optional[str]:
        """Query with context from a file"""
        if not query:
            raise ValueError("No query provided")
        
        full_prompt = query
        if context_file and os.path.isfile(context_file):
            try:
                with open(context_file, 'r') as f:
                    # Read first 50 lines as per original shell script
                    context_lines = []
                    for i, line in enumerate(f):
                        if i >= 50:
                            break
                        context_lines.append(line.rstrip())
                    context_data = '\n'.join(context_lines)
                
                full_prompt = f"""Context: {context_data}

Query: {query}

Please provide a helpful response based on the context provided."""
            except IOError:
                # Fall back to query without context
                pass
        
        return self.query(full_prompt, model)


def main():
    parser = argparse.ArgumentParser(description='Ollama API Client for ISA')
    parser.add_argument('prompt', nargs='?', help='The prompt to send to Ollama')
    parser.add_argument('--model', help='Model to use (default: phi3:mini)')
    parser.add_argument('--host', help='Ollama host URL (default: http://192.168.1.161:11434)')
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds (default: 30)')
    parser.add_argument('--context-file', help='File to use as context')
    parser.add_argument('--health-check', action='store_true', help='Check Ollama health')
    parser.add_argument('--list-models', action='store_true', help='List available models')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create client
    client = OllamaClient(host=args.host, model=args.model, timeout=args.timeout)
    
    try:
        if args.health_check:
            if client.health_check():
                print("✅ Ollama is accessible")
                sys.exit(0)
            else:
                print("❌ Cannot connect to Ollama")
                sys.exit(1)
        
        if args.list_models:
            models = client.list_models()
            if models:
                for model in models:
                    print(model)
            else:
                print("No models available")
            sys.exit(0)
        
        # Main query
        if not args.prompt:
            parser.error('Prompt is required for query operations')
        
        if args.context_file:
            response = client.context_query(args.prompt, args.context_file)
        else:
            response = client.query(args.prompt)
        
        if response:
            print(response)
        else:
            print("Empty response received", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()