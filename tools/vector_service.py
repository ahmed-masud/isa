#!/usr/bin/env python3
"""
ISA Vector Database Service
Provides semantic search and caching for ISA contexts using ChromaDB and sentence transformers.
"""

import os
import sys
import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextChunk(BaseModel):
    """Data model for a context chunk"""
    text: str
    source: str
    section: str
    chunk_id: str
    metadata: Dict[str, Any] = {}

class SearchQuery(BaseModel):
    """Data model for search queries"""
    query: str
    n_results: int = 5
    context_type: Optional[str] = None
    include_metadata: bool = True

class ISAVectorService:
    """Main vector database service for ISA contexts"""
    
    def __init__(self, persist_directory: str = "./chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        self.persist_directory = persist_directory
        self.model_name = model_name
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize or get collection
        try:
            self.collection = self.client.get_collection("isa_contexts")
            logger.info(f"Loaded existing collection with {self.collection.count()} embeddings")
        except Exception:
            self.collection = self.client.create_collection(
                name="isa_contexts",
                metadata={"description": "ISA context embeddings for semantic search"}
            )
            logger.info("Created new collection")
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Vector service initialized successfully")
    
    def add_contexts(self, chunks: List[ContextChunk]) -> Dict[str, Any]:
        """Add context chunks to the vector database"""
        try:
            texts = [chunk.text for chunk in chunks]
            metadatas = []
            ids = []
            
            # Prepare metadata and IDs
            for chunk in chunks:
                metadata = {
                    "source": chunk.source,
                    "section": chunk.section,
                    "chunk_id": chunk.chunk_id,
                    **chunk.metadata
                }
                metadatas.append(metadata)
                ids.append(f"{chunk.source}_{chunk.section}_{chunk.chunk_id}")
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector database")
            return {"status": "success", "chunks_added": len(chunks)}
            
        except Exception as e:
            logger.error(f"Error adding contexts: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to add contexts: {str(e)}")
    
    def search_contexts(self, query: str, n_results: int = 5, context_type: Optional[str] = None) -> Dict[str, Any]:
        """Search for semantically similar contexts"""
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query], convert_to_tensor=False)
            
            # Prepare search parameters
            search_kwargs = {
                "query_embeddings": query_embedding.tolist(),
                "n_results": min(n_results, 50)  # Cap at 50 results
            }
            
            # Add filter if context type specified
            if context_type:
                search_kwargs["where"] = {"context_type": context_type}
            
            # Perform search
            results = self.collection.query(**search_kwargs)
            
            # Format results
            formatted_results = {
                "query": query,
                "results": [],
                "total_found": len(results["documents"][0]) if results["documents"] else 0
            }
            
            if results["documents"]:
                for i in range(len(results["documents"][0])):
                    result = {
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0,
                        "id": results["ids"][0][i] if results["ids"] else ""
                    }
                    formatted_results["results"].append(result)
            
            logger.info(f"Search for '{query}' returned {formatted_results['total_found']} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching contexts: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    def delete_contexts(self, source: str) -> Dict[str, Any]:
        """Delete all contexts from a specific source"""
        try:
            # Find all IDs matching the source
            all_results = self.collection.get()
            matching_ids = [
                id_ for id_, metadata in zip(all_results["ids"], all_results["metadatas"])
                if metadata.get("source") == source
            ]
            
            if matching_ids:
                self.collection.delete(ids=matching_ids)
                logger.info(f"Deleted {len(matching_ids)} chunks from source: {source}")
            
            return {"status": "success", "deleted_count": len(matching_ids)}
            
        except Exception as e:
            logger.error(f"Error deleting contexts: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            count = self.collection.count()
            all_metadata = self.collection.get()["metadatas"]
            
            # Count by source
            source_counts = {}
            for metadata in all_metadata:
                source = metadata.get("source", "unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
            
            return {
                "total_chunks": count,
                "sources": source_counts,
                "model": self.model_name,
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}

# Initialize service
vector_service = ISAVectorService()

# Create FastAPI app
app = FastAPI(
    title="ISA Vector Database Service",
    description="Semantic search and caching for ISA contexts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ISA Vector Database"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    stats = vector_service.get_stats()
    return {"status": "healthy", "stats": stats}

@app.post("/embed")
async def embed_contexts(chunks: List[ContextChunk]):
    """Add context chunks to the vector database"""
    return vector_service.add_contexts(chunks)

@app.post("/search")
async def search_contexts(query: SearchQuery):
    """Search for semantically similar contexts"""
    return vector_service.search_contexts(
        query=query.query,
        n_results=query.n_results,
        context_type=query.context_type
    )

@app.delete("/contexts/{source}")
async def delete_contexts(source: str):
    """Delete all contexts from a specific source"""
    return vector_service.delete_contexts(source)

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    return vector_service.get_stats()

@app.post("/rebuild")
async def rebuild_index():
    """Rebuild the entire vector index"""
    # This would be implemented to re-process all ISA contexts
    return {"status": "not_implemented", "message": "Rebuild functionality coming soon"}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ISA Vector Database Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use")
    parser.add_argument("--persist", default="./chroma_db", help="Persistence directory")
    
    args = parser.parse_args()
    
    # Initialize service with custom parameters
    vector_service = ISAVectorService(
        persist_directory=args.persist,
        model_name=args.model
    )
    
    logger.info(f"Starting ISA Vector Database Service on {args.host}:{args.port}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )