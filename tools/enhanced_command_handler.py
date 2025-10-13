#!/usr/bin/env python3
"""
Enhanced ISA Command Handler with Multi-Provider AI Support
Extends ISA's natural language command system with Models.dev integration
"""

import sys
import os
import subprocess
import json
from typing import Dict, Any, Optional, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_intent import CommandIntentMapper
from enhanced_ai_client import EnhancedISAClient


class EnhancedCommandHandler:
    """Enhanced command handler that integrates multi-provider AI with ISA's command system"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.intent_mapper = CommandIntentMapper(verbose=verbose)
        self.ai_client = EnhancedISAClient()
        
        # Extended command mappings for AI provider operations
        self.ai_command_mappings = {
            'ai-providers': self._handle_ai_providers,
            'ai-switch': self._handle_ai_switch,
            'ai-models': self._handle_ai_models,
            'ai-status': self._handle_ai_status,
        }
        
        # Extended command mappings for context stack operations
        self.context_command_mappings = {
            'context-push': self._handle_context_push,
            'context-pop': self._handle_context_pop,
            'context-stack': self._handle_context_stack,
            'context-breadcrumbs': self._handle_context_breadcrumbs,
        }
    
    def _handle_ai_providers(self, args: List[str]) -> str:
        """Handle AI providers listing command"""
        try:
            providers = self.ai_client.list_providers()
            
            output = "🤖 Available AI Providers:\n"
            output += "=" * 40 + "\n"
            
            for name, info in providers.items():
                if info.get('active'):
                    status = "✅ ACTIVE"
                elif info.get('available'):
                    status = "🟢 Available"
                else:
                    status = "❌ Unavailable"
                
                provider_type = info.get('type', 'unknown')
                model = info.get('model', 'N/A')
                
                output += f"  {name} ({provider_type}): {status}\n"
                output += f"    Model: {model}\n"
                
                if self.verbose:
                    for key, value in info.items():
                        if key not in ['active', 'available', 'type', 'model', 'provider']:
                            output += f"    {key}: {value}\n"
                output += "\n"
            
            return output.rstrip()
            
        except Exception as e:
            return f"❌ Error listing AI providers: {e}"
    
    def _handle_ai_switch(self, args: List[str]) -> str:
        """Handle AI provider switching command"""
        if not args:
            return "❌ Provider name required. Use: computer switch to [ollama|models-dev]"
        
        provider_name = args[0].lower()
        
        # Map common variations
        provider_mapping = {
            'ollama': 'ollama',
            'local': 'ollama',
            'models-dev': 'models-dev',
            'modelsdev': 'models-dev',
            'models.dev': 'models-dev',
            'cloud': 'models-dev',
            'gpt': 'models-dev',
            'openai': 'models-dev'
        }
        
        mapped_provider = provider_mapping.get(provider_name, provider_name)
        
        try:
            success = self.ai_client.switch_provider(mapped_provider)
            if success:
                return f"✅ Switched to AI provider: {mapped_provider}"
            else:
                available = list(self.ai_client.list_providers().keys())
                return f"❌ Could not switch to '{mapped_provider}'. Available providers: {', '.join(available)}"
        except Exception as e:
            return f"❌ Error switching AI provider: {e}"
    
    def _handle_ai_models(self, args: List[str]) -> str:
        """Handle AI models listing command"""
        try:
            status = self.ai_client.get_status()
            active_provider_name = status['active_provider']
            
            if not active_provider_name:
                return "❌ No active AI provider"
            
            active_provider = self.ai_client.client.get_active_provider()
            if not active_provider:
                return "❌ Could not get active provider details"
            
            models = active_provider.list_models()
            
            if not models:
                return f"No models available for {active_provider_name}"
            
            output = f"📚 Models available for {active_provider_name}:\n"
            for model in models:
                current_marker = " (current)" if model == active_provider.config.model else ""
                output += f"  {model}{current_marker}\n"
            
            return output.rstrip()
            
        except Exception as e:
            return f"❌ Error listing AI models: {e}"
    
    def _handle_ai_status(self, args: List[str]) -> str:
        """Handle AI status command"""
        try:
            status = self.ai_client.get_status()
            
            output = "🔍 ISA AI System Status:\n"
            output += "=" * 40 + "\n"
            
            output += f"Active Provider: {status['active_provider']}\n\n"
            
            output += "Providers:\n"
            for name, info in status['providers'].items():
                status_icon = "🟢" if info.get('available') else "❌"
                active_icon = " (ACTIVE)" if info.get('active') else ""
                model = info.get('model', 'N/A')
                output += f"  {status_icon} {name}{active_icon}: {model}\n"
            
            output += "\nSemantic Context:\n"
            sc = status['semantic_context']
            output += f"  Enabled: {'✅' if sc['enabled'] else '❌'}\n"
            output += f"  Available: {'✅' if sc['available'] else '❌'}\n"
            output += f"  Vector Service: {sc['vector_service_url']}\n"
            
            return output.rstrip()
            
        except Exception as e:
            return f"❌ Error getting AI status: {e}"
    
    def _handle_context_push(self, args: List[str]) -> str:
        """Handle context push command"""
        if not args:
            return "❌ Context name required. Use: computer push context <name>"
        
        context_name = args[0]
        
        try:
            # Import context stack manager
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from context_stack import ContextStack
            
            stack_manager = ContextStack()
            success = stack_manager.push(context_name)
            
            if success:
                return f"✅ Context '{context_name}' loaded, previous context saved to stack"
            else:
                return f"❌ Failed to push context '{context_name}'"
                
        except Exception as e:
            return f"❌ Error pushing context: {e}"
    
    def _handle_context_pop(self, args: List[str]) -> str:
        """Handle context pop command"""
        try:
            # Import context stack manager
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from context_stack import ContextStack
            
            stack_manager = ContextStack()
            success = stack_manager.pop()
            
            if success:
                return "✅ Returned to previous context"
            else:
                return "❌ No context to pop from stack"
                
        except Exception as e:
            return f"❌ Error popping context: {e}"
    
    def _handle_context_stack(self, args: List[str]) -> str:
        """Handle context stack display command"""
        try:
            # Import context stack manager
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from context_stack import ContextStack
            
            stack_manager = ContextStack()
            
            # Capture the output from show_stack
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                stack_manager.show_stack()
            
            return output_buffer.getvalue().strip()
                
        except Exception as e:
            return f"❌ Error showing context stack: {e}"
    
    def _handle_context_breadcrumbs(self, args: List[str]) -> str:
        """Handle context breadcrumbs command"""
        try:
            # Import context stack manager
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from context_stack import ContextStack
            
            stack_manager = ContextStack()
            breadcrumbs = stack_manager.get_breadcrumbs()
            
            return f"🗺️  Context Trail: {breadcrumbs}"
                
        except Exception as e:
            return f"❌ Error getting context breadcrumbs: {e}"
    
    def _execute_isa_command(self, command: str, args: List[str]) -> str:
        """Execute traditional ISA commands"""
        try:
            if command.startswith('isa '):
                cmd_parts = command.split()[1:]  # Remove 'isa' prefix
            else:
                cmd_parts = [command]
            
            cmd_parts.extend(args)
            
            # Special handling for context commands that need full python path
            if cmd_parts[0].startswith('ctx-'):
                # Use the enhanced AI client for context commands that might benefit from it
                if cmd_parts[0] == 'ctx-search' and args:
                    # Use semantic search through our enhanced client
                    search_query = ' '.join(args)
                    try:
                        response = self.ai_client.client.semantic_retriever.search_contexts(search_query)
                        if response:
                            return f"🔍 Semantic Search: {search_query}\n\n{response}"
                        else:
                            return f"No results found for: {search_query}"
                    except Exception as e:
                        return f"❌ Search failed: {e}"
                
                # Fall back to traditional ISA commands
                full_cmd = ['isa'] + cmd_parts
            else:
                full_cmd = ['isa'] + cmd_parts
            
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip() if result.stderr else "Command failed"
                return f"❌ {error_msg}"
                
        except subprocess.TimeoutExpired:
            return "❌ Command timed out"
        except Exception as e:
            return f"❌ Error executing command: {e}"
    
    def handle_natural_language(self, user_input: str) -> Dict[str, Any]:
        """Handle natural language input with enhanced AI provider support"""
        try:
            # First, try to parse with the intent mapper
            parsed = self.intent_mapper.interpret_command(user_input)
            
            if not parsed:
                return {
                    'success': False,
                    'error': 'Could not understand command',
                    'suggestion': 'Try: computer show stats, computer check health, computer list providers'
                }
            
            command = parsed['command']
            args = parsed.get('args', [])
            
            # Check if it's one of our new AI provider or context stack commands
            if command.startswith('isa '):
                isa_command = command.split()[1]  # Get the part after 'isa '
                
                if isa_command in self.ai_command_mappings:
                    # Handle AI provider commands directly
                    output = self.ai_command_mappings[isa_command](args)
                    return {
                        'success': True,
                        'output': output,
                        'command': command,
                        'confidence': parsed.get('confidence', 0.8)
                    }
                elif isa_command in self.context_command_mappings:
                    # Handle context stack commands directly
                    output = self.context_command_mappings[isa_command](args)
                    return {
                        'success': True,
                        'output': output,
                        'command': command,
                        'confidence': parsed.get('confidence', 0.8)
                    }
            
            # Execute traditional ISA command
            output = self._execute_isa_command(command, args)
            
            return {
                'success': True,
                'output': output,
                'command': command,
                'args': args,
                'confidence': parsed.get('confidence', 0.8),
                'reasoning': parsed.get('reasoning', '')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing command: {e}",
                'command': user_input
            }
    
    def execute_ai_query(self, query: str, provider: str = None, **kwargs) -> str:
        """Execute an AI query with provider selection"""
        try:
            response = self.ai_client.enhanced_query(
                query=query,
                provider=provider,
                force_provider=bool(provider),
                **kwargs
            )
            return response or "No response received"
        except Exception as e:
            return f"❌ AI query failed: {e}"


def main():
    """Command-line interface for the enhanced command handler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced ISA Command Handler')
    parser.add_argument('command', nargs='*', help='Natural language command')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--provider', help='Force specific AI provider')
    parser.add_argument('--ai-query', help='Direct AI query (bypasses command parsing)')
    
    args = parser.parse_args()
    
    if not args.command and not args.ai_query:
        parser.error("Either command or --ai-query is required")
    
    handler = EnhancedCommandHandler(verbose=args.verbose)
    
    try:
        if args.ai_query:
            # Direct AI query
            response = handler.execute_ai_query(args.ai_query, provider=args.provider)
            if args.json:
                print(json.dumps({'response': response}))
            else:
                print(response)
        else:
            # Natural language command
            user_input = ' '.join(args.command)
            result = handler.handle_natural_language(user_input)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result['success']:
                    print(result['output'])
                    if args.verbose and 'reasoning' in result:
                        print(f"\n[Reasoning: {result['reasoning']}]", file=sys.stderr)
                else:
                    print(f"Error: {result['error']}", file=sys.stderr)
                    if 'suggestion' in result:
                        print(f"Suggestion: {result['suggestion']}", file=sys.stderr)
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled", file=sys.stderr)
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