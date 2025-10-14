#!/usr/bin/env python3
"""
ISA Google Drive Integration
Context-aware Google Drive mounting using rclone
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class GoogleDriveManager:
    """Manages Google Drive mounts for ISA contexts"""
    
    def __init__(self, config_dir: str = None):
        """Initialize Google Drive manager"""
        self.config_dir = Path(config_dir or os.path.expanduser('~/.config/isa'))
        self.mounts_dir = Path.home() / 'GoogleDrive'
        self.drive_config_file = self.config_dir / 'google_drives.json'
        self.mount_status_file = self.config_dir / '.drive_mounts.json'
        
        # Common Google Drive for Desktop locations
        self.official_drive_locations = [
            Path.home() / 'Google Drive',
            Path.home() / 'GoogleDrive',
            '/Volumes/GoogleDrive',
            Path.home() / 'My Drive',
        ]
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.mounts_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configurations
        self.drive_configs = self._load_drive_configs()
        self.mount_status = self._load_mount_status()
        
        # Detect preferred backend
        self.backend = self._detect_preferred_backend()
        
        # Colors for output
        self.colors = {
            'red': '\033[0;31m',
            'green': '\033[0;32m',
            'yellow': '\033[1;33m',
            'blue': '\033[0;34m',
            'purple': '\033[0;35m',
            'cyan': '\033[0;36m',
            'white': '\033[1;37m',
            'nc': '\033[0m'  # No Color
        }
    
    def _load_drive_configs(self) -> Dict:
        """Load Google Drive configurations from file"""
        if not self.drive_config_file.exists():
            # Create default configuration for ahmed-masud context
            default_config = {
                "contexts": {
                    "ahmed-masud": {
                        "email": "ahmed.masud@saf.ai",
                        "rclone_remote": "ahmed-masud-drive",
                        "mount_point": "ahmed-masud",
                        "description": "Ahmed Masud's Google Drive"
                    }
                }
            }
            self._save_drive_configs(default_config)
            return default_config
        
        try:
            with open(self.drive_config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load drive configs: {e}", file=sys.stderr)
            return {"contexts": {}}
    
    def _save_drive_configs(self, config: Dict) -> bool:
        """Save Google Drive configurations to file"""
        try:
            with open(self.drive_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Could not save drive configs: {e}", file=sys.stderr)
            return False
    
    def _load_mount_status(self) -> Dict:
        """Load mount status from file"""
        if not self.mount_status_file.exists():
            return {}
        
        try:
            with open(self.mount_status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load mount status: {e}", file=sys.stderr)
            return {}
    
    def _save_mount_status(self) -> bool:
        """Save mount status to file"""
        try:
            with open(self.mount_status_file, 'w') as f:
                json.dump(self.mount_status, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Could not save mount status: {e}", file=sys.stderr)
            return False
    
    def _get_current_context(self) -> Optional[str]:
        """Get the current ISA context"""
        current_context_file = self.config_dir / '.current_context'
        if current_context_file.exists():
            try:
                with open(current_context_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        return None
    
    def _detect_preferred_backend(self) -> str:
        """Detect preferred Google Drive backend (official app vs rclone)"""
        # Check if Google Drive for Desktop is running and has mounted drives
        if self._is_google_drive_app_running():
            official_mount = self._get_official_drive_mount()
            if official_mount and official_mount.exists():
                return 'official'
        
        # Fall back to rclone
        return 'rclone'
    
    def _is_google_drive_app_running(self) -> bool:
        """Check if Google Drive for Desktop is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'Google Drive'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_official_drive_mount(self) -> Optional[Path]:
        """Get the official Google Drive mount point if available"""
        for location in self.official_drive_locations:
            if location.exists() and location.is_dir():
                try:
                    # Check if directory has content (typical sign of being mounted)
                    contents = list(location.iterdir())
                    if len(contents) > 0:
                        return location
                except (PermissionError, OSError):
                    continue
        return None
    
    def _check_rclone_remote(self, remote_name: str) -> bool:
        """Check if rclone remote exists"""
        try:
            result = subprocess.run(['rclone', 'listremotes'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                remotes = [line.strip(':') for line in result.stdout.strip().split('\n') if line]
                return remote_name in remotes
        except Exception:
            pass
        return False
    
    def _is_mounted(self, mount_point: Path) -> bool:
        """Check if a directory is currently mounted"""
        try:
            # Check if mount point exists and has content (typical sign of being mounted)
            if not mount_point.exists():
                return False
                
            # Use psutil to check for mount points on macOS (if available)
            if PSUTIL_AVAILABLE:
                for partition in psutil.disk_partitions():
                    if partition.mountpoint == str(mount_point):
                        return True
                    
            # Alternative check: see if directory is non-empty and contains Google Drive files
            if mount_point.is_dir():
                try:
                    # Try to list contents - if it's a mount, this should work
                    contents = list(mount_point.iterdir())
                    return len(contents) > 0
                except (PermissionError, OSError):
                    return False
                    
        except Exception:
            pass
        return False
    
    def _mount_drive(self, remote_name: str, mount_point: Path, context_name: str) -> bool:
        """Mount a Google Drive using rclone"""
        try:
            print(f"{self.colors['blue']}🔗 Mounting {remote_name} to {mount_point}...{self.colors['nc']}")
            
            # Ensure mount point directory exists
            mount_point.mkdir(parents=True, exist_ok=True)
            
            # Mount command for macOS
            cmd = [
                'rclone', 'mount', f'{remote_name}:',
                str(mount_point),
                '--daemon',  # Run in background
                '--vfs-cache-mode', 'writes',  # Enable write caching
                '--vfs-cache-max-age', '1h',   # Cache for 1 hour
                '--dir-cache-time', '1h',      # Directory cache
                '--poll-interval', '1m',       # Poll for changes
                '--log-level', 'ERROR'         # Reduce log noise
            ]
            
            # Execute mount command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Wait a moment for mount to establish
                time.sleep(2)
                
                # Verify mount was successful
                if self._is_mounted(mount_point):
                    # Update mount status
                    self.mount_status[context_name] = {
                        'remote': remote_name,
                        'mount_point': str(mount_point),
                        'mounted_at': time.time(),
                        'status': 'mounted'
                    }
                    self._save_mount_status()
                    
                    print(f"{self.colors['green']}✅ Successfully mounted {remote_name}{self.colors['nc']}")
                    print(f"{self.colors['cyan']}📁 Available at: {mount_point}{self.colors['nc']}")
                    return True
                else:
                    print(f"{self.colors['red']}❌ Mount command succeeded but drive not accessible{self.colors['nc']}")
                    return False
            else:
                print(f"{self.colors['red']}❌ Mount failed: {result.stderr}{self.colors['nc']}")
                return False
                
        except Exception as e:
            print(f"{self.colors['red']}❌ Error mounting drive: {e}{self.colors['nc']}")
            return False
    
    def _unmount_drive(self, mount_point: Path, context_name: str) -> bool:
        """Unmount a Google Drive"""
        try:
            print(f"{self.colors['yellow']}📤 Unmounting {mount_point}...{self.colors['nc']}")
            
            # Unmount using fusermount (Linux) or umount (macOS)
            if sys.platform == 'darwin':  # macOS
                cmd = ['umount', str(mount_point)]
            else:  # Linux
                cmd = ['fusermount', '-u', str(mount_point)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Update mount status
                if context_name in self.mount_status:
                    self.mount_status[context_name]['status'] = 'unmounted'
                    self.mount_status[context_name]['unmounted_at'] = time.time()
                    self._save_mount_status()
                
                print(f"{self.colors['green']}✅ Successfully unmounted{self.colors['nc']}")
                return True
            else:
                print(f"{self.colors['red']}❌ Unmount failed: {result.stderr}{self.colors['nc']}")
                return False
                
        except Exception as e:
            print(f"{self.colors['red']}❌ Error unmounting drive: {e}{self.colors['nc']}")
            return False
    
    def mount_context_drive(self, context_name: str = None) -> bool:
        """Mount Google Drive for a specific context"""
        if not context_name:
            context_name = self._get_current_context()
            
        if not context_name:
            print(f"{self.colors['red']}❌ No context specified and no current context found{self.colors['nc']}")
            return False
        
        # Check if context has drive configuration
        if context_name not in self.drive_configs.get('contexts', {}):
            print(f"{self.colors['red']}❌ No Google Drive configured for context: {context_name}{self.colors['nc']}")
            return False
        
        # Check if using official Google Drive app
        if self.backend == 'official':
            return self._mount_official_drive(context_name)
        else:
            return self._mount_rclone_drive(context_name)
    
    def _mount_official_drive(self, context_name: str) -> bool:
        """Handle mounting with official Google Drive app"""
        official_mount = self._get_official_drive_mount()
        if not official_mount:
            print(f"{self.colors['yellow']}⚠️  Google Drive for Desktop not found or not running{self.colors['nc']}")
            print(f"{self.colors['cyan']}💡 Please start Google Drive for Desktop and sign in with {self.drive_configs['contexts'][context_name]['email']}{self.colors['nc']}")
            return False
        
        # Update mount status to point to official drive location
        self.mount_status[context_name] = {
            'backend': 'official',
            'mount_point': str(official_mount),
            'mounted_at': time.time(),
            'status': 'mounted'
        }
        self._save_mount_status()
        
        print(f"{self.colors['green']}✅ Using Google Drive for Desktop{self.colors['nc']}")
        print(f"{self.colors['cyan']}📁 Available at: {official_mount}{self.colors['nc']}")
        return True
    
    def _mount_rclone_drive(self, context_name: str) -> bool:
        """Handle mounting with rclone"""
        drive_config = self.drive_configs['contexts'][context_name]
        remote_name = drive_config['rclone_remote']
        mount_name = drive_config['mount_point']
        
        # Check if rclone remote exists
        if not self._check_rclone_remote(remote_name):
            print(f"{self.colors['red']}❌ rclone remote '{remote_name}' not found{self.colors['nc']}")
            print(f"{self.colors['yellow']}💡 Configure with: rclone config{self.colors['nc']}")
            return False
        
        mount_point = self.mounts_dir / mount_name
        
        # Check if already mounted
        if self._is_mounted(mount_point):
            print(f"{self.colors['yellow']}⚠️  Drive already mounted at {mount_point}{self.colors['nc']}")
            return True
        
        # Mount the drive with rclone
        return self._mount_drive(remote_name, mount_point, context_name)
    
    def unmount_context_drive(self, context_name: str = None) -> bool:
        """Unmount Google Drive for a specific context"""
        if not context_name:
            context_name = self._get_current_context()
            
        if not context_name:
            print(f"{self.colors['red']}❌ No context specified and no current context found{self.colors['nc']}")
            return False
        
        # Check if context is mounted
        if context_name not in self.mount_status:
            print(f"{self.colors['yellow']}⚠️  No mounted drive found for context: {context_name}{self.colors['nc']}")
            return False
        
        mount_info = self.mount_status[context_name]
        mount_point = Path(mount_info['mount_point'])
        
        return self._unmount_drive(mount_point, context_name)
    
    def list_drives(self) -> None:
        """List all configured Google Drives"""
        print(f"{self.colors['white']}🗂️  ISA Google Drive Configuration{self.colors['nc']}")
        print("=" * 50)
        
        contexts = self.drive_configs.get('contexts', {})
        if not contexts:
            print(f"{self.colors['cyan']}No Google Drives configured{self.colors['nc']}")
            return
        
        for context_name, config in contexts.items():
            mount_point = self.mounts_dir / config['mount_point']
            is_mounted = self._is_mounted(mount_point)
            
            status_icon = "✅ Mounted" if is_mounted else "❌ Not mounted"
            
            print(f"\n📂 {context_name}:")
            print(f"   Email: {config['email']}")
            print(f"   Remote: {config['rclone_remote']}")
            print(f"   Mount Point: {mount_point}")
            print(f"   Status: {status_icon}")
            
            if is_mounted and context_name in self.mount_status:
                mount_info = self.mount_status[context_name]
                mount_time = time.ctime(mount_info.get('mounted_at', 0))
                print(f"   Mounted At: {mount_time}")
    
    def show_mount_status(self) -> None:
        """Show current mount status"""
        current_context = self._get_current_context()
        
        print(f"{self.colors['white']}📀 Google Drive Mount Status{self.colors['nc']}")
        print("=" * 40)
        print(f"Backend: {self.colors['cyan']}{self.backend.title()}{self.colors['nc']}")
        
        if current_context:
            print(f"Current Context: {self.colors['green']}{current_context}{self.colors['nc']}")
        else:
            print(f"Current Context: {self.colors['yellow']}None{self.colors['nc']}")
        
        # Show official Google Drive status if available
        if self.backend == 'official':
            official_mount = self._get_official_drive_mount()
            if official_mount:
                print(f"Official Drive: {self.colors['green']}{official_mount}{self.colors['nc']}")
            else:
                print(f"Official Drive: {self.colors['red']}Not found{self.colors['nc']}")
        
        print()
        
        # Check all configured drives
        contexts = self.drive_configs.get('contexts', {})
        for context_name, config in contexts.items():
            if self.backend == 'official':
                # For official backend, check if it's available
                official_mount = self._get_official_drive_mount()
                is_mounted = official_mount is not None
                mount_point = official_mount if official_mount else "Not available"
            else:
                # For rclone backend, check traditional mount point
                mount_point = self.mounts_dir / config['mount_point']
                is_mounted = self._is_mounted(mount_point)
            
            status_color = self.colors['green'] if is_mounted else self.colors['red']
            status_text = "MOUNTED" if is_mounted else "NOT MOUNTED"
            active_marker = " (CURRENT)" if context_name == current_context else ""
            
            print(f"  {context_name}{active_marker}: {status_color}{status_text}{self.colors['nc']}")
            if is_mounted:
                print(f"    📁 {mount_point}")
    
    def auto_mount_current_context(self) -> bool:
        """Automatically mount drive for current context"""
        current_context = self._get_current_context()
        if not current_context:
            return False
            
        return self.mount_context_drive(current_context)
    
    def setup_rclone_remote(self, context_name: str) -> None:
        """Guide user through setting up rclone remote for context"""
        if context_name not in self.drive_configs.get('contexts', {}):
            print(f"{self.colors['red']}❌ No configuration found for context: {context_name}{self.colors['nc']}")
            return
        
        config = self.drive_configs['contexts'][context_name]
        remote_name = config['rclone_remote']
        email = config['email']
        
        print(f"{self.colors['blue']}🔧 Setting up rclone remote for {context_name}{self.colors['nc']}")
        print(f"Email: {email}")
        print(f"Remote name: {remote_name}")
        print()
        print("Run the following command to configure:")
        print(f"{self.colors['cyan']}rclone config{self.colors['nc']}")
        print()
        print("When prompted:")
        print(f"1. Choose 'n' for new remote")
        print(f"2. Name: {self.colors['yellow']}{remote_name}{self.colors['nc']}")
        print(f"3. Storage: {self.colors['yellow']}drive{self.colors['nc']} (Google Drive)")
        print(f"4. Follow the authentication flow")
        print(f"5. Use email: {self.colors['yellow']}{email}{self.colors['nc']}")


def main():
    """Command-line interface for Google Drive management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ISA Google Drive Integration')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Mount command
    mount_parser = subparsers.add_parser('mount', help='Mount Google Drive for context')
    mount_parser.add_argument('context', nargs='?', help='Context name (default: current)')
    
    # Unmount command
    unmount_parser = subparsers.add_parser('unmount', help='Unmount Google Drive for context')
    unmount_parser.add_argument('context', nargs='?', help='Context name (default: current)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all configured Google Drives')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show mount status')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup rclone remote for context')
    setup_parser.add_argument('context', help='Context name')
    
    # Auto-mount command
    auto_parser = subparsers.add_parser('auto-mount', help='Auto-mount drive for current context')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize Google Drive manager
    drive_manager = GoogleDriveManager()
    
    try:
        if args.command == 'mount':
            success = drive_manager.mount_context_drive(args.context)
            sys.exit(0 if success else 1)
        
        elif args.command == 'unmount':
            success = drive_manager.unmount_context_drive(args.context)
            sys.exit(0 if success else 1)
        
        elif args.command == 'list':
            drive_manager.list_drives()
        
        elif args.command == 'status':
            drive_manager.show_mount_status()
        
        elif args.command == 'setup':
            drive_manager.setup_rclone_remote(args.context)
        
        elif args.command == 'auto-mount':
            success = drive_manager.auto_mount_current_context()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()