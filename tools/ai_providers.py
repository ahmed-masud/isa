#!/usr/bin/env python3
"""
ISA Multi-Provider AI Client
Supports Ollama (local) and Models.dev (75+ cloud providers)
"""

import json
import sys
import requests
import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time

# Try to import semantic context retrieval
try:
    from semantic_context import SemanticContextRetriever
    SEMANTIC_CONTEXT_AVAILABLE = True
except ImportError:
    SEMANTIC_CONTEXT_AVAILABLE = False


@dataclass
class AIConfig:
    """Configuration for AI providers"""
    provider: str  # 'ollama' or 'models-dev'
    model: str
    host: str = None
    api_key: str = None
    timeout: int = 30
    max_tokens: int = 1000
    temperature: float = 0.7
    

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: AIConfig):
        self.config = config
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is accessible"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models"""
        pass
    
    @abstractmethod
    def query(self, prompt: str, **kwargs) -> Optional[str]:
        """Send a query to the provider"""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider"""
        pass


class OllamaProvider(AIProvider):
    """Ollama provider implementation"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        # Ensure host has proper format
        self.host = config.host or "http://192.168.1.161:11434"
        if not self.host.startswith('http'):
            self.host = f'http://{self.host}'
        if not self.host.endswith(':11434'):
            if ':' not in self.host.replace('http://', '').replace('https://', ''):
                self.host = f'{self.host}:11434'
    
    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException:
            return []
    
    def query(self, prompt: str, **kwargs) -> Optional[str]:
        if not prompt:
            raise ValueError("No prompt provided")
        
        if not self.health_check():
            raise ConnectionError(f"Cannot connect to Ollama at {self.host}")
        
        model = kwargs.get('model', self.config.model)
        stream = kwargs.get('stream', False)
        temperature = kwargs.get('temperature', self.config.temperature)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": kwargs.get('max_tokens', self.config.max_tokens)
            }
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', '')
            
        except requests.Timeout:
            raise TimeoutError(f"Request timed out after {self.config.timeout} seconds")
        except requests.RequestException as e:
            raise ConnectionError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "provider": "ollama",
            "type": "local",
            "host": self.host,
            "model": self.config.model,
            "available": self.health_check()
        }


