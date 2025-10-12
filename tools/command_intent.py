#!/usr/bin/env python3
"""
Command Intent Mapper for ISA
Translates natural language commands into executable ISA commands using Ollama AI.
"""

import os
import sys
import json
import subprocess
import argparse
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tools.ollama_client import OllamaClient
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}", file=sys.stderr)
    OllamaClient = None


class CommandIntentMapper:
    """Maps natural language to ISA commands using AI."""
    
    # Define known ISA commands and their patterns
    COMMAND_PATTERNS = {
        'context-stats': {
            'aliases': ['ctx-stats'],
            'patterns': [
                'context stats',
                'context statistics',
                'how many chunks',
                'vector database stats',
                'show stats',
                'database stats'
            ],
            'description': 'Show vector database statistics'
        },
        'context-health': {
            'aliases': ['ctx-health'],
            'patterns': [
                'health',
                'check health',
                'health check',
                'services running',
                'everything ok',
                'everything healthy',
                'check status',
                'status check'
            ],
            'description': 'Check health of semantic context services'
        },
        'context-search': {
            'aliases': ['ctx-search'],
            'patterns': [
                'search for',
                'find',
                'look for',
                'search context',
                'semantic search'
            ],
            'description': 'Search contexts semantically',
            'requires_arg': True
        },
        'context-sync': {
            'aliases': ['ctx-sync'],
            'patterns': [
                'sync',
                'update contexts',
                'reindex',
                'process contexts',
                'refresh'
            ],
            'description': 'Sync all contexts to vector database'
        },
        'context-add': {
            'aliases': ['ctx-add'],
            'patterns': [
                'add context',
                'add file',
                'index file',
                'add this context'
            ],
            'description': 'Add a single context file',
            'requires_arg': True
        },
        'context-rebuild': {
            'aliases': ['ctx-rebuild'],
            'patterns': [
                'rebuild index',
                'rebuild database',
                'rebuild vector db',
                'start over'
            ],
            'description': 'Rebuild entire vector database index'
        },
        'ai-status': {
            'aliases': [],
            'patterns': [
                'ai status',
                'show ai status',
                'ai configuration',
                'ai info'
            ],
            'description': 'Show AI system status'
        }
    }
    
    def __init__(self, ollama_host: str = "http://192.168.1.161:11434", verbose: bool = False):
        """Initialize the command intent mapper."""
        self.verbose = verbose
        self.ollama_client = None
        
        if OllamaClient:
            try:
                self.ollama_client = OllamaClient(
                    host=ollama_host,
                    model="llama3.2:latest"
                )
                if self.verbose:
                    print(f"✅ Connected to Ollama at {ollama_host}", file=sys.stderr)
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Could not connect to Ollama: {e}", file=sys.stderr)
    
    def _get_command_context(self) -> str:
        """Generate context about available ISA commands for the AI."""
        context = "Available ISA commands:\n\n"
        
        for cmd, info in self.COMMAND_PATTERNS.items():
            context += f"Command: isa {cmd}\n"
            if info['aliases']:
                context += f"  Aliases: {', '.join(['isa ' + a for a in info['aliases']])}\n"
            context += f"  Description: {info['description']}\n"
            context += f"  Example patterns: {', '.join(info['patterns'][:3])}\n"
            if info.get('requires_arg'):
                context += "  Requires argument: Yes\n"
            context += "\n"
        
        return context
    
    def _build_intent_prompt(self, user_input: str) -> str:
        """Build prompt for AI to interpret command intent."""
        command_context = self._get_command_context()
        
        prompt = f"""You are a command interpreter for the ISA (Intelligent Shell Assistant) system.
Your job is to translate natural language requests into executable ISA commands.

{command_context}

User request: "{user_input}"

Analyze the user's request and determine:
1. Which ISA command they want to execute
2. What arguments (if any) are needed

Respond ONLY with a valid JSON object in this exact format:
{{
    "command": "isa command-name",
    "args": ["arg1", "arg2"],
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Rules:
- Use the SHORTEST form of the command (prefer ctx-* aliases)
- Extract any search terms, file paths, or parameters as args
- Set confidence between 0.0 (unsure) and 1.0 (certain)
- If unclear, set confidence below 0.5

Examples:
User: "show me context stats"
{{"command": "isa ctx-stats", "args": [], "confidence": 0.95, "reasoning": "Clear request for statistics"}}

User: "search for deployment procedures"
{{"command": "isa ctx-search", "args": ["deployment procedures"], "confidence": 0.9, "reasoning": "Search request with clear query"}}

User: "check if everything is healthy"
{{"command": "isa ctx-health", "args": [], "confidence": 0.85, "reasoning": "Health check request"}}

Now analyze the user's request and respond with JSON only."""

        return prompt
    
    def interpret_command(self, user_input: str) -> Dict:
        """
        Interpret natural language and map to ISA command.
        
        Returns:
            Dict with keys: command, args, confidence, reasoning
        """
        if not self.ollama_client:
            # Fallback to simple pattern matching if Ollama unavailable
            return self._fallback_interpret(user_input)
        
        try:
            # Use AI to interpret the command
            prompt = self._build_intent_prompt(user_input)
            
            response = self.ollama_client.generate(
                prompt=prompt,
                system="You are a precise command interpreter. Respond only with valid JSON.",
                temperature=0.1  # Low temperature for consistent parsing
            )
            
            # Parse the JSON response
            # Try to extract JSON from the response
            response_text = response.strip()
            
            # Handle code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            
            # Validate the result
            if not isinstance(result, dict) or 'command' not in result:
                raise ValueError("Invalid response format")
            
            # Ensure all required fields
            result.setdefault('args', [])
            result.setdefault('confidence', 0.5)
            result.setdefault('reasoning', 'Interpreted from natural language')
            
            if self.verbose:
                print(f"🤖 Interpreted: {result['command']} {' '.join(result['args'])}", file=sys.stderr)
                print(f"   Confidence: {result['confidence']:.2f}", file=sys.stderr)
                print(f"   Reasoning: {result['reasoning']}", file=sys.stderr)
            
            return result
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  AI interpretation failed: {e}", file=sys.stderr)
                print(f"   Falling back to pattern matching", file=sys.stderr)
            return self._fallback_interpret(user_input)
    
    def _fallback_interpret(self, user_input: str) -> Dict:
        """Fallback pattern matching when AI is unavailable."""
        user_lower = user_input.lower()
        
        # Check each command pattern
        for cmd, info in self.COMMAND_PATTERNS.items():
            for pattern in info['patterns']:
                if pattern in user_lower:
                    # Extract arguments if needed
                    args = []
                    if info.get('requires_arg'):
                        # Try to extract the argument after the pattern
                        parts = user_lower.split(pattern, 1)
                        if len(parts) > 1:
                            arg = parts[1].strip().strip('"\'')
                            if arg:
                                args = [arg]
                    
                    return {
                        'command': f"isa {info['aliases'][0] if info['aliases'] else cmd}",
                        'args': args,
                        'confidence': 0.7,
                        'reasoning': f"Pattern matched: {pattern}"
                    }
        
        # No match found
        return {
            'command': None,
            'args': [],
            'confidence': 0.0,
            'reasoning': 'No matching command pattern found'
        }
    
    def execute_command(self, command: str, args: List[str], dry_run: bool = False) -> Tuple[int, str, str]:
        """
        Execute an ISA command safely.
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not command:
            return 1, "", "No command to execute"
        
        # Build full command string
        cmd_parts = [command] + args
        cmd_str = ' '.join(cmd_parts)
        
        if dry_run:
            return 0, f"Would execute: {cmd_str}", ""
        
        try:
            # Get ISA_ROOT from environment
            isa_root = os.environ.get('ISA_ROOT', os.path.expanduser('~/projects/isa'))
            
            # Execute via shell to access isa function
            # Source isa.rc first to get access to the isa function
            shell_cmd = f"source {isa_root}/isa.rc > /dev/null 2>&1 && {cmd_str}"
            
            result = subprocess.run(
                shell_cmd,
                shell=True,
                executable='/bin/zsh',  # Use zsh as it's the user's shell
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out after 30 seconds"
        except Exception as e:
            return 1, "", f"Execution error: {e}"


def main():
    """Main entry point for command line usage."""
    parser = argparse.ArgumentParser(
        description="Interpret natural language and execute ISA commands"
    )
    parser.add_argument(
        'input',
        nargs='+',
        help='Natural language command to interpret'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running it'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed interpretation process'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )
    parser.add_argument(
        '--ollama-host',
        default='http://192.168.1.161:11434',
        help='Ollama server URL (default: http://192.168.1.161:11434)'
    )
    
    args = parser.parse_args()
    
    # Join input into single string
    user_input = ' '.join(args.input)
    
    # Create mapper
    mapper = CommandIntentMapper(
        ollama_host=args.ollama_host,
        verbose=args.verbose
    )
    
    # Interpret the command
    result = mapper.interpret_command(user_input)
    
    if args.json:
        # Output as JSON
        print(json.dumps(result, indent=2))
        return 0 if result['command'] else 1
    
    # Check confidence
    if result['confidence'] < 0.5:
        print(f"⚠️  Low confidence ({result['confidence']:.2f}): {result['reasoning']}", file=sys.stderr)
        if not result['command']:
            print("Could not interpret command. Try being more specific.", file=sys.stderr)
            return 1
    
    # Execute the command
    if result['command']:
        if args.verbose or args.dry_run:
            cmd_str = result['command'] + (' ' + ' '.join(result['args']) if result['args'] else '')
            print(f"➡️  Executing: {cmd_str}", file=sys.stderr)
        
        exit_code, stdout, stderr = mapper.execute_command(
            result['command'],
            result['args'],
            dry_run=args.dry_run
        )
        
        if stdout:
            print(stdout, end='')
        if stderr:
            print(stderr, end='', file=sys.stderr)
        
        return exit_code
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
