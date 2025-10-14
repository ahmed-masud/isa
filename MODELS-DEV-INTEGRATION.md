# ISA Models.dev Integration Guide

## 🎉 Overview

ISA now supports **Models.dev integration**, giving you access to **75+ LLM providers** including OpenAI GPT-4, Claude, Gemini, and many others, while maintaining full compatibility with your existing Ollama setup.

This integration extends ISA's AI capabilities beyond local Ollama models to include cloud-based models from major providers, all through a unified interface that preserves ISA's natural language command system and semantic context features.

---

## ✨ What You Get

### 🤖 **Multi-Provider AI Support**
- **Ollama (Local)**: Your existing local LLM setup
- **Models.dev (Cloud)**: 75+ cloud providers including:
  - OpenAI (GPT-4, GPT-3.5, etc.)
  - Anthropic (Claude models)
  - Google (Gemini, PaLM)
  - Amazon Bedrock models
  - And many more!

### 🔄 **Seamless Provider Switching**
```bash
# Switch between providers with natural language
computer switch to ollama          # Use local models
computer switch to models-dev      # Use cloud models
computer switch to gpt             # Smart mapping to models-dev
```

### 🧠 **Enhanced Natural Language Commands**
All existing ISA commands work with both providers:
```bash
computer ask "What should I work on?" --provider models-dev
computer show providers             # List all available providers
computer list models               # Show models for active provider
```

### 📊 **Unified Status and Health Monitoring**
```bash
computer show ai status            # Complete AI system overview
computer check health              # Health check all providers
computer list providers            # Detailed provider information
```

---

## 🚀 Quick Setup

### 1. **Get Models.dev API Key**

