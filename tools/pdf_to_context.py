#!/usr/bin/env python3
"""
ISA PDF to Context Converter
Extracts text from PDFs and converts to markdown format for ISA contexts
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import re
from typing import List, Tuple, Optional

class PDFContextConverter:
    """Converts PDFs to ISA context markdown files"""
    
    def __init__(self):
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
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[bool, str, str]:
        """Run a shell command and return success, stdout, stderr"""
        try:
            result = subprocess.run(cmd, capture_output=capture_output, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def _check_dependencies(self) -> bool:
        """Check if required tools are available"""
        tools = ['pdftotext']
        missing = []
        
        for tool in tools:
            success, _, _ = self._run_command(['which', tool])
            if not success:
                missing.append(tool)
        
        if missing:
            print(f"{self.colors['red']}❌ Missing required tools: {', '.join(missing)}{self.colors['nc']}")
            print(f"{self.colors['yellow']}💡 Install with: brew install poppler{self.colors['nc']}")
            return False
        
        return True
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text from PDF using pdftotext"""
        try:
            # Try pdftotext first (part of poppler-utils)
            success, text, error = self._run_command(['pdftotext', str(pdf_path), '-'])
            
            if success and text.strip():
                return text.strip()
            
            # Fallback: try textutil on macOS
            if sys.platform == 'darwin':
                success, text, error = self._run_command(['textutil', '-convert', 'txt', str(pdf_path), '-stdout'])
                if success and text.strip():
                    return text.strip()
            
            print(f"{self.colors['yellow']}⚠️ Could not extract text from {pdf_path.name}: {error}{self.colors['nc']}")
            return None
            
        except Exception as e:
            print(f"{self.colors['red']}❌ Error extracting text from {pdf_path.name}: {e}{self.colors['nc']}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text for better markdown formatting"""
        if not text:
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Clean up common PDF artifacts
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Remove page numbers
        text = re.sub(r'\f', '\n\n', text)  # Replace form feeds with paragraph breaks
        
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n ', '\n', text)
        
        return text.strip()
    
    def _format_as_markdown(self, text: str, title: str, pdf_path: Path) -> str:
        """Format extracted text as markdown"""
        
        # Clean the text
        clean_text = self._clean_text(text)
        
        # Create markdown content
        markdown = f"""# {title}

## Document Information
- **Source**: {pdf_path.name}
- **Full Path**: {pdf_path}
- **Added to ISA**: {Path.cwd().name} context
- **Extracted**: Auto-generated from PDF

## Content

{clean_text}

---

*This document was automatically extracted from PDF format for ISA context integration.*
"""
        
        return markdown
    
    def _sanitize_filename(self, filename: str) -> str:
        """Convert filename to safe markdown filename"""
        # Remove extension and sanitize
        base_name = Path(filename).stem
        
        # Replace spaces and special characters
        safe_name = re.sub(r'[^\w\-_.]', '-', base_name.lower())
        safe_name = re.sub(r'-+', '-', safe_name)  # Collapse multiple hyphens
        safe_name = safe_name.strip('-')  # Remove leading/trailing hyphens
        
        return f"{safe_name}.md"
    
    def convert_pdf_to_context(self, pdf_path: str, context_dir: str, title: str = None) -> bool:
        """Convert a PDF to markdown and save to context directory"""
        
        pdf_file = Path(pdf_path)
        context_path = Path(context_dir)
        
        # Validate inputs
        if not pdf_file.exists():
            print(f"{self.colors['red']}❌ PDF file not found: {pdf_path}{self.colors['nc']}")
            return False
        
        if not context_path.exists():
            print(f"{self.colors['red']}❌ Context directory not found: {context_dir}{self.colors['nc']}")
            return False
        
        # Generate title if not provided
        if not title:
            title = pdf_file.stem.replace('-', ' ').replace('_', ' ').title()
        
        print(f"{self.colors['blue']}📄 Processing: {pdf_file.name}{self.colors['nc']}")
        
        # Extract text
        text = self._extract_text_from_pdf(pdf_file)
        if not text:
            return False
        
        # Format as markdown
        markdown_content = self._format_as_markdown(text, title, pdf_file)
        
        # Generate output filename
        output_filename = self._sanitize_filename(pdf_file.name)
        output_path = context_path / output_filename
        
        # Save markdown file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"{self.colors['green']}✅ Created: {output_path}{self.colors['nc']}")
            print(f"{self.colors['cyan']}📊 Extracted {len(text)} characters{self.colors['nc']}")
            
            return True
            
        except Exception as e:
            print(f"{self.colors['red']}❌ Error saving markdown: {e}{self.colors['nc']}")
            return False
    
    def batch_convert(self, pdf_paths: List[str], context_dir: str) -> int:
        """Convert multiple PDFs to context directory"""
        
        if not self._check_dependencies():
            return 0
        
        print(f"{self.colors['white']}🔄 Converting {len(pdf_paths)} PDFs to ISA context{self.colors['nc']}")
        print(f"Target context: {context_dir}")
        print()
        
        success_count = 0
        
        for pdf_path in pdf_paths:
            if self.convert_pdf_to_context(pdf_path, context_dir):
                success_count += 1
            print()  # Add spacing between conversions
        
        print(f"{self.colors['white']}📊 Summary: {success_count}/{len(pdf_paths)} PDFs converted successfully{self.colors['nc']}")
        
        if success_count > 0:
            print(f"{self.colors['yellow']}💡 Next steps:{self.colors['nc']}")
            print(f"  1. Run: isa ctx-sync")
            print(f"  2. Test: isa ctx-search \"keyword from documents\"")
        
        return success_count


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description='Convert PDFs to ISA context markdown files')
    parser.add_argument('pdfs', nargs='+', help='PDF files to convert')
    parser.add_argument('--context', '-c', required=True, help='ISA context directory')
    parser.add_argument('--title', '-t', help='Custom title for single PDF conversion')
    
    args = parser.parse_args()
    
    converter = PDFContextConverter()
    
    # Convert PDFs
    success_count = converter.batch_convert(args.pdfs, args.context)
    
    # Exit with appropriate code
    sys.exit(0 if success_count > 0 else 1)


if __name__ == "__main__":
    main()