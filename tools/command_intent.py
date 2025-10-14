#!/usr/bin/env python3
"""
Command Intent Mapper for ISA
Translates natural language commands into executable ISA commands using Ollama AI.
Supports imperative commands and contextual references.
"""

import os
import sys
import json
import subprocess
import argparse
import re
import signal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tools.ollama_client import OllamaClient
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}", file=sys.stderr)
    OllamaClient = None


class CommandHistory:
    """Tracks command execution history for contextual references."""
    
    def __init__(self, history_file: str = None):
        """Initialize command history."""
        if history_file is None:
            isa_config = os.environ.get('ISA_CONFIG', os.path.expanduser('~/.config/isa'))
            history_file = os.path.join(isa_config, '.command_history.json')
        
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load command history from file."""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_history(self):
        """Save command history to file."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-100:], f, indent=2)  # Keep last 100 commands
        except Exception as e:
            print(f"Warning: Could not save history: {e}", file=sys.stderr)
    
    def add(self, command: str, args: List[str], pid: int = None):
        """Add a command to history."""
        import time
        entry = {
            'timestamp': time.time(),
            'command': command,
            'args': args,
            'pid': pid
        }
        self.history.append(entry)
        self._save_history()
    
    def get_last(self, n: int = 1) -> Optional[Dict]:
        """Get the last n commands."""
        if len(self.history) < n:
            return None
        return self.history[-n]
    
    def get_previous(self) -> Optional[Dict]:
        """Get the previous command."""
        return self.get_last(1)