1. Visit [models.dev](https://models.dev) and create an account
2. Generate an API key from your dashboard
3. Set the environment variable:

```bash
# Add to your ~/.zshrc or ~/.bashrc
export MODELS_DEV_API_KEY="your-api-key-here"

# Reload your shell
source ~/.zshrc
```

### 2. **Choose Your Default Model**

```bash
# Optional: Set your preferred Models.dev model
export MODELS_DEV_MODEL="openai/gpt-4o-mini"  # Default: cost-effective
# or
export MODELS_DEV_MODEL="anthropic/claude-3-5-haiku-20241022"  # Claude
# or  
export MODELS_DEV_MODEL="openai/gpt-4o"  # Most powerful OpenAI
```

### 3. **Test the Integration**

```bash
# Check if everything is working
computer show ai status

# Test both providers
computer ask "Hello, test message" --provider ollama
computer ask "Hello, test message" --provider models-dev
```

---

## 🎯 Usage Guide

### **Basic AI Queries**

```bash
# Use active provider (auto-selected)
computer ask "What should I work on next?"

# Force specific provider
computer ask "Explain quantum computing" --provider models-dev
computer ask "What's my local system info?" --provider ollama

# With context type filtering
computer ask "What are my urgent AI projects?" --context-type priorities
```

### **Provider Management**

```bash
# List all available providers
computer show providers
computer list providers

# Switch active provider
computer switch to models-dev
computer switch to ollama  
computer switch to cloud      # Maps to models-dev
computer switch to local      # Maps to ollama

# Check provider health
computer check health

# Show AI system status
computer show ai status
```

### **Model Management**

```bash
# List models for active provider
computer list models
computer show models

# Use specific model (provider-specific syntax)
computer ask "Hello" --model "openai/gpt-4o" --provider models-dev
computer ask "Hello" --model "llama3.2:latest" --provider ollama
```

### **Semantic Context Integration**

The Models.dev integration fully supports ISA's semantic context system:

```bash
# Semantic search works with both providers
computer search for "deployment procedures"

# AI queries automatically use semantic context
computer ask "Based on my deployment docs, how should I deploy ISA?"

# Context-aware queries with provider selection
computer ask "What AI projects need attention?" --provider models-dev
```

---

## ⚙️ Configuration

### **Environment Variables**

```bash
# Models.dev Configuration
export MODELS_DEV_API_KEY="your-api-key"           # Required
export MODELS_DEV_MODEL="openai/gpt-4o-mini"       # Optional (default)

# Ollama Configuration (existing)
export OLLAMA_HOST="http://192.168.1.161:11434"    # Optional
export OLLAMA_MODEL="llama3"                       # Optional

# Global AI Settings
export AI_TIMEOUT="60"                              # Timeout in seconds
```

### **Configuration File** (Advanced)

You can create a JSON configuration file at `~/.config/isa/ai_config.json`:

```json
{
  "providers": [
    {
      "provider": "ollama",
      "model": "llama3.2:latest",
      "host": "http://192.168.1.161:11434",
      "timeout": 30,
      "temperature": 0.7
    },
    {
      "provider": "models-dev",
      "model": "openai/gpt-4o",
      "api_key": "your-api-key-here",
      "timeout": 60,
      "temperature": 0.8,
      "max_tokens": 2000
    }
  ]
}
```

---

## 📋 Command Reference

### **Natural Language Commands**

| What You Want | Natural Command | Traditional Alternative |
|---------------|-----------------|------------------------|
| **Provider Management** |
| List providers | `computer show providers` | `python3 tools/enhanced_ai_client.py --list-providers` |
| Switch provider | `computer switch to models-dev` | `python3 tools/enhanced_ai_client.py --switch-provider models-dev` |
| Show AI status | `computer show ai status` | `python3 tools/enhanced_ai_client.py --status` |
| Check health | `computer check health` | `python3 tools/enhanced_ai_client.py --health-check` |
| List models | `computer list models` | `python3 tools/enhanced_ai_client.py --list-models` |
| **AI Queries** |
| Basic query | `computer ask "question"` | `python3 tools/enhanced_ai_client.py "question"` |
| Provider-specific | `computer ask "question" with models-dev` | `python3 tools/enhanced_ai_client.py "question" --provider models-dev` |
| With context | `computer ask "question" about priorities` | `python3 tools/enhanced_ai_client.py "question" --context-type priorities` |

### **Direct CLI Usage**

```bash
# Enhanced AI client (recommended)
python3 tools/enhanced_ai_client.py --help
python3 tools/enhanced_ai_client.py "What should I work on?" --provider models-dev
python3 tools/enhanced_ai_client.py --list-providers --verbose
python3 tools/enhanced_ai_client.py --status

# Multi-provider client (advanced)
python3 tools/ai_providers.py  # Basic test

# Enhanced command handler (for integration)
python3 tools/enhanced_command_handler.py show ai status
python3 tools/enhanced_command_handler.py list providers
```

---

## 🎨 Model Selection Guide

### **Cost-Effective Options**

```bash
# Best value for money
export MODELS_DEV_MODEL="openai/gpt-4o-mini"       # $0.15/$0.60 per 1M tokens
export MODELS_DEV_MODEL="anthropic/claude-3-5-haiku-20241022"  # $0.80/$4.00 per 1M tokens

# Free tier (if available)
export MODELS_DEV_MODEL="alibaba/qwen3-coder-plus" # $1.00/$5.00 per 1M tokens
```

### **High Performance Options**

```bash
# Most capable models
export MODELS_DEV_MODEL="openai/gpt-4o"           # Latest OpenAI flagship
export MODELS_DEV_MODEL="anthropic/claude-3-5-sonnet-20241022"  # Claude's most capable
export MODELS_DEV_MODEL="google/gemini-pro"       # Google's flagship
```

### **Specialized Models**

```bash
# Coding focused
export MODELS_DEV_MODEL="alibaba/qwen3-coder-plus"

# Long context
export MODELS_DEV_MODEL="anthropic/claude-3-5-haiku-20241022"  # 200K context
```

---

## 🔧 Troubleshooting

### **Common Issues**

1. **"Models.dev API key required" Error**
   ```bash
   # Check if environment variable is set
   echo $MODELS_DEV_API_KEY
   
   # Set it if missing
   export MODELS_DEV_API_KEY="your-api-key"
   ```

2. **"Cannot connect to Models.dev API" Error**
   ```bash
   # Test API connectivity
   curl -H "Authorization: Bearer $MODELS_DEV_API_KEY" https://api.models.dev/v1/models
   
   # Check provider health
   computer check health
   ```

3. **Provider Not Available**
   ```bash
   # List what's actually available
   computer show providers --verbose
   
   # Reset to working provider
   computer switch to ollama  # Fall back to local
   ```

4. **Semantic Context Not Working**
   ```bash
   # Check semantic context status
   computer show ai status
   
   # Test vector database
   isa ctx-health
   ```

### **Performance Tips**

1. **Use Appropriate Models for Tasks**
   - Simple queries: `gpt-4o-mini` or local `llama3`
   - Complex analysis: `gpt-4o` or `claude-3-5-sonnet`
   - Coding: `qwen3-coder-plus` or local `codellama`

2. **Optimize Costs**
   - Set reasonable `max_tokens` limits
   - Use local models for system queries
   - Use cloud models for complex reasoning

3. **Reduce Latency**
   - Prefer local models for quick queries
   - Cache frequently used responses
   - Use shorter context when possible

---

## 🧪 Testing Your Setup

### **Basic Functionality Test**

```bash
# 1. Check system status
computer show ai status

# 2. Test both providers
computer ask "Hello, this is a test" --provider ollama
computer ask "Hello, this is a test" --provider models-dev

# 3. Test provider switching
computer switch to models-dev
computer ask "What's 2+2?"
computer switch to ollama  
computer ask "What's 2+2?"

# 4. Test natural language commands
computer list providers
computer show models
computer check health
```

### **Advanced Feature Test**

```bash
# Test semantic context integration
computer ask "What should I work on based on my priorities?"

# Test context-specific queries
computer ask "What AI projects do I have?" --context-type project

# Test model selection
computer ask "Explain machine learning" --model "openai/gpt-4o" --provider models-dev
```

---

## 📈 Performance Comparison

| Provider | Latency | Cost | Context | Best For |
|----------|---------|------|---------|----------|
| **Ollama (Local)** | ~1-5s | Free | Limited | System queries, privacy, offline |
| **Models.dev GPT-4o-mini** | ~2-10s | Low | High | General tasks, cost-effective |
| **Models.dev GPT-4o** | ~5-15s | High | Very High | Complex reasoning, analysis |
| **Models.dev Claude** | ~3-12s | Medium | Very High | Long documents, nuanced tasks |

---

## 🎯 Integration with Existing ISA Workflows

The Models.dev integration seamlessly works with all existing ISA features:

### **Morning Routine**
```bash
# Check system status (uses active provider)
computer show ai status

# Get AI-powered morning brief (uses semantic context + cloud AI)
computer ask "What should I prioritize today?" --provider models-dev

# Check urgent items (local, fast)
computer urgent
```

### **Project Work**
```bash
# AI analysis with full context (cloud for complex reasoning)
computer ask "Based on my ISA project, what should I work on next?" --provider models-dev

# Quick status checks (local, fast)
computer show stats
computer check health

# Semantic search (local vector DB, but can use cloud AI for query)
computer search for "deployment procedures"
```

### **Context Management**
```bash
# All context commands work as before
computer sync
computer show stats

# But now AI queries can use cloud models for better analysis
computer ask "Analyze my context data and suggest improvements" --provider models-dev
```

---

## 🚀 Advanced Usage

### **Custom Scripts**

You can use the multi-provider system in your own scripts:

```python
#!/usr/bin/env python3
from tools.ai_providers import MultiProviderAIClient, AIConfig

# Initialize client with custom config
client = MultiProviderAIClient()

# Use different providers for different tasks
local_response = client.query("Quick system check", provider="ollama")
cloud_response = client.query("Complex analysis task", provider="models-dev")

# Smart query with automatic provider selection and semantic context
response = client.smart_query("What should I work on next?")
```

### **Configuration Management**

```bash
# Save current configuration
python3 -c "
from tools.ai_providers import save_config_to_file, AIConfig
configs = [
    AIConfig(provider='ollama', model='llama3', host='http://192.168.1.161:11434'),
    AIConfig(provider='models-dev', model='openai/gpt-4o-mini', api_key='$MODELS_DEV_API_KEY')
]
save_config_to_file(configs, '~/.config/isa/ai_config.json')
"
```

---

## 🔒 Security and Privacy

### **Data Handling**
- **Local (Ollama)**: All data stays on your network
- **Cloud (Models.dev)**: Data sent to chosen provider according to their privacy policy
- **Semantic Context**: Vector database remains local regardless of AI provider

### **API Key Security**
- API keys are read from environment variables only
- Never logged or saved in plain text
- Use dedicated API keys with appropriate permissions

### **Best Practices**
```bash
# Use local models for sensitive data
computer ask "Analyze my personal priorities" --provider ollama

# Use cloud models for general knowledge
computer ask "Explain quantum computing" --provider models-dev

# Check what data is being sent
python3 tools/enhanced_ai_client.py --verbose "test query"
```

---

## 🎉 Next Steps

1. **Set up your Models.dev API key** and test the integration
2. **Try different models** to see which work best for your use cases
3. **Experiment with provider switching** in your daily ISA workflows
4. **Share your feedback** to help improve the integration

The Models.dev integration makes ISA even more powerful while maintaining its simplicity and natural language interface. You now have the best of both worlds: local privacy and control with Ollama, plus access to state-of-the-art cloud models when you need them.

---

## 📞 Support and Feedback

If you encounter issues or have suggestions for improvement:

1. Check the troubleshooting section above
2. Use `--verbose` flags for detailed error information
3. Test with both providers to isolate issues
4. Check your API key and network connectivity

**Happy AI-assisted productivity!** 🚀

---

**Last Updated**: 2025-10-13  
**ISA Version**: 1.0+ with Models.dev Integration  
**Compatibility**: macOS, Linux, zsh/bash