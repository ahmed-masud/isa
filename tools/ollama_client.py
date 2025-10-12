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

# Try to import semantic context retrieval
try:
    from semantic_context import SemanticContextRetriever
    SEMANTIC_CONTEXT_AVAILABLE = True
except ImportError:
    SEMANTIC_CONTEXT_AVAILABLE = False
    print("Warning: Semantic context retrieval not available", file=sys.stderr)

# Configuration - matches the shell script defaults
DEFAULT_HOST = "http://192.168.1.161:11434"
DEFAULT_MODEL = "phi3:mini"
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_TOKENS = 1000
DEFAULT_VECTOR_SERVICE = "http://192.168.1.161:8000"


class OllamaClient:
    def __init__(self, host: str = None, model: str = None, timeout: int = None, 
                 vector_service_url: str = None, enable_semantic_context: bool = True):
        # Use environment variables or defaults
        self.host = host or os.environ.get('OLLAMA_HOST', DEFAULT_HOST)
        self.model = model or os.environ.get('AI_MODEL', DEFAULT_MODEL)
        self.timeout = timeout or int(os.environ.get('AI_TIMEOUT', DEFAULT_TIMEOUT))
        
        # Semantic context configuration
        self.vector_service_url = vector_service_url or os.environ.get('VECTOR_SERVICE_URL', DEFAULT_VECTOR_SERVICE)
        self.enable_semantic_context = enable_semantic_context and SEMANTIC_CONTEXT_AVAILABLE
        
        # Initialize semantic retriever if available
        self.semantic_retriever = None
        if self.enable_semantic_context:
            try:
                self.semantic_retriever = SemanticContextRetriever(self.vector_service_url)
                # Test connection
                if not self.semantic_retriever.test_connection():
                    print(f"Warning: Cannot connect to vector service at {self.vector_service_url}", file=sys.stderr)
                    self.enable_semantic_context = False
            except Exception as e:
                print(f"Warning: Failed to initialize semantic context: {e}", file=sys.stderr)
                self.enable_semantic_context = False
        
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
        """Query with context from a file (legacy method)"""
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
    
    def semantic_query(self, query: str, context_type: str = None, model: str = None, 
                      max_context_length: int = 2000) -> Optional[str]:
        """Query with semantic context retrieval from vector database"""
        if not query:
            raise ValueError("No query provided")
        
        # Use semantic context if available
        if self.enable_semantic_context and self.semantic_retriever:
            try:
                enhanced_prompt = self.semantic_retriever.build_enhanced_prompt(
                    user_query=query,
                    context_type=context_type,
                    max_context_length=max_context_length
                )
                return self.query(enhanced_prompt, model)
            except Exception as e:
                print(f"Warning: Semantic context retrieval failed: {e}", file=sys.stderr)
                # Fall back to basic query
                return self.query(query, model)
        else:
            # Fall back to basic query if semantic context is not available
            return self.query(query, model)
    
    def smart_query(self, query: str, context_type: str = None, context_file: str = None, 
                   model: str = None, prefer_semantic: bool = True) -> Optional[str]:
        """Intelligent query that chooses best context method available"""
        if not query:
            raise ValueError("No query provided")
        
        # Prefer semantic context if available and requested
        if prefer_semantic and self.enable_semantic_context:
            return self.semantic_query(query, context_type, model)
        
        # Fall back to file context if available
        elif context_file:
            return self.context_query(query, context_file, model)
        
        # Try semantic as fallback if file context not available
        elif self.enable_semantic_context:
            return self.semantic_query(query, context_type, model)
        
        # Final fallback to basic query
        else:
            return self.query(query, model)


def main():
    parser = argparse.ArgumentParser(description='Ollama API Client for ISA')
    parser.add_argument('prompt', nargs='?', help='The prompt to send to Ollama')
    parser.add_argument('--model', help='Model to use (default: phi3:mini)')
    parser.add_argument('--host', help='Ollama host URL (default: http://192.168.1.161:11434)')
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds (default: 30)')
    parser.add_argument('--context-file', help='File to use as context (legacy method)')
    parser.add_argument('--context-type', help='Semantic context type filter (person, project, priorities, etc.)')
    parser.add_argument('--vector-service', help='Vector service URL (default: http://192.168.1.161:8000)')
    parser.add_argument('--disable-semantic', action='store_true', help='Disable semantic context retrieval')
    parser.add_argument('--semantic-only', action='store_true', help='Use only semantic context (no file fallback)')
    parser.add_argument('--health-check', action='store_true', help='Check Ollama health')
    parser.add_argument('--list-models', action='store_true', help='List available models')
    parser.add_argument('--test-semantic', action='store_true', help='Test semantic context service')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create client
    client = OllamaClient(
        host=args.host, 
        model=args.model, 
        timeout=args.timeout,
        vector_service_url=args.vector_service,
        enable_semantic_context=not args.disable_semantic
    )
    
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
        
        if args.test_semantic:
            if client.enable_semantic_context:
                print("✅ Semantic context service is available")
                # Test with a simple query
                stats = client.semantic_retriever.get_service_stats()
                print(f"📊 Vector database stats: {stats}")
            else:
                print("❌ Semantic context service is not available")
            sys.exit(0)
        
        # Main query
        if not args.prompt:
            parser.error('Prompt is required for query operations')
        
        # Choose query method based on arguments
        if args.semantic_only:
            # Force semantic query only
            response = client.semantic_query(args.prompt, args.context_type)
        elif args.context_file and args.disable_semantic:
            # Force file context only
            response = client.context_query(args.prompt, args.context_file)
        elif args.context_file or client.enable_semantic_context:
            # Smart query with both options available
            response = client.smart_query(
                query=args.prompt,
                context_type=args.context_type,
                context_file=args.context_file,
                prefer_semantic=not args.disable_semantic
            )
        else:
            # Basic query without context
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