class CommandIntentMapper:
    """Maps natural language to ISA commands using AI."""
    
    # Imperative verb mappings for direct commands
    # Format: verb -> (command, requires_arg)
    IMPERATIVE_VERBS = {
        'show': ('me', False),  # Default to showing personal priorities
        'display': ('me', False),
        'list': ('me', False),
        'check': ('ctx-health', False),
        'verify': ('ctx-health', False),
        'search': ('ctx-search', True),
        'find': ('ctx-search', True),
        'locate': ('ctx-search', True),
        'sync': ('ctx-sync', False),
        'update': ('ctx-sync', False),
        'refresh': ('ctx-sync', False),
        'rebuild': ('ctx-rebuild', False),
        'recreate': ('ctx-rebuild', False),
        'add': ('ctx-add', True),
        'index': ('ctx-add', True),
        'switch': ('ai-switch', True),
        'use': ('ai-switch', True),
        'push': ('context-push', True),
        'pop': ('context-pop', False),
        'back': ('context-pop', False),
        'return': ('context-pop', False),
    }
    
    # Object/noun mappings to refine imperative commands
    OBJECT_REFINEMENTS = {
        # Stats and status
        'stats': 'ctx-stats',
        'statistics': 'ctx-stats',
        'status': 'status',
        'health': 'ctx-health',
        'dashboard': 'status',
        
        # Personal workflow
        'priorities': 'me',
        'priority': 'me', 
        'tasks': 'me',
        'urgent': 'urgent',
        'urgent priorities': 'urgent',
        'urgent tasks': 'urgent',
        'week': 'week',
        'weekly': 'week',
        'month': 'month',
        'monthly': 'month',
        'todo': 'todo',
        'todos': 'todo',
        
        # Context operations
        'contexts': 'ctx-sync',
        'database': 'ctx-rebuild',
        'index': 'ctx-rebuild',
        
        # AI provider operations
        'providers': 'ai-providers',
        'ai providers': 'ai-providers',
        'models': 'ai-models',
        'ai models': 'ai-models',
        'ai status': 'ai-status',
        
        # Context stack operations
        'stack': 'context-stack',
        'context stack': 'context-stack',
        'breadcrumbs': 'context-breadcrumbs',
        'context trail': 'context-breadcrumbs',
        'previous context': 'context-pop',
        
        # Google Drive operations
        'google drive': 'drive-mount',
        'gdrive': 'drive-mount',
        'drive': 'drive-mount',
        'drive status': 'drive-status',
        'drives': 'drive-status',
    }
    
    # Contextual commands that reference history
    CONTEXTUAL_COMMANDS = {
        'stop': 'stop_process',
        'kill': 'kill_process',
        'halt': 'stop_process',
        'terminate': 'kill_process',
        'pause': 'pause_process',
        'resume': 'resume_process',
        'repeat': 'repeat_command',
        'redo': 'repeat_command',
        'again': 'repeat_command',
    }
    
    # Define known ISA commands and their patterns
    COMMAND_PATTERNS = {
        'me': {
            'aliases': ['my', 'self'],
            'patterns': [
                'my priorities',
                'my tasks',
                'show me my priorities',
                'what are my priorities',
                'personal priorities',
                'my current priorities'
            ],
            'description': 'Show your personal priorities'
        },
        'urgent': {
            'aliases': [],
            'patterns': [
                'urgent',
                'urgent priorities',
                'urgent tasks',
                'what is urgent',
                'show urgent',
                'urgent items',
                'critical tasks',
                'high priority',
                'what needs immediate attention'
            ],
            'description': 'Show urgent items'
        },
        'week': {
            'aliases': ['weekly'],
            'patterns': [
                'this week',
                'weekly tasks',
                'week priorities',
                'what this week',
                'weekly plan',
                'this weeks tasks'
            ],
            'description': 'Show this week\'s tasks'
        },
        'month': {
            'aliases': ['monthly'],
            'patterns': [
                'next month',
                'monthly plan',
                'month priorities',
                'monthly tasks',
                'what next month'
            ],
            'description': 'Show next month\'s plan'
        },
        'status': {
            'aliases': [],
            'patterns': [
                'status',
                'dashboard',
                'overview',
                'show status',
                'current status',
                'what is the status'
            ],
            'description': 'Show ISA status dashboard'
        },
        'todo': {
            'aliases': ['todos'],
            'patterns': [
                'todo',
                'todos',
                'todo list',
                'tasks',
                'all tasks',
                'show todos'
            ],
            'description': 'Show all TODO items'
        },
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
        },
        'ai-providers': {
            'aliases': ['providers'],
            'patterns': [
                'ai providers',
                'list providers',
                'show providers',
                'available providers',
                'which providers',
                'provider status'
            ],
            'description': 'List available AI providers'
        },
        'ai-switch': {
            'aliases': ['switch'],
            'patterns': [
                'switch provider',
                'switch to',
                'use provider',
                'change provider',
                'switch ai'
            ],
            'description': 'Switch to different AI provider',
            'requires_arg': True
        },
        'ai-models': {
            'aliases': ['models'],
            'patterns': [
                'ai models',
                'list models',
                'show models',
                'available models',
                'which models'
            ],
            'description': 'List available AI models for active provider'
        },
        'context-push': {
            'aliases': ['push'],
            'patterns': [
                'push context',
                'push to',
                'save context and load',
                'switch to temporarily',
                'temp switch to'
            ],
            'description': 'Push current context to stack and load new one',
            'requires_arg': True
        },
        'context-pop': {
            'aliases': ['pop'],
            'patterns': [
                'pop context',
                'go back',
                'return to previous',
                'restore context',
                'back to previous'
            ],
            'description': 'Pop context from stack and return to it'
        },
        'context-stack': {
            'aliases': ['stack'],
            'patterns': [
                'show stack',
                'context stack',
                'stack status',
                'what contexts',
                'show context stack'
            ],
            'description': 'Show current context stack'
        },
        'context-breadcrumbs': {
            'aliases': ['breadcrumbs'],
            'patterns': [
                'show breadcrumbs',
                'context trail',
                'where am i',
                'context path',
                'show context path'
            ],
            'description': 'Show context breadcrumb trail'
        },
        'drive-mount': {
            'aliases': ['mount', 'gdrive-mount'],
            'patterns': [
                'mount google drive',
                'mount drive',
                'connect google drive',
                'access google drive',
                'mount gdrive'
            ],
            'description': 'Mount Google Drive for current context'
        },
        'drive-unmount': {
            'aliases': ['unmount', 'gdrive-unmount'],
            'patterns': [
                'unmount google drive',
                'unmount drive',
                'disconnect google drive',
                'unmount gdrive'
            ],
            'description': 'Unmount Google Drive'
        },
        'drive-status': {
            'aliases': ['gdrive-status'],
            'patterns': [
                'drive status',
                'google drive status',
                'gdrive status',
                'show drives',
                'drive mounts'
            ],
            'description': 'Show Google Drive mount status'
        }
    }
    
    def __init__(self, ollama_host: str = "http://192.168.1.161:11434", verbose: bool = False):
        """Initialize the command intent mapper."""
        self.verbose = verbose
        self.ollama_client = None
        self.history = CommandHistory()
        
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
    
    def _parse_imperative(self, user_input: str) -> Optional[Dict]:
        """
        Parse imperative commands like 'show stats', 'check health'.
        Returns parsed command or None if not an imperative.
        """
        words = user_input.lower().strip().split()
        if len(words) == 0:
            return None
        
        # Try verb + object pattern (e.g., "show stats", "check health")
        if len(words) >= 2:
            verb = words[0]
            obj = ' '.join(words[1:])
            
            # Check if object directly maps to a command
            for keyword in self.OBJECT_REFINEMENTS:
                if keyword in obj:
                    return {
                        'command': f"isa {self.OBJECT_REFINEMENTS[keyword]}",
                        'args': [],
                        'confidence': 0.85,
                        'reasoning': f"Imperative: {verb} {keyword}"
                    }
            
            # Check if verb maps to a command
            if verb in self.IMPERATIVE_VERBS:
                cmd, requires_arg = self.IMPERATIVE_VERBS[verb]
                if requires_arg:
                    # Rest of the words are the argument
                    arg = ' '.join(words[1:])
                    return {
                        'command': f"isa {cmd}",
                        'args': [arg] if arg else [],
                        'confidence': 0.8,
                        'reasoning': f"Imperative verb: {verb}"
                    }
                else:
                    return {
                        'command': f"isa {cmd}",
                        'args': [],
                        'confidence': 0.8,
                        'reasoning': f"Imperative verb: {verb}"
                    }
        
        # Single verb (e.g., "sync", "rebuild")
        if len(words) == 1:
            verb = words[0]
            if verb in self.IMPERATIVE_VERBS:
                cmd, requires_arg = self.IMPERATIVE_VERBS[verb]
                if not requires_arg:
                    return {
                        'command': f"isa {cmd}",
                        'args': [],
                        'confidence': 0.75,
                        'reasoning': f"Single imperative: {verb}"
                    }
        
        return None
    
    def _parse_contextual(self, user_input: str) -> Optional[Dict]:
        """
        Parse contextual commands that reference history.
        E.g., 'stop the previous command', 'repeat last', 'kill it'.
        """
        words = user_input.lower().strip().split()
        if len(words) == 0:
            return None
        
        # Check for contextual action verbs
        action = None
        for word in words:
            if word in self.CONTEXTUAL_COMMANDS:
                action = self.CONTEXTUAL_COMMANDS[word]
                break
        
        if not action:
            return None
        
        # Determine which command to act on
        target_cmd = None
        
        # Look for references to previous/last/it
        if any(ref in words for ref in ['previous', 'last', 'it', 'that']):
            target_cmd = self.history.get_previous()
        
        if target_cmd is None:
            return {
                'command': None,
                'args': [],
                'confidence': 0.0,
                'reasoning': f"Contextual action '{action}' but no command in history"
            }
        
        return {
            'command': action,
            'args': [json.dumps(target_cmd)],
            'confidence': 0.9,
            'reasoning': f"Contextual: {action} on previous command"
        }
    
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
        
        prompt = f"""System: You are a precise command interpreter for the ISA (Intelligent Shell Assistant) system. Your job is to translate natural language requests into executable ISA commands. Respond ONLY with valid JSON.

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
- For personal workflow queries like "my priorities", "urgent tasks", use commands like "me", "urgent", "week"

Examples:
User: "show me context stats"
{{"command": "isa ctx-stats", "args": [], "confidence": 0.95, "reasoning": "Clear request for statistics"}}

User: "what are my urgent priorities"
{{"command": "isa urgent", "args": [], "confidence": 0.9, "reasoning": "Request for urgent items"}}

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
        # First, try contextual commands (highest priority)
        contextual = self._parse_contextual(user_input)
        if contextual and contextual.get('command'):
            return contextual
        
        # Second, try imperative commands
        imperative = self._parse_imperative(user_input)
        if imperative:
            return imperative
        
        # Third, try AI interpretation if available
        if not self.ollama_client:
            # Fallback to simple pattern matching if Ollama unavailable
            return self._fallback_interpret(user_input)
        
        try:
            # Use AI to interpret the command
            prompt = self._build_intent_prompt(user_input)
            
            response = self.ollama_client.query(
                prompt=prompt,
                model=self.ollama_client.model  # Use the configured model
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
    
    def _handle_contextual_action(self, action: str, target_cmd_json: str) -> Tuple[int, str, str]:
        """
        Handle contextual actions like stop, kill, repeat.
        """
        try:
            target_cmd = json.loads(target_cmd_json)
        except:
            return 1, "", "Could not parse target command"
        
        if action == 'stop_process' or action == 'kill_process':
            pid = target_cmd.get('pid')
            if not pid:
                return 1, "", "Previous command has no PID to stop"
            
            try:
                sig = signal.SIGTERM if action == 'stop_process' else signal.SIGKILL
                os.kill(pid, sig)
                action_name = "Stopped" if action == 'stop_process' else "Killed"
                return 0, f"{action_name} process {pid}", ""
            except ProcessLookupError:
                return 1, "", f"Process {pid} not found (may have already exited)"
            except PermissionError:
                return 1, "", f"Permission denied to stop process {pid}"
            except Exception as e:
                return 1, "", f"Error stopping process: {e}"
        
        elif action == 'repeat_command':
            cmd = target_cmd.get('command')
            args = target_cmd.get('args', [])
            if not cmd:
                return 1, "", "No command to repeat"
            print(f"🔁 Repeating: {cmd} {' '.join(args)}", file=sys.stderr)
            return self.execute_command(cmd, args, dry_run=False)
        
        else:
            return 1, "", f"Unknown contextual action: {action}"
    
    def execute_command(self, command: str, args: List[str], dry_run: bool = False) -> Tuple[int, str, str]:
        """
        Execute an ISA command safely.
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not command:
            return 1, "", "No command to execute"
        
        # Handle contextual actions
        if command in ['stop_process', 'kill_process', 'repeat_command']:
            if dry_run:
                return 0, f"Would execute contextual action: {command}", ""
            if len(args) > 0:
                return self._handle_contextual_action(command, args[0])
            else:
                return 1, "", "Contextual action requires target command info"
        
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
            
            result = subprocess.Popen(
                shell_cmd,
                shell=True,
                executable='/bin/zsh',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Add to history with PID
            self.history.add(command, args, result.pid)
            
            # Wait for completion
            try:
                stdout, stderr = result.communicate(timeout=30)
                return result.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                result.kill()
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
