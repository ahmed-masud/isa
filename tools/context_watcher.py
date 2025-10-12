#!/usr/bin/env python3
"""
ISA Context Watcher
Monitors ISA context files for changes and automatically updates the vector database.
"""

import os
import sys
import json
import time
import hashlib
import logging
import argparse
from pathlib import Path
from typing import Dict, Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from chunk_and_embed import process_file

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextChangeHandler(FileSystemEventHandler):
    """Handle file system events for ISA contexts"""
    
    def __init__(self, vector_service_url: str = "http://192.168.1.161:8000", 
                 hash_file: str = ".context_hashes.json"):
        self.service_url = vector_service_url
        self.hash_file = hash_file
        self.file_hashes = self.load_file_hashes()
        self.processing_queue: Set[str] = set()
        
    def load_file_hashes(self) -> Dict[str, str]:
        """Load file hashes from disk"""
        try:
            if os.path.exists(self.hash_file):
                with open(self.hash_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading file hashes: {e}")
            return {}
    
    def save_file_hashes(self):
        """Save file hashes to disk"""
        try:
            with open(self.hash_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving file hashes: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return ""
    
    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        # Only process markdown files
        if not file_path.endswith('.md'):
            return False
        
        # Skip temporary files
        if '/.git/' in file_path or file_path.endswith('.tmp'):
            return False
        
        # Check if it's in ISA contexts directory
        isa_contexts = os.getenv('ISA_CONTEXTS', '/Users/masud/.config/isa/contexts')
        return file_path.startswith(isa_contexts)
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if not self.should_process_file(file_path):
            return
        
        # Avoid processing the same file multiple times quickly
        if file_path in self.processing_queue:
            return
        
        # Calculate current hash
        current_hash = self.get_file_hash(file_path)
        if not current_hash:
            return
        
        # Check if file actually changed
        if file_path in self.file_hashes and self.file_hashes[file_path] == current_hash:
            return
        
        logger.info(f"Context file changed: {file_path}")
        self.processing_queue.add(file_path)
        
        try:
            # Process the file
            success = process_file(
                file_path=file_path,
                vector_service_url=self.service_url,
                max_chunk_size=1000
            )
            
            if success:
                self.file_hashes[file_path] = current_hash
                self.save_file_hashes()
                logger.info(f"✅ Updated vector database for: {file_path}")
            else:
                logger.error(f"❌ Failed to update vector database for: {file_path}")
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        finally:
            self.processing_queue.discard(file_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if not self.should_process_file(file_path):
            return
        
        # Small delay to ensure file is fully written
        time.sleep(1)
        
        logger.info(f"New context file created: {file_path}")
        self.on_modified(event)  # Reuse modification logic
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if file_path in self.file_hashes:
            del self.file_hashes[file_path]
            self.save_file_hashes()
            logger.info(f"Removed hash for deleted file: {file_path}")

class ContextWatcher:
    """Main context watcher service"""
    
    def __init__(self, contexts_dir: str, vector_service_url: str = "http://192.168.1.161:8000"):
        self.contexts_dir = contexts_dir
        self.service_url = vector_service_url
        self.observer = Observer()
        self.handler = ContextChangeHandler(vector_service_url)
        
    def start_watching(self):
        """Start watching for context changes"""
        logger.info(f"Starting context watcher for: {self.contexts_dir}")
        logger.info(f"Vector service: {self.service_url}")
        
        # Setup file system watcher
        self.observer.schedule(
            self.handler, 
            self.contexts_dir, 
            recursive=True
        )
        
        # Start observer
        self.observer.start()
        logger.info("Context watcher started successfully")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping context watcher...")
            self.observer.stop()
        
        self.observer.join()
        logger.info("Context watcher stopped")
    
    def process_all_contexts(self):
        """Process all existing contexts on startup"""
        logger.info("Processing all existing contexts...")
        
        processed = 0
        failed = 0
        
        for root, dirs, files in os.walk(self.contexts_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        success = process_file(
                            file_path=file_path,
                            vector_service_url=self.service_url,
                            max_chunk_size=1000
                        )
                        
                        if success:
                            # Update hash
                            file_hash = self.handler.get_file_hash(file_path)
                            self.handler.file_hashes[file_path] = file_hash
                            processed += 1
                        else:
                            failed += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        failed += 1
        
        # Save hashes
        self.handler.save_file_hashes()
        
        logger.info(f"Initial processing complete: {processed} successful, {failed} failed")
        return processed, failed

def main():
    parser = argparse.ArgumentParser(description="ISA Context Watcher")
    parser.add_argument("--contexts-dir", 
                       default=os.getenv('ISA_CONTEXTS', '/Users/masud/.config/isa/contexts'),
                       help="ISA contexts directory to watch")
    parser.add_argument("--service-url", default="http://192.168.1.161:8000",
                       help="Vector service URL")
    parser.add_argument("--process-all", action="store_true",
                       help="Process all existing contexts before starting watcher")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate contexts directory
    if not os.path.exists(args.contexts_dir):
        logger.error(f"Contexts directory not found: {args.contexts_dir}")
        sys.exit(1)
    
    # Initialize watcher
    watcher = ContextWatcher(args.contexts_dir, args.service_url)
    
    # Process all existing contexts if requested
    if args.process_all:
        processed, failed = watcher.process_all_contexts()
        if failed > 0:
            logger.warning(f"Some files failed to process: {failed}")
    
    # Start watching for changes
    watcher.start_watching()

if __name__ == "__main__":
    main()