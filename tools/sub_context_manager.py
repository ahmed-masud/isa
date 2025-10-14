#!/usr/bin/env python3
"""
ISA Sub-Context Manager
Manages temporary/experimental sub-contexts that inherit from parent contexts
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class SubContextManager:
    """Manages ISA sub-contexts that inherit from parent contexts"""
    
    def __init__(self, isa_config_dir: str = None):
        """Initialize SubContextManager"""
        self.isa_config = Path(isa_config_dir or os.path.expanduser('~/.config/isa'))
        self.contexts_dir = self.isa_config / 'contexts'
        self.sub_contexts_dir = self.isa_config / 'sub-contexts'
        self.sub_context_registry = self.isa_config / '.sub-contexts.json'
        
        # Ensure directories exist
        self.sub_contexts_dir.mkdir(parents=True, exist_ok=True)
        
        # Load registry
        self.registry = self._load_registry()
        
        # Colors for output
        self.colors = {
            'red': '\033[0;31m',
            'green': '\033[0;32m',
            'yellow': '\033[1;33m',
            'blue': '\033[0;34m',
            'purple': '\033[0;35m',
            'cyan': '\033[0;36m',
            'white': '\033[1;37m',
            'gray': '\033[0;90m',
            'nc': '\033[0m'  # No Color
        }
    
    def _load_registry(self) -> Dict:
        """Load sub-context registry"""
        if not self.sub_context_registry.exists():
            return {"sub_contexts": {}, "version": "1.0"}
        
        try:
            with open(self.sub_context_registry, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load sub-context registry: {e}")
            return {"sub_contexts": {}, "version": "1.0"}
    
    def _save_registry(self) -> bool:
        """Save sub-context registry"""
        try:
            with open(self.sub_context_registry, 'w') as f:
                json.dump(self.registry, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Could not save sub-context registry: {e}")
            return False
    
    def _find_parent_context(self, context_name: str) -> Optional[Tuple[str, Path]]:
        """Find parent context by name, return (type, path) or None"""
        for context_type in ['people', 'places', 'things']:
            context_path = self.contexts_dir / context_type / context_name
            if context_path.exists():
                return (context_type, context_path)
        return None
    
    def _copy_context_files(self, source_path: Path, dest_path: Path, prefix: str = "") -> bool:
        """Copy context files from source to destination with optional prefix"""
        try:
            # Copy all markdown files and directories
            for item in source_path.iterdir():
                if item.is_file() and item.suffix == '.md':
                    dest_name = f"{prefix}{item.name}" if prefix else item.name
                    shutil.copy2(item, dest_path / dest_name)
                elif item.is_dir() and not item.name.startswith('.'):
                    dest_dir_name = f"{prefix}{item.name}" if prefix else item.name
                    shutil.copytree(item, dest_path / dest_dir_name, dirs_exist_ok=True)
            return True
        except Exception as e:
            print(f"Error copying context files: {e}")
            return False
    
    def _blend_contexts(self, parent_contexts: List[Tuple[str, str, Path]], dest_path: Path) -> Dict[str, List[str]]:
        """Blend content from multiple parent contexts into destination"""
        blended_files = {}
        conflicts = []
        
        for parent_name, parent_type, parent_path in parent_contexts:
            print(f"  📥 Blending from {parent_type}/{parent_name}...")
            
            # Create a prefix for this parent to avoid naming conflicts
            prefix = f"{parent_name}-" if len(parent_contexts) > 1 else ""
            
            for item in parent_path.iterdir():
                if item.is_file() and item.suffix == '.md':
                    dest_name = f"{prefix}{item.name}" if prefix else item.name
                    dest_file = dest_path / dest_name
                    
                    if dest_file.exists():
                        conflicts.append((dest_name, parent_name, item))
                        # Append content instead of overwriting
                        with open(dest_file, 'a', encoding='utf-8') as f:
                            f.write(f"\n\n---\n# Additional content from {parent_type}/{parent_name}\n\n")
                            with open(item, 'r', encoding='utf-8') as source_f:
                                f.write(source_f.read())
                    else:
                        shutil.copy2(item, dest_file)
                    
                    # Track which parents contributed to this file
                    if dest_name not in blended_files:
                        blended_files[dest_name] = []
                    blended_files[dest_name].append(f"{parent_type}/{parent_name}")
                
                elif item.is_dir() and not item.name.startswith('.'):
                    dest_dir_name = f"{prefix}{item.name}" if prefix else item.name
                    dest_dir = dest_path / dest_dir_name
                    
                    if dest_dir.exists():
                        # Merge directory contents
                        self._copy_context_files(item, dest_dir)
                    else:
                        shutil.copytree(item, dest_dir, dirs_exist_ok=True)
                    
                    # Track directory sources
                    if dest_dir_name not in blended_files:
                        blended_files[dest_dir_name] = []
                    blended_files[dest_dir_name].append(f"{parent_type}/{parent_name}")
        
        # Create blending report
        if conflicts:
            print(f"  ⚠️  {len(conflicts)} files had naming conflicts and were merged")
        
        return blended_files
    
    def create_sub_context(self, sub_name: str, parent_names: List[str], description: str = "") -> bool:
        """Create a new sub-context inheriting from multiple parent contexts"""
        
        # Check if sub-context already exists
        if sub_name in self.registry['sub_contexts']:
            print(f"{self.colors['red']}❌ Sub-context '{sub_name}' already exists{self.colors['nc']}")
            return False
        
        # Validate all parent contexts exist
        parent_contexts = []
        for parent_name in parent_names:
            parent_info = self._find_parent_context(parent_name)
            if not parent_info:
                print(f"{self.colors['red']}❌ Parent context '{parent_name}' not found{self.colors['nc']}")
                return False
            parent_type, parent_path = parent_info
            parent_contexts.append((parent_name, parent_type, parent_path))
        
        parents_str = ", ".join([f"{t}/{n}" for n, t, _ in parent_contexts])
        print(f"{self.colors['blue']}🔄 Creating sub-context '{sub_name}' from: {parents_str}...{self.colors['nc']}")
        
        # Create sub-context directory
        sub_context_path = self.sub_contexts_dir / sub_name
        sub_context_path.mkdir(parents=True, exist_ok=True)
        
        # Blend content from all parent contexts
        print(f"{self.colors['cyan']}🎨 Blending content from {len(parent_contexts)} parent(s)...{self.colors['nc']}")
        try:
            blended_files = self._blend_contexts(parent_contexts, sub_context_path)
        except Exception as e:
            print(f"{self.colors['red']}❌ Error blending contexts: {e}{self.colors['nc']}")
            # Clean up on failure
            shutil.rmtree(sub_context_path, ignore_errors=True)
            return False
        
        # Create sub-context metadata
        timestamp = datetime.now().isoformat()
        parent_info_list = [{
            "name": name,
            "type": ptype,
            "path": str(path)
        } for name, ptype, path in parent_contexts]
        
        metadata = {
            "name": sub_name,
            "parent_contexts": parent_info_list,
            "blended_files": blended_files,
            "description": description,
            "created": timestamp,
            "last_modified": timestamp,
            "is_temporary": True,
            "auto_expire": None  # Can be set for auto-cleanup
        }
        
        # Create inheritance marker file
        inheritance_file = sub_context_path / '.sub-context-info.json'
        with open(inheritance_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update registry
        self.registry['sub_contexts'][sub_name] = metadata
        if not self._save_registry():
            # Clean up on failure
            shutil.rmtree(sub_context_path, ignore_errors=True)
            return False
        
        print(f"{self.colors['green']}✅ Sub-context '{sub_name}' created successfully{self.colors['nc']}")
        print(f"{self.colors['cyan']}📁 Location: {sub_context_path}{self.colors['nc']}")
        print(f"{self.colors['gray']}🔗 Inherits from: {parents_str}{self.colors['nc']}")
        print(f"{self.colors['gray']}📄 Blended {len(blended_files)} files/directories{self.colors['nc']}")
        
        return True
    
    def list_sub_contexts(self) -> None:
        """List all sub-contexts with their parent relationships"""
        print(f"{self.colors['white']}🌿 Sub-Contexts{self.colors['nc']}")
        print("═" * 40)
        
        if not self.registry['sub_contexts']:
            print(f"{self.colors['gray']}No sub-contexts created yet{self.colors['nc']}")
            print()
            print(f"{self.colors['cyan']}💡 Create one with: isa sub-create <name> <parent1> [parent2...]{self.colors['nc']}")
            return
        
        for sub_name, metadata in self.registry['sub_contexts'].items():
            created = metadata['created'][:10]  # Just date part
            
            # Check if sub-context directory still exists
            sub_path = self.sub_contexts_dir / sub_name
            status = "🟢" if sub_path.exists() else "🔴"
            
            print(f"{status} {sub_name}")
            
            # Handle both old (single parent) and new (multiple parents) format
            if 'parent_contexts' in metadata:
                # New format with multiple parents
                parents = [f"{p['type']}/{p['name']}" for p in metadata['parent_contexts']]
                parents_str = ", ".join(parents)
                print(f"  🔗 Inherits from: {parents_str}")
                
                # Show blending info if available
                if 'blended_files' in metadata and metadata['blended_files']:
                    file_count = len(metadata['blended_files'])
                    print(f"  🎨 Blended: {file_count} files/directories")
            else:
                # Legacy format with single parent
                parent = metadata.get('parent_context', 'unknown')
                parent_type = metadata.get('parent_type', 'unknown')
                print(f"  🔗 Inherits from: {parent_type}/{parent}")
            
            print(f"  📅 Created: {created}")
            
            if metadata.get('description'):
                print(f"  📝 Description: {metadata['description']}")
            
            print(f"  📁 Path: {sub_path}")
            print()
    
    def delete_sub_context(self, sub_name: str, force: bool = False) -> bool:
        """Delete a sub-context and all its files"""
        
        if sub_name not in self.registry['sub_contexts']:
            print(f"{self.colors['red']}❌ Sub-context '{sub_name}' not found{self.colors['nc']}")
            return False
        
        sub_path = self.sub_contexts_dir / sub_name
        metadata = self.registry['sub_contexts'][sub_name]
        
        if not force:
            print(f"{self.colors['yellow']}⚠️  About to delete sub-context '{sub_name}'{self.colors['nc']}")
            print(f"   Parent: {metadata['parent_type']}/{metadata['parent_context']}")
            print(f"   Path: {sub_path}")
            
            confirm = input("Are you sure? (y/N): ").lower().strip()
            if confirm != 'y':
                print("Deletion cancelled.")
                return False
        
        print(f"{self.colors['blue']}🗑️  Deleting sub-context '{sub_name}'...{self.colors['nc']}")
        
        # Remove directory and contents
        if sub_path.exists():
            shutil.rmtree(sub_path)
        
        # Remove from registry
        del self.registry['sub_contexts'][sub_name]
        
        if self._save_registry():
            print(f"{self.colors['green']}✅ Sub-context '{sub_name}' deleted successfully{self.colors['nc']}")
            return True
        else:
            print(f"{self.colors['red']}❌ Failed to update registry{self.colors['nc']}")
            return False
    
    def show_sub_context_info(self, sub_name: str) -> bool:
        """Show detailed information about a sub-context"""
        
        if sub_name not in self.registry['sub_contexts']:
            print(f"{self.colors['red']}❌ Sub-context '{sub_name}' not found{self.colors['nc']}")
            return False
        
        metadata = self.registry['sub_contexts'][sub_name]
        sub_path = self.sub_contexts_dir / sub_name
        
        print(f"{self.colors['white']}📋 Sub-Context: {sub_name}{self.colors['nc']}")
        print("═" * (15 + len(sub_name)))
        
        # Handle both old and new metadata formats
        if 'parent_contexts' in metadata:
            # New format with multiple parents
            print(f"🔗 Parent Contexts:")
            for i, parent in enumerate(metadata['parent_contexts'], 1):
                print(f"   {i}. {parent['type']}/{parent['name']}")
            
            # Show blending information
            if 'blended_files' in metadata and metadata['blended_files']:
                print(f"🎨 Blended Content:")
                for file_name, sources in metadata['blended_files'].items():
                    sources_str = ", ".join(sources)
                    print(f"   • {file_name} ← {sources_str}")
        else:
            # Legacy format with single parent
            parent_type = metadata.get('parent_type', 'unknown')
            parent_context = metadata.get('parent_context', 'unknown')
            print(f"🔗 Parent Context: {parent_type}/{parent_context}")
        
        print(f"📁 Location: {sub_path}")
        print(f"📅 Created: {metadata['created']}")
        print(f"🔄 Last Modified: {metadata['last_modified']}")
        
        if metadata.get('description'):
            print(f"📝 Description: {metadata['description']}")
        
        # Check if directory exists and show file count
        if sub_path.exists():
            file_count = len([f for f in sub_path.rglob('*.md')])
            print(f"📄 Markdown Files: {file_count}")
            print(f"✅ Status: Active")
        else:
            print(f"🔴 Status: Missing (directory not found)")
        
        return True
    
    def cleanup_orphaned(self) -> int:
        """Clean up orphaned sub-context directories and invalid registry entries"""
        cleaned_count = 0
        
        print(f"{self.colors['blue']}🧹 Cleaning up orphaned sub-contexts...{self.colors['nc']}")
        
        # Clean up directories without registry entries
        if self.sub_contexts_dir.exists():
            for sub_dir in self.sub_contexts_dir.iterdir():
                if sub_dir.is_dir() and sub_dir.name not in self.registry['sub_contexts']:
                    print(f"  🗑️  Removing orphaned directory: {sub_dir.name}")
                    shutil.rmtree(sub_dir)
                    cleaned_count += 1
        
        # Clean up registry entries without directories
        to_remove = []
        for sub_name in self.registry['sub_contexts']:
            sub_path = self.sub_contexts_dir / sub_name
            if not sub_path.exists():
                to_remove.append(sub_name)
        
        for sub_name in to_remove:
            print(f"  🗑️  Removing registry entry for missing: {sub_name}")
            del self.registry['sub_contexts'][sub_name]
            cleaned_count += 1
        
        if to_remove:
            self._save_registry()
        
        if cleaned_count > 0:
            print(f"{self.colors['green']}✅ Cleaned up {cleaned_count} orphaned items{self.colors['nc']}")
        else:
            print(f"{self.colors['gray']}No orphaned items found{self.colors['nc']}")
        
        return cleaned_count
    
    def sync_from_parents(self, sub_name: str) -> bool:
        """Re-sync sub-context with all its parents (overwrites changes)"""
        
        if sub_name not in self.registry['sub_contexts']:
            print(f"{self.colors['red']}❌ Sub-context '{sub_name}' not found{self.colors['nc']}")
            return False
        
        metadata = self.registry['sub_contexts'][sub_name]
        sub_path = self.sub_contexts_dir / sub_name
        
        # Handle both old and new metadata formats
        if 'parent_contexts' in metadata:
            # New format with multiple parents
            parent_contexts = []
            for parent_info in metadata['parent_contexts']:
                parent_name = parent_info['name']
                current_parent = self._find_parent_context(parent_name)
                if not current_parent:
                    print(f"{self.colors['red']}❌ Parent context '{parent_name}' not found{self.colors['nc']}")
                    return False
                parent_type, parent_path = current_parent
                parent_contexts.append((parent_name, parent_type, parent_path))
            
            parents_str = ", ".join([f"{t}/{n}" for n, t, _ in parent_contexts])
            print(f"{self.colors['yellow']}⚠️  This will overwrite all changes in '{sub_name}' and re-blend from: {parents_str}!{self.colors['nc']}")
        else:
            # Legacy format with single parent
            parent_name = metadata.get('parent_context', '')
            parent_info = self._find_parent_context(parent_name)
            if not parent_info:
                print(f"{self.colors['red']}❌ Parent context '{parent_name}' not found{self.colors['nc']}")
                return False
            parent_type, parent_path = parent_info
            parent_contexts = [(parent_name, parent_type, parent_path)]
            print(f"{self.colors['yellow']}⚠️  This will overwrite all changes in '{sub_name}'!{self.colors['nc']}")
        
        confirm = input("Continue? (y/N): ").lower().strip()
        if confirm != 'y':
            print("Sync cancelled.")
            return False
        
        print(f"{self.colors['blue']}🔄 Syncing '{sub_name}' from {len(parent_contexts)} parent(s)...{self.colors['nc']}")
        
        # Remove existing files (except metadata)
        for item in sub_path.iterdir():
            if item.name != '.sub-context-info.json':
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        
        # Re-blend content from all parents
        try:
            if len(parent_contexts) > 1:
                print(f"{self.colors['cyan']}🎨 Re-blending content from {len(parent_contexts)} parent(s)...{self.colors['nc']}")
                blended_files = self._blend_contexts(parent_contexts, sub_path)
                # Update blended files info in metadata
                metadata['blended_files'] = blended_files
            else:
                # Single parent, use simple copy
                _, _, parent_path = parent_contexts[0]
                if not self._copy_context_files(parent_path, sub_path):
                    return False
            
            # Update last modified
            metadata['last_modified'] = datetime.now().isoformat()
            self.registry['sub_contexts'][sub_name] = metadata
            self._save_registry()
            
            print(f"{self.colors['green']}✅ Sub-context '{sub_name}' synced successfully{self.colors['nc']}")
            return True
        except Exception as e:
            print(f"{self.colors['red']}❌ Error during sync: {e}{self.colors['nc']}")
            return False


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description='ISA Sub-Context Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create sub-context
    create_parser = subparsers.add_parser('create', help='Create a new sub-context')
    create_parser.add_argument('name', help='Sub-context name')
    create_parser.add_argument('parents', nargs='+', help='Parent context names (one or more)')
    create_parser.add_argument('--description', '-d', help='Optional description')
    
    # List sub-contexts
    list_parser = subparsers.add_parser('list', help='List all sub-contexts')
    
    # Show sub-context info
    info_parser = subparsers.add_parser('info', help='Show sub-context information')
    info_parser.add_argument('name', help='Sub-context name')
    
    # Delete sub-context
    delete_parser = subparsers.add_parser('delete', help='Delete a sub-context')
    delete_parser.add_argument('name', help='Sub-context name')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Sync from parent
    sync_parser = subparsers.add_parser('sync', help='Re-sync sub-context from all parents')
    sync_parser.add_argument('name', help='Sub-context name')
    
    # Cleanup orphaned
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up orphaned sub-contexts')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = SubContextManager()
    
    try:
        if args.command == 'create':
            success = manager.create_sub_context(args.name, args.parents, args.description or "")
            sys.exit(0 if success else 1)
        
        elif args.command == 'list':
            manager.list_sub_contexts()
        
        elif args.command == 'info':
            success = manager.show_sub_context_info(args.name)
            sys.exit(0 if success else 1)
        
        elif args.command == 'delete':
            success = manager.delete_sub_context(args.name, args.force)
            sys.exit(0 if success else 1)
        
        elif args.command == 'sync':
            success = manager.sync_from_parents(args.name)
            sys.exit(0 if success else 1)
        
        elif args.command == 'cleanup':
            manager.cleanup_orphaned()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()