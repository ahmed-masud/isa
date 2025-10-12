#!/usr/bin/env python3
"""
Example: How to integrate semantic context retrieval into ISA AI commands
"""

import sys
import os
sys.path.append('tools')

from tools.semantic_context import SemanticContextRetriever

def enhanced_ai_query(user_query: str, context_type: str = None) -> str:
    """
    Example function showing how to enhance AI queries with semantic context
    This is the pattern you'd use in your actual ISA AI command functions.
    """
    print(f"🤖 Processing AI query: '{user_query}'")
    
    # Initialize semantic retriever
    retriever = SemanticContextRetriever("http://192.168.1.161:8000")
    
    # Test connection
    if not retriever.test_connection():
        print("⚠️  Vector service unavailable, falling back to basic query")
        return user_query
    
    # Get enhanced prompt with semantic context
    enhanced_prompt = retriever.build_enhanced_prompt(
        user_query=user_query,
        context_type=context_type,
        max_context_length=2000
    )
    
    print("✅ Enhanced prompt with relevant context:")
    print("=" * 80)
    print(enhanced_prompt)
    print("=" * 80)
    
    # In a real implementation, you'd send this enhanced_prompt to your AI service
    # (Ollama, OpenAI, etc.) instead of the original user_query
    
    return enhanced_prompt

def demo_queries():
    """Demo various types of enhanced queries"""
    
    queries = [
        ("What should I work on next?", "priorities"),
        ("How do I set up Ollama?", "project"),
        ("What's my development workflow?", None),
        ("Show me my AI assistant projects", "project")
    ]
    
    for query, context_type in queries:
        print(f"\n{'='*60}")
        print(f"Demo Query: {query}")
        if context_type:
            print(f"Context Type: {context_type}")
        print("="*60)
        
        try:
            enhanced_ai_query(query, context_type)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("🎯 ISA AI Integration Demo")
    print("This shows how to integrate semantic context retrieval into AI commands.\n")
    
    demo_queries()
    
    print("💡 Integration Tips:")
    print("1. Call enhanced_ai_query() instead of sending raw queries to AI")
    print("2. Use context_type to filter relevant contexts")
    print("3. The enhanced prompt includes relevant context automatically")
    print("4. Fallback to basic query if vector service is unavailable")