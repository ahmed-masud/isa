#!/usr/bin/env python3
"""
ISA Context Chunking and Embedding Processor
Converts ISA markdown files into chunks and sends them to the vector database.
"""

import os
import sys
import re
import json
import hashlib
import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path

import requests
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContextChunk:
    """Represents a chunk of context"""
    text: str
    source: str
    section: str
    chunk_id: str
    metadata: Dict[str, Any]

class MarkdownChunker:
    """Intelligent markdown chunker that respects document structure"""
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_markdown(self, content: str, source_path: str) -> List[ContextChunk]:
        """Chunk markdown content while preserving structure"""
        chunks = []
        
        # Split by major sections (## headers)
        sections = self._split_by_headers(content)
        
        for section_title, section_content in sections:
            # Further chunk large sections
            section_chunks = self._chunk_section(section_content, section_title)
            
            for i, chunk_text in enumerate(section_chunks):
                if chunk_text.strip():  # Only add non-empty chunks
                    # Generate unique chunk ID based on content and source
                    normalized_source = self._normalize_source_path(source_path)
                    chunk_id = self._generate_chunk_id(chunk_text.strip(), normalized_source, section_title or "header", i)
                    
                    chunk = ContextChunk(
                        text=chunk_text.strip(),
                        source=normalized_source,
                        section=section_title or "header",
                        chunk_id=chunk_id,
                        metadata={
                            "file_path": source_path,
                            "chunk_size": len(chunk_text),
                            "context_type": self._infer_context_type(source_path),
                            "section_title": section_title
                        }
                    )
                    chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {source_path}")
        return chunks
    
    def _split_by_headers(self, content: str) -> List[tuple]:
        """Split content by major markdown headers"""
        sections = []
        current_section = ""
        current_title = ""
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for major headers (## level)
            header_match = re.match(r'^#+\s+(.+)$', line)
            
            if header_match and line.startswith('##'):
                # Save previous section
                if current_section.strip():
                    sections.append((current_title, current_section))
                
                # Start new section
                current_title = header_match.group(1).strip()
                current_section = line + '\n'
            else:
                current_section += line + '\n'
        
        # Add final section
        if current_section.strip():
            sections.append((current_title, current_section))
        
        return sections
    
    def _chunk_section(self, content: str, section_title: str) -> List[str]:
        """Chunk a section if it's too large"""
        if len(content) <= self.max_chunk_size:
            return [content]
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit, start new chunk
            if len(current_chunk) + len(paragraph) > self.max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = paragraph + '\n\n'
            else:
                current_chunk += paragraph + '\n\n'
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def _normalize_source_path(self, path: str) -> str:
        """Normalize source path for consistent referencing"""
        # Convert absolute path to relative from ISA_CONTEXTS
        isa_contexts = os.getenv('ISA_CONTEXTS', '/Users/masud/.config/isa/contexts')
        if path.startswith(isa_contexts):
            return path[len(isa_contexts):].lstrip('/')
        return os.path.basename(path)
    
    def _infer_context_type(self, path: str) -> str:
        """Infer context type from file path"""
        if '/people/' in path:
            return 'person'
        elif '/places/' in path:
            return 'place'
        elif '/things/' in path:
            return 'project'
        elif 'PRIORITIES' in path:
            return 'priorities'
        elif 'README' in path:
            return 'overview'
        else:
            return 'general'
    
    def _generate_chunk_id(self, text: str, source: str, section: str, index: int) -> str:
        """Generate unique chunk ID based on content and metadata"""
        content = f"{source}:{section}:{index}:{text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

class VectorClient:
    """Client for communicating with the vector database service"""
    
    def __init__(self, service_url: str = "http://192.168.1.161:8000"):
        self.service_url = service_url
    
    def add_chunks(self, chunks: List[ContextChunk]) -> Dict[str, Any]:
        """Send chunks to the vector database"""
        try:
            # Convert chunks to API format for simple vector service
            chunk_data = []
            for chunk in chunks:
                # Merge all metadata including source, section info
                merged_metadata = chunk.metadata.copy()
                merged_metadata.update({
                    "source": chunk.source,
                    "section": chunk.section,
                    "chunk_id": chunk.chunk_id
                })
                
                chunk_data.append({
                    "text": chunk.text,
                    "metadata": merged_metadata,
                    "chunk_id": chunk.chunk_id
                })
            
            # Send to vector service
            logger.debug(f"Sending {len(chunk_data)} chunks to vector service")
            response = requests.post(
                f"{self.service_url}/add_chunks",
                json=chunk_data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully added {result.get('added', 0)} chunks to vector database (total: {result.get('total', 0)})")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to communicate with vector service: {e}")
            raise
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            raise
    
    def delete_source(self, source: str) -> Dict[str, Any]:
        """Delete all chunks from a specific source (not implemented in simple service)"""
        logger.warning(f"Delete source functionality not implemented in simple vector service")
        return {"deleted": 0, "reason": "not_implemented"}
    
    def test_connection(self) -> bool:
        """Test connection to vector service"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

def process_file(file_path: str, vector_service_url: str = "http://192.168.1.161:8000", 
                max_chunk_size: int = 1000) -> bool:
    """Process a single markdown file"""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Initialize components
        chunker = MarkdownChunker(max_chunk_size=max_chunk_size)
        client = VectorClient(service_url=vector_service_url)
        
        # Test connection first
        if not client.test_connection():
            logger.error(f"Cannot connect to vector service at {vector_service_url}")
            return False
        
        # Delete existing chunks from this source first
        source = chunker._normalize_source_path(file_path)
        try:
            client.delete_source(source)
        except Exception as e:
            logger.warning(f"Could not delete existing chunks: {e}")
        
        # Chunk the content
        chunks = chunker.chunk_markdown(content, file_path)
        
        if not chunks:
            logger.warning(f"No chunks generated from {file_path}")
            return True
        
        # Send to vector database in smaller batches
        batch_size = 10
        total_added = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            result = client.add_chunks(batch)
            total_added += result.get('added', 0)
            logger.info(f"Batch {i//batch_size + 1}: Added {result.get('added', 0)} chunks")
        
        logger.info(f"Total chunks added: {total_added}")
        
        logger.info(f"Successfully processed {file_path} -> {len(chunks)} chunks")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Process ISA contexts into vector database")
    parser.add_argument("file_path", help="Path to markdown file to process")
    parser.add_argument("--service-url", default="http://192.168.1.161:8000", 
                       help="Vector service URL")
    parser.add_argument("--chunk-size", type=int, default=1000,
                       help="Maximum chunk size in characters")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate file exists
    if not os.path.exists(args.file_path):
        logger.error(f"File not found: {args.file_path}")
        sys.exit(1)
    
    # Process file
    success = process_file(
        file_path=args.file_path,
        vector_service_url=args.service_url,
        max_chunk_size=args.chunk_size
    )
    
    if success:
        print(f"✅ Successfully processed {args.file_path}")
        sys.exit(0)
    else:
        print(f"❌ Failed to process {args.file_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()