#!/usr/bin/env python3
"""
Enhanced ISA AI Client with Multi-Provider Support
Extends the existing ollama_client.py with Models.dev integration
"""

import json
import sys
import argparse
import os
from typing import Optional, Dict, Any, List

# Import our new multi-provider system
from ai_providers import MultiProviderAIClient, AIConfig, load_config_from_file


class EnhancedISAClient:
    """Enhanced ISA client with multi-provider support"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.expanduser('~/.config/isa/ai_config.json')
        
        # Load configurations
        if os.path.exists(self.config_file):
            provider_configs = load_config_from_file(self.config_file)
        else:
            provider_configs = None  # Use defaults
        
        # Initialize multi-provider client
        self.client = MultiProviderAIClient(provider_configs)
    
    def _detect_system_query(self, query: str) -> Optional[str]:
        """Detect system queries that don't need semantic context (same as original)"""
        import subprocess
        query_lower = query.lower().strip()
        
        def run_command(cmd, description=""):
            """Helper to run system commands safely"""
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return f"{description}Command failed: {result.stderr.strip()}"
            except Exception as e:
                return f"{description}Error: {str(e)}"
        
        # Time/date queries
        time_patterns = [
            'what time is it', 'current time', 'what is the time', 'time now',
            'what is the current time', 'what is the current system time',
            'system time', 'current system time', 'time', 'date'
        ]
        
        for pattern in time_patterns:
            if pattern in query_lower:
                result = run_command("date '+%A, %B %d, %Y at %I:%M:%S %p %Z'", "")
                return f"Current system time: {result}"
        
        # Other system queries (abbreviated for brevity)
        if any(phrase in query_lower for phrase in ['where am i', 'current directory', 'pwd']):
            result = run_command("pwd", "")
            return f"Current directory: {result}"
        
        return None
    
    def enhanced_query(self, query: str, provider: str = None, context_type: str = None,
                      force_provider: bool = False, **kwargs) -> Optional[str]:
        """Enhanced query with provider selection and system query detection"""
        if not query:
            raise ValueError("No query provided")
        
        # Check for simple system queries first
        system_response = self._detect_system_query(query)
        if system_response:
            return system_response
        
        # Use smart query with optional provider override
        return self.client.smart_query(
            query=query,
            provider=provider if force_provider else None,
            context_type=context_type,
            **kwargs
        )
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers"""
        return self.client.list_providers()
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different provider"""
        return self.client.set_active_provider(provider_name)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return self.client.get_status()
    
    def health_check(self, provider: str = None) -> Dict[str, bool]:
        """Check provider health"""
        return self.client.health_check(provider)


def main():
    parser = argparse.ArgumentParser(description='Enhanced ISA AI Client with Multi-Provider Support')
    parser.add_argument('prompt', nargs='?', help='The prompt to send to AI')
    
    # Provider selection
    parser.add_argument('--provider', choices=['ollama', 'models-dev'], 
                      help='Force specific provider (default: auto-select best available)')
    parser.add_argument('--model', help='Model to use (provider-specific)')
    parser.add_argument('--list-providers', action='store_true', help='List all available providers')
    parser.add_argument('--switch-provider', help='Switch active provider')
    parser.add_argument('--status', action='store_true', help='Show system status')
    
    # Context options
    parser.add_argument('--context-type', help='Semantic context type filter')
    parser.add_argument('--disable-semantic', action='store_true', help='Disable semantic context')
    
    # Configuration
    parser.add_argument('--config', help='Configuration file path')
    
    # Health checks
    parser.add_argument('--health-check', action='store_true', help='Check all providers health')
    parser.add_argument('--test-semantic', action='store_true', help='Test semantic context')
    
    # API compatibility with existing ollama_client.py
    parser.add_argument('--host', help='Ollama host URL (for ollama provider)')
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
    parser.add_argument('--context-file', help='File context (legacy)')
    parser.add_argument('--semantic-only', action='store_true', help='Use only semantic context')
    parser.add_argument('--list-models', action='store_true', help='List models for active provider')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        # Initialize enhanced client
        client = EnhancedISAClient(args.config)
        
        # Handle various commands
        if args.list_providers:
            providers = client.list_providers()
            print("🤖 Available AI Providers:")
            print("=" * 40)
            for name, info in providers.items():
                status = "✅ Active" if info.get('active') else ("🟢 Available" if info.get('available') else "❌ Unavailable")
                provider_type = info.get('type', 'unknown')
                model = info.get('model', 'N/A')
                print(f"  {name} ({provider_type}): {status}")
                print(f"    Model: {model}")
                if args.verbose:
                    for key, value in info.items():
                        if key not in ['active', 'available', 'type', 'model', 'provider']:
                            print(f"    {key}: {value}")
                print()
            return
        
        if args.switch_provider:
            success = client.switch_provider(args.switch_provider)
            if success:
                print(f"✅ Switched to provider: {args.switch_provider}")
            else:
                print(f"❌ Failed to switch to provider: {args.switch_provider}")
                sys.exit(1)
            return
        
        if args.status:
            status = client.get_status()
            print("🔍 ISA AI System Status:")
            print("=" * 40)
            
            print(f"Active Provider: {status['active_provider']}")
            print("\nProviders:")
            for name, info in status['providers'].items():
                status_icon = "🟢" if info.get('available') else "❌"
                active_icon = " (ACTIVE)" if info.get('active') else ""
                print(f"  {status_icon} {name}{active_icon}: {info.get('model', 'N/A')}")
            
            print(f"\nSemantic Context:")
            sc = status['semantic_context']
            print(f"  Enabled: {'✅' if sc['enabled'] else '❌'}")
            print(f"  Available: {'✅' if sc['available'] else '❌'}")
            print(f"  Vector Service: {sc['vector_service_url']}")
            return
        
        if args.health_check:
            health = client.health_check()
            print("🏥 Provider Health Check:")
            print("=" * 30)
            for provider, is_healthy in health.items():
                status = "✅ Healthy" if is_healthy else "❌ Unavailable"
                print(f"  {provider}: {status}")
            return
        
        if args.test_semantic:
            status = client.get_status()
            sc = status['semantic_context']
            if sc['enabled'] and sc['available']:
                print("✅ Semantic context is available and enabled")
                # Test with the client's semantic retriever if available
                if hasattr(client.client, 'semantic_retriever') and client.client.semantic_retriever:
                    try:
                        stats = client.client.semantic_retriever.get_service_stats()
                        print(f"📊 Vector database stats: {stats}")
                    except Exception as e:
                        print(f"⚠️ Could not retrieve stats: {e}")
            else:
                print("❌ Semantic context is not available")
            return
        
        if args.list_models:
            active_provider = client.client.get_active_provider()
            if active_provider:
                models = active_provider.list_models()
                if models:
                    print(f"📚 Models available for {client.client.active_provider}:")
                    for model in models:
                        print(f"  {model}")
                else:
                    print("No models available")
            else:
                print("No active provider")
            return
        
        # Main query processing
        if not args.prompt:
            parser.error('Prompt is required for query operations')
        
        # Prepare query options
        query_kwargs = {}
        if args.model:
            query_kwargs['model'] = args.model
        if args.timeout:
            query_kwargs['timeout'] = args.timeout
        
        # Execute query with enhanced client
        response = client.enhanced_query(
            query=args.prompt,
            provider=args.provider,
            context_type=args.context_type,
            force_provider=bool(args.provider),
            **query_kwargs
        )
        
        if response:
            print(response)
        else:
            print("Empty response received", file=sys.stderr)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
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