#!/usr/bin/env python3
"""
Simplified Vector Database Service for ISA Contexts
Purpose: Provides REST API for semantic embedding and search of context chunks
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response Models
class ContextChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    min_score: float = 0.1

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int

class DeleteRequest(BaseModel):
    chunk_ids: List[str]

# Simple Vector Database using TF-IDF and sklearn
class SimpleVectorDB:
    def __init__(self, storage_dir: str = "./simple_vector_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.chunks = {}  # chunk_id -> {text, metadata}
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.vectors = None
        self.is_trained = False
        
        # Load existing data if available
        self._load_from_disk()
    
    def _generate_chunk_id(self, text: str, metadata: Dict[str, Any]) -> str:
        content = f"{text}:{json.dumps(metadata, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _save_to_disk(self):
        """Save chunks and vectorizer to disk"""
        try:
            # Save chunks
            chunks_file = self.storage_dir / "chunks.json"
            with open(chunks_file, 'w') as f:
                json.dump(self.chunks, f, indent=2)
            
            # Save vectorizer if trained
            if self.is_trained:
                vectorizer_file = self.storage_dir / "vectorizer.pkl"
                with open(vectorizer_file, 'wb') as f:
                    pickle.dump(self.vectorizer, f)
                
                # Save vectors
                vectors_file = self.storage_dir / "vectors.npy"
                np.save(vectors_file, self.vectors.toarray())
                
            logger.info(f"Saved {len(self.chunks)} chunks to disk")
        except Exception as e:
            logger.error(f"Error saving to disk: {e}")
    
    def _load_from_disk(self):
        """Load chunks and vectorizer from disk"""
        try:
            chunks_file = self.storage_dir / "chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r') as f:
                    self.chunks = json.load(f)
                logger.info(f"Loaded {len(self.chunks)} chunks from disk")
            
            vectorizer_file = self.storage_dir / "vectorizer.pkl"
            vectors_file = self.storage_dir / "vectors.npy"
            
            if vectorizer_file.exists() and vectors_file.exists():
                with open(vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                vectors_array = np.load(vectors_file)
                self.vectors = vectors_array
                self.is_trained = True
                logger.info("Loaded trained vectorizer and vectors from disk")
        except Exception as e:
            logger.error(f"Error loading from disk: {e}")
    
    def _retrain_vectorizer(self):
        """Retrain vectorizer with all current chunks"""
        if not self.chunks:
            logger.warning("No chunks available for training")
            return
        
        try:
            texts = [chunk['text'] for chunk in self.chunks.values()]
            self.vectors = self.vectorizer.fit_transform(texts)
            self.is_trained = True
            logger.info(f"Retrained vectorizer with {len(texts)} texts")
        except Exception as e:
            logger.error(f"Error retraining vectorizer: {e}")
            raise
    
    def add_chunks(self, chunks: List[ContextChunk]) -> Dict[str, Any]:
        """Add chunks to the database"""
        added_count = 0
        updated_count = 0
        
        for chunk in chunks:
            chunk_id = chunk.chunk_id or self._generate_chunk_id(chunk.text, chunk.metadata)
            
            if chunk_id in self.chunks:
                updated_count += 1
            else:
                added_count += 1
            
            self.chunks[chunk_id] = {
                'text': chunk.text,
                'metadata': chunk.metadata
            }
        
        # Retrain vectorizer
        self._retrain_vectorizer()
        
        # Save to disk
        self._save_to_disk()
        
        return {
            'added': added_count,
            'updated': updated_count,
            'total': len(self.chunks)
        }
    
    def search(self, query: str, limit: int = 10, min_score: float = 0.1) -> List[SearchResult]:
        """Search for similar chunks"""
        if not self.is_trained or not self.chunks:
            return []
        
        try:
            # Transform query using trained vectorizer
            query_vector = self.vectorizer.transform([query])
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_vector, self.vectors).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:limit]
            
            results = []
            chunk_ids = list(self.chunks.keys())
            
            for idx in top_indices:
                score = float(similarities[idx])
                if score < min_score:
                    break
                
                chunk_id = chunk_ids[idx]
                chunk_data = self.chunks[chunk_id]
                
                results.append(SearchResult(
                    chunk_id=chunk_id,
                    text=chunk_data['text'],
                    metadata=chunk_data['metadata'],
                    score=score
                ))
            
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    def delete_chunks(self, chunk_ids: List[str]) -> Dict[str, Any]:
        """Delete chunks by IDs"""
        deleted_count = 0
        not_found = []
        
        for chunk_id in chunk_ids:
            if chunk_id in self.chunks:
                del self.chunks[chunk_id]
                deleted_count += 1
            else:
                not_found.append(chunk_id)
        
        if deleted_count > 0:
            # Retrain vectorizer
            self._retrain_vectorizer()
            
            # Save to disk
            self._save_to_disk()
        
        return {
            'deleted': deleted_count,
            'not_found': not_found,
            'total_remaining': len(self.chunks)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_chunks': len(self.chunks),
            'is_trained': self.is_trained,
            'storage_dir': str(self.storage_dir)
        }
    
    def rebuild_index(self) -> Dict[str, Any]:
        """Rebuild the entire index"""
        if self.chunks:
            self._retrain_vectorizer()
            self._save_to_disk()
            return {'rebuilt': True, 'total_chunks': len(self.chunks)}
        else:
            return {'rebuilt': False, 'reason': 'No chunks to rebuild'}

# Initialize FastAPI app and database
app = FastAPI(
    title="Simple Vector Database Service",
    description="Semantic search service for ISA contexts using TF-IDF",
    version="1.0.0"
)

# Initialize database
db = SimpleVectorDB()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simple-vector-db"}

@app.post("/add_chunks")
async def add_chunks(chunks: List[ContextChunk]):
    """Add context chunks to the database"""
    try:
        result = db.add_chunks(chunks)
        return result
    except Exception as e:
        logger.error(f"Error adding chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_chunks(search_query: SearchQuery):
    """Search for similar context chunks"""
    try:
        results = db.search(
            query=search_query.query,
            limit=search_query.limit,
            min_score=search_query.min_score
        )
        
        return SearchResponse(
            results=results,
            total_count=len(results)
        )
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_chunks")
async def delete_chunks(delete_request: DeleteRequest):
    """Delete chunks by IDs"""
    try:
        result = db.delete_chunks(delete_request.chunk_ids)
        return result
    except Exception as e:
        logger.error(f"Error deleting chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rebuild")
async def rebuild_index():
    """Rebuild the vector index"""
    try:
        result = db.rebuild_index()
        return result
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting Simple Vector Database Service...")
    uvicorn.run(
        "vector_service_simple:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )