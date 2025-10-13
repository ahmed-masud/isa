#!/usr/bin/env python3
"""
ISA Context Stack Manager
Implements push/pop context switching with persistent stack state
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import subprocess


class ContextStack:
    """Manages a stack of ISA contexts with push/pop operations"""
    
    def __init__(self, config_dir: str = None):
        """Initialize context stack manager"""
        self.config_dir = Path(config_dir or os.path.expanduser('~/.config/isa'))
        self.stack_file = self.config_dir / '.context_stack.json'
        self.current_context_file = self.config_dir / '.current_context'
        self.contexts_dir = self.config_dir / 'contexts'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize stack
        self.stack = self._load_stack()
        
        # Colors for output
        self.colors = {
            'red': '\033[0;31m',
            'green': '\033[0;32m',
            'yellow': '\033[1;33m',
            'blue': '\033[0;34m',
            'purple': '\033[0;35m',
            'cyan': '\033[0;36m',
            'white': '\033[1;37m',
            'nc': '\033[0m'  # No Color
        }
    
    def _load_stack(self) -> List[Dict]:
        """Load context stack from persistent storage"""
        if not self.stack_file.exists():
            return []
        
        try:
            with open(self.stack_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load context stack: {e}", file=sys.stderr)
            return []
    
    def _save_stack(self) -> bool:
        """Save context stack to persistent storage"""
        try:
            with open(self.stack_file, 'w') as f:
                json.dump(self.stack, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Could not save context stack: {e}", file=sys.stderr)
            return False
    
    def _get_current_context(self) -> Optional[str]:
        """Get the currently loaded context"""
        if self.current_context_file.exists():
            try:
                with open(self.current_context_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        return None
    
    def _set_current_context(self, context_name: str) -> bool:
        """Set the currently loaded context"""
        try:
            with open(self.current_context_file, 'w') as f:
                f.write(context_name)
            return True
        except Exception as e:
            print(f"Error: Could not save current context: {e}", file=sys.stderr)
            return False
    
    def _find_context_path(self, context_name: str) -> Optional[Tuple[str, str]]:
        """Find the path and type for a context"""
        for context_type in ['people', 'places', 'things']:
            context_path = self.contexts_dir / context_type / context_name
            if context_path.exists():
                return str(context_path), context_type
        return None
    
    def _load_context_with_script(self, context_name: str) -> bool:
        """Load context using the existing load-context.sh script"""
        try:
            isa_root = os.environ.get('ISA_ROOT', os.path.expanduser('~/projects/isa'))
            script_path = os.path.join(isa_root, 'load-context.sh')
            
            if not os.path.exists(script_path):
                print(f"Error: load-context.sh not found at {script_path}", file=sys.stderr)
                return False
            
            # Run the context loading script
            result = subprocess.run([script_path, context_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Update our current context tracking
                self._set_current_context(context_name)
                print(result.stdout)
                return True
            else:
                print(f"Error loading context: {result.stderr}", file=sys.stderr)
                return False
                
        except Exception as e:
            print(f"Error: Could not load context {context_name}: {e}", file=sys.stderr)
            return False
    
    def push(self, context_name: str) -> bool:
        """Push current context to stack and load new context"""
        current_context = self._get_current_context()
        
        if current_context:
            # Add current context to stack with timestamp
            stack_entry = {
                'context': current_context,
                'timestamp': datetime.now().isoformat(),
                'position': len(self.stack)
            }
            self.stack.append(stack_entry)
            
            print(f"{self.colors['yellow']}📚 Pushing context '{current_context}' to stack (position {len(self.stack) - 1}){self.colors['nc']}")
        
        # Load new context
        print(f"{self.colors['blue']}🔄 Loading new context: {context_name}{self.colors['nc']}")
        
        if self._load_context_with_script(context_name):
            self._save_stack()
            print(f"{self.colors['green']}✅ Context '{context_name}' loaded successfully{self.colors['nc']}")
            if current_context:
                print(f"{self.colors['cyan']}📋 Previous context '{current_context}' saved to stack{self.colors['nc']}")
            return True
        else:
            # Remove the entry we just added if loading failed
            if current_context and self.stack:
                self.stack.pop()
            return False
    
    def pop(self) -> bool:
        """Pop context from stack and load it"""
        if not self.stack:
            print(f"{self.colors['red']}❌ Context stack is empty - nothing to pop{self.colors['nc']}")
            return False
        
        # Get the most recent context from stack
        popped_entry = self.stack.pop()
        context_to_load = popped_entry['context']
        
        print(f"{self.colors['yellow']}📚 Popping context '{context_to_load}' from stack{self.colors['nc']}")
        
        # Load the popped context
        if self._load_context_with_script(context_to_load):
            self._save_stack()
            print(f"{self.colors['green']}✅ Restored to context: {context_to_load}{self.colors['nc']}")
            
            # Show remaining stack
            if self.stack:
                print(f"{self.colors['cyan']}📋 {len(self.stack)} context(s) remaining in stack{self.colors['nc']}")
            else:
                print(f"{self.colors['cyan']}📋 Stack is now empty{self.colors['nc']}")
            return True
        else:
            # Put the context back on the stack if loading failed
            self.stack.append(popped_entry)
            return False
    
    def peek(self) -> Optional[str]:
        """Peek at the top context in the stack without popping"""
        if not self.stack:
            return None
        return self.stack[-1]['context']
    
    def show_stack(self) -> None:
        """Display the current context stack"""
        current_context = self._get_current_context()
        
        print(f"{self.colors['white']}🏗️  ISA Context Stack{self.colors['nc']}")
        print("=" * 50)
        
        if current_context:
            print(f"{self.colors['green']}📍 Current: {current_context}{self.colors['nc']}")
        else:
            print(f"{self.colors['yellow']}📍 Current: (none loaded){self.colors['nc']}")
        
        print()
        
        if not self.stack:
            print(f"{self.colors['cyan']}📋 Stack: (empty){self.colors['nc']}")
            print("\n💡 Use 'isa push <context>' to start building a context stack")
        else:
            print(f"{self.colors['cyan']}📋 Stack ({len(self.stack)} contexts):{self.colors['nc']}")
            
            # Show stack from top to bottom (most recent first)
            for i, entry in enumerate(reversed(self.stack)):
                stack_pos = len(self.stack) - i - 1
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M:%S")
                marker = "→ " if i == 0 else "  "
                
                print(f"  {marker}[{stack_pos}] {entry['context']} {self.colors['blue']}(pushed at {timestamp}){self.colors['nc']}")
            
            print(f"\n💡 Use 'isa pop' to return to '{self.stack[-1]['context']}'")
    
    def clear_stack(self) -> bool:
        """Clear the entire context stack"""
        if not self.stack:
            print(f"{self.colors['yellow']}⚠️  Stack is already empty{self.colors['nc']}")
            return True
        
        stack_size = len(self.stack)
        self.stack.clear()
        
        if self._save_stack():
            print(f"{self.colors['green']}🗑️  Cleared {stack_size} context(s) from stack{self.colors['nc']}")
            return True
        else:
            return False
    
    def show_history(self, limit: int = 10) -> None:
        """Show recent context history"""
        print(f"{self.colors['white']}📜 Recent Context History{self.colors['nc']}")
        print("=" * 40)
        
        if not self.stack:
            print(f"{self.colors['cyan']}No context history yet{self.colors['nc']}")
            return
        
        # Show recent history (last N items)
        recent_stack = self.stack[-limit:] if len(self.stack) > limit else self.stack
        
        for i, entry in enumerate(reversed(recent_stack)):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {entry['context']} {self.colors['blue']}({timestamp}){self.colors['nc']}")
    
    def get_breadcrumbs(self) -> str:
        """Get a breadcrumb trail of contexts"""
        current_context = self._get_current_context()
        
        if not self.stack and not current_context:
            return "No contexts"
        
        breadcrumbs = []
        
        # Add stack contexts
        for entry in self.stack:
            breadcrumbs.append(entry['context'])
        
        # Add current context
        if current_context:
            breadcrumbs.append(f"*{current_context}*")
        
        return " → ".join(breadcrumbs)


def main():
    """Command-line interface for context stack operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ISA Context Stack Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push current context and load new one')
    push_parser.add_argument('context', help='Context name to load')
    
    # Pop command
    pop_parser = subparsers.add_parser('pop', help='Pop context from stack')
    
    # Show stack command
    stack_parser = subparsers.add_parser('stack', help='Show current context stack')
    
    # Peek command
    peek_parser = subparsers.add_parser('peek', help='Peek at top of stack without popping')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear entire context stack')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show context history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of recent contexts to show')
    
    # Breadcrumbs command
    breadcrumbs_parser = subparsers.add_parser('breadcrumbs', help='Show context breadcrumb trail')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize context stack manager
    stack_manager = ContextStack()
    
    try:
        if args.command == 'push':
            success = stack_manager.push(args.context)
            sys.exit(0 if success else 1)
        
        elif args.command == 'pop':
            success = stack_manager.pop()
            sys.exit(0 if success else 1)
        
        elif args.command == 'stack':
            stack_manager.show_stack()
        
        elif args.command == 'peek':
            top_context = stack_manager.peek()
            if top_context:
                print(f"Top of stack: {top_context}")
            else:
                print("Stack is empty")
        
        elif args.command == 'clear':
            success = stack_manager.clear_stack()
            sys.exit(0 if success else 1)
        
        elif args.command == 'history':
            stack_manager.show_history(args.limit)
        
        elif args.command == 'breadcrumbs':
            print(stack_manager.get_breadcrumbs())
    
    except KeyboardInterrupt:
        print("\nOperation cancelled", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()