class ModelsDevProvider(AIProvider):
    """Models.dev provider implementation"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.base_url = "https://api.models.dev/v1"
        self.api_key = config.api_key or os.environ.get('MODELS_DEV_API_KEY')
        
        if not self.api_key:
            raise ValueError("Models.dev API key required. Set MODELS_DEV_API_KEY environment variable.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/models", 
                                  headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/models", 
                                  headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            return []
        except requests.RequestException:
            return []
    
    def query(self, prompt: str, **kwargs) -> Optional[str]:
        if not prompt:
            raise ValueError("No prompt provided")
        
        if not self.health_check():
            raise ConnectionError("Cannot connect to Models.dev API")
        
        model = kwargs.get('model', self.config.model)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        temperature = kwargs.get('temperature', self.config.temperature)
        
        # Format message for chat completion format
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            return None
            
        except requests.Timeout:
            raise TimeoutError(f"Request timed out after {self.config.timeout} seconds")
        except requests.RequestException as e:
            raise ConnectionError(f"Models.dev API request failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "provider": "models-dev",
            "type": "cloud",
            "api_url": self.base_url,
            "model": self.config.model,
            "available": self.health_check(),
            "api_key_configured": bool(self.api_key)
        }


class MultiProviderAIClient:
    """Multi-provider AI client for ISA with semantic context integration"""
    
    def __init__(self, provider_configs: List[AIConfig] = None, 
                 vector_service_url: str = None, enable_semantic_context: bool = True):
        
        # Default configurations
        if provider_configs is None:
            provider_configs = self._load_default_configs()
        
        # Initialize providers
        self.providers = {}
        self.active_provider = None
        
        for config in provider_configs:
            try:
                if config.provider == 'ollama':
                    self.providers['ollama'] = OllamaProvider(config)
                elif config.provider == 'models-dev':
                    self.providers['models-dev'] = ModelsDevProvider(config)
                else:
                    print(f"Warning: Unknown provider {config.provider}", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Failed to initialize {config.provider}: {e}", file=sys.stderr)
        
        # Set default active provider (prefer Ollama if available, then models-dev)
        if 'ollama' in self.providers and self.providers['ollama'].health_check():
            self.active_provider = 'ollama'
        elif 'models-dev' in self.providers and self.providers['models-dev'].health_check():
            self.active_provider = 'models-dev'
        elif self.providers:
            self.active_provider = next(iter(self.providers.keys()))
        
        # Semantic context setup
        self.vector_service_url = vector_service_url or os.environ.get('VECTOR_SERVICE_URL', 'http://192.168.1.161:8000')
        self.enable_semantic_context = enable_semantic_context and SEMANTIC_CONTEXT_AVAILABLE
        self.semantic_retriever = None
        
        if self.enable_semantic_context:
            try:
                self.semantic_retriever = SemanticContextRetriever(self.vector_service_url)
                if not self.semantic_retriever.test_connection():
                    print(f"Warning: Cannot connect to vector service at {self.vector_service_url}", file=sys.stderr)
                    self.enable_semantic_context = False
            except Exception as e:
                print(f"Warning: Failed to initialize semantic context: {e}", file=sys.stderr)
                self.enable_semantic_context = False
    
    def _load_default_configs(self) -> List[AIConfig]:
        """Load default provider configurations from environment"""
        configs = []
        
        # Ollama config
        ollama_config = AIConfig(
            provider='ollama',
            model=os.environ.get('OLLAMA_MODEL', 'llama3'),
            host=os.environ.get('OLLAMA_HOST', 'http://192.168.1.161:11434'),
            timeout=int(os.environ.get('AI_TIMEOUT', 30))
        )
        configs.append(ollama_config)
        
        # Models.dev config (if API key is available)
        if os.environ.get('MODELS_DEV_API_KEY'):
            models_dev_config = AIConfig(
                provider='models-dev',
                model=os.environ.get('MODELS_DEV_MODEL', 'openai/gpt-4o-mini'),
                api_key=os.environ.get('MODELS_DEV_API_KEY'),
                timeout=int(os.environ.get('AI_TIMEOUT', 30))
            )
            configs.append(models_dev_config)
        
        return configs
    
    def set_active_provider(self, provider_name: str) -> bool:
        """Switch to a different provider"""
        if provider_name not in self.providers:
            print(f"Provider {provider_name} not available", file=sys.stderr)
            return False
        
        if not self.providers[provider_name].health_check():
            print(f"Provider {provider_name} is not healthy", file=sys.stderr)
            return False
        
        self.active_provider = provider_name
        return True
    
    def get_active_provider(self) -> Optional[AIProvider]:
        """Get the currently active provider"""
        if self.active_provider and self.active_provider in self.providers:
            return self.providers[self.active_provider]
        return None
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all configured providers and their status"""
        result = {}
        for name, provider in self.providers.items():
            result[name] = provider.get_provider_info()
            result[name]['active'] = (name == self.active_provider)
        return result
    
    def query(self, prompt: str, provider: str = None, **kwargs) -> Optional[str]:
        """Send a query using specified provider or active provider"""
        target_provider = provider or self.active_provider
        
        if not target_provider or target_provider not in self.providers:
            raise ValueError(f"Provider {target_provider} not available")
        
        return self.providers[target_provider].query(prompt, **kwargs)
    
    def semantic_query(self, query: str, context_type: str = None, provider: str = None,
                      max_context_length: int = 2000, **kwargs) -> Optional[str]:
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
                return self.query(enhanced_prompt, provider, **kwargs)
            except Exception as e:
                print(f"Warning: Semantic context retrieval failed: {e}", file=sys.stderr)
                # Fall back to basic query
                return self.query(query, provider, **kwargs)
        else:
            # Fall back to basic query if semantic context is not available
            return self.query(query, provider, **kwargs)
    
    def smart_query(self, query: str, provider: str = None, context_type: str = None,
                   prefer_semantic: bool = True, **kwargs) -> Optional[str]:
        """Intelligent query that uses semantic context when available"""
        if not query:
            raise ValueError("No query provided")
        
        # Try semantic context first if preferred and available
        if prefer_semantic and self.enable_semantic_context:
            return self.semantic_query(query, context_type, provider, **kwargs)
        else:
            return self.query(query, provider, **kwargs)
    
    def health_check(self, provider: str = None) -> Dict[str, bool]:
        """Check health of all providers or specific provider"""
        if provider:
            if provider in self.providers:
                return {provider: self.providers[provider].health_check()}
            else:
                return {provider: False}
        
        return {name: provider.health_check() for name, provider in self.providers.items()}
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        return {
            "providers": self.list_providers(),
            "active_provider": self.active_provider,
            "semantic_context": {
                "enabled": self.enable_semantic_context,
                "available": SEMANTIC_CONTEXT_AVAILABLE,
                "vector_service_url": self.vector_service_url
            }
        }


# Configuration helper functions
def load_config_from_file(config_path: str) -> List[AIConfig]:
    """Load provider configurations from JSON file"""
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        configs = []
        for provider_data in data.get('providers', []):
            config = AIConfig(**provider_data)
            configs.append(config)
        
        return configs
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}", file=sys.stderr)
        return []


def save_config_to_file(configs: List[AIConfig], config_path: str) -> bool:
    """Save provider configurations to JSON file"""
    try:
        data = {
            "providers": [
                {
                    "provider": config.provider,
                    "model": config.model,
                    "host": config.host,
                    "api_key": "***" if config.api_key else None,  # Don't save actual API keys
                    "timeout": config.timeout,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature
                }
                for config in configs
            ]
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Simple test
    client = MultiProviderAIClient()
    print("Available providers:")
    for name, info in client.list_providers().items():
        print(f"  {name}: {info}")
    
    print(f"\nActive provider: {client.active_provider}")
    
    if client.active_provider:
        try:
            response = client.query("Hello, how are you?")
            print(f"Test response: {response[:100]}..." if response else "No response")
        except Exception as e:
            print(f"Test query failed: {e}")