#!/usr/bin/env python3
"""
Semantic Context Retrieval Client
Provides intelligent context retrieval for ISA AI commands using vector search.
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any, Optional

import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticContextRetriever:
    """Client for semantic context retrieval using vector database"""
    
    def __init__(self, vector_service_url: str = "http://192.168.1.161:8000"):
        self.service_url = vector_service_url
        
    def get_relevant_contexts(self, query: str, context_type: Optional[str] = None, 
                            n_results: int = 3, include_blended: bool = True) -> Dict[str, Any]:
        """Retrieve semantically relevant contexts for a query"""
        try:
            search_payload = {
                "query": query,
                "limit": n_results,
                "min_score": 0.1
            }
            
            if context_type:
                search_payload["context_type"] = context_type
            
            # Add blended context support
            if include_blended:
                search_payload["include_blended"] = True
                
            response = requests.post(
                f"{self.service_url}/search",
                json=search_payload,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve contexts: {e}")
            return {"results": [], "total_count": 0}
        except Exception as e:
            logger.error(f"Error in context retrieval: {e}")
            return {"results": [], "total_count": 0}
    
    def build_enhanced_prompt(self, user_query: str, context_type: str = "priorities",
                            max_context_length: int = 2000) -> str:
        """Build AI prompt with semantically relevant context"""
        try:
            # Get relevant contexts
            relevant_data = self.get_relevant_contexts(user_query, context_type)
            
            if not relevant_data.get("results"):
                logger.warning("No relevant contexts found, using basic prompt")
                return user_query
            
            # Build context text from results
            context_pieces = []
            total_length = 0
            
            for result in relevant_data["results"]:
                text = result.get("text", "")
                metadata = result.get("metadata", {})
                source = metadata.get("source", "unknown")
                section = metadata.get("section_title", metadata.get("section", ""))
                
                # Enhanced formatting for blended contexts
                source_info = self._format_source_info(metadata, source)
                if section and section != "header":
                    context_piece = f"From {source_info} ({section}):\n{text}\n"
                else:
                    context_piece = f"From {source_info}:\n{text}\n"
                
                # Check if adding this would exceed limit
                if total_length + len(context_piece) > max_context_length:
                    break
                    
                context_pieces.append(context_piece)
                total_length += len(context_piece)
            
            if not context_pieces:
                return user_query
            
            # Build enhanced prompt
            context_text = "\n".join(context_pieces)
            
            enhanced_prompt = f"""Based on the following relevant context information:

{context_text}

User Query: {user_query}

Please provide a helpful response that takes into account the context provided above. Focus on being specific and actionable based on the information given."""
            
            logger.info(f"Built enhanced prompt with {len(context_pieces)} context pieces ({total_length} chars)")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error building enhanced prompt: {e}")
            return user_query
    
    def search_contexts(self, query: str, context_type: Optional[str] = None,
                       n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for contexts and return formatted results"""
        try:
            results = self.get_relevant_contexts(query, context_type, n_results)
            
            formatted_results = []
            for result in results.get("results", []):
                metadata = result.get("metadata", {})
                source = metadata.get("source", "unknown")
                
                formatted_result = {
                    "text": result.get("text", ""),
                    "source": source,
                    "source_formatted": self._format_source_info(metadata, source),
                    "section": metadata.get("section_title", ""),
                    "context_type": metadata.get("context_type", "general"),
                    "relevance_score": result.get("score", 0.0),
                    "is_blended": metadata.get("is_sub_context", False),
                    "blended_from": metadata.get("blended_from", ""),
                    "sub_context_name": metadata.get("sub_context_name", "")
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching contexts: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test connection to vector service"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics from the vector service"""
        try:
            response = requests.get(f"{self.service_url}/stats", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {"error": str(e)}
    
    def _format_source_info(self, metadata: Dict[str, Any], source: str) -> str:
        """Format source information with blended context details"""
        if metadata.get('is_sub_context'):
            sub_context_name = metadata.get('sub_context_name', 'unknown')
            blended_from = metadata.get('blended_from', 'unknown')
            original_source = metadata.get('original_source', source)
            
            return f"🎨 {sub_context_name} (blended: {original_source} from {blended_from})"
        else:
            return source

def main():
    parser = argparse.ArgumentParser(description="Semantic context retrieval for ISA AI commands")
    parser.add_argument("query", help="Query to search for")
    parser.add_argument("--context-type", help="Filter by context type (person, project, priorities, etc.)")
    parser.add_argument("--service-url", default="http://192.168.1.161:8000", help="Vector service URL")
    parser.add_argument("--results", "-n", type=int, default=3, help="Number of results to return")
    parser.add_argument("--format", choices=["prompt", "json", "text"], default="prompt",
                       help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize retriever
    retriever = SemanticContextRetriever(vector_service_url=args.service_url)
    
    # Test connection first
    if not retriever.test_connection():
        print(f"❌ Cannot connect to vector service at {args.service_url}", file=sys.stderr)
        sys.exit(1)
    
    if args.format == "prompt":
        # Generate enhanced prompt
        enhanced_prompt = retriever.build_enhanced_prompt(
            user_query=args.query,
            context_type=args.context_type
        )
        print(enhanced_prompt)
        
    elif args.format == "json":
        # Return JSON results
        results = retriever.search_contexts(
            query=args.query,
            context_type=args.context_type,
            n_results=args.results
        )
        print(json.dumps(results, indent=2))
        
    elif args.format == "text":
        # Return formatted text results
        results = retriever.search_contexts(
            query=args.query,
            context_type=args.context_type,
            n_results=args.results
        )
        
        if not results:
            print("No relevant contexts found.")
        else:
            print(f"Found {len(results)} relevant contexts:")
            print("=" * 50)
            
            for i, result in enumerate(results, 1):
                relevance = result["relevance_score"]
                print(f"\n{i}. {result['source']} ({result['section']}) - Relevance: {relevance:.2f}")
                print("-" * 40)
                print(result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"])

if __name__ == "__main__":
    main()