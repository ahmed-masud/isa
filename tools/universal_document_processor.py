#!/usr/bin/env python3
"""
ISA Universal Document Processor
Detects file types and converts various document formats to markdown for ISA contexts
"""

import os
import sys
import subprocess
import argparse
import mimetypes
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import re
import json
from datetime import datetime


class UniversalDocumentProcessor:
    """Universal document processor that handles multiple file formats"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
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
        
        # File type mappings
        self.supported_types = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.doc': self._process_doc,
            '.xlsx': self._process_xlsx,
            '.xls': self._process_xls,
            '.pptx': self._process_pptx,
            '.ppt': self._process_ppt,
            '.odt': self._process_odt,
            '.ods': self._process_ods,
            '.odp': self._process_odp,
            '.rtf': self._process_rtf,
            '.txt': self._process_text,
            '.md': self._process_markdown,
            '.html': self._process_html,
            '.htm': self._process_html,
            '.csv': self._process_csv,
            '.tsv': self._process_csv,
            '.json': self._process_json,
            '.xml': self._process_xml,
            '.yaml': self._process_yaml,
            '.yml': self._process_yaml,
        }
    
    def _log(self, message: str, color: str = 'nc'):
        """Log message with optional color"""
        if self.verbose or color != 'nc':
            print(f"{self.colors[color]}{message}{self.colors['nc']}")
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[bool, str, str]:
        """Run a shell command and return success, stdout, stderr"""
        try:
            result = subprocess.run(cmd, capture_output=capture_output, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def _check_tool_available(self, tool: str) -> bool:
        """Check if a tool is available in the system"""
        success, _, _ = self._run_command(['which', tool])
        return success
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get basic file information"""
        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'extension': file_path.suffix.lower(),
            'mime_type': mime_type,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'path': str(file_path)
        }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Convert filename to safe markdown filename"""
        base_name = Path(filename).stem
        safe_name = re.sub(r'[^\w\-_.]', '-', base_name.lower())
        safe_name = re.sub(r'-+', '-', safe_name)
        safe_name = safe_name.strip('-')
        return f"{safe_name}.md"
    
    def _create_markdown_wrapper(self, content: str, title: str, file_info: Dict[str, Any], 
                               extraction_method: str = "Unknown") -> str:
        """Create standardized markdown wrapper for extracted content"""
        
        size_mb = file_info['size'] / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{file_info['size']} bytes"
        
        markdown = f"""# {title}

## Document Information
- **Original File**: {file_info['name']}
- **File Type**: {file_info['extension'].upper()} ({file_info['mime_type'] or 'Unknown'})
- **Size**: {size_str}
- **Modified**: {file_info['modified']}
- **Extraction Method**: {extraction_method}
- **Processed**: {datetime.now().isoformat()}
- **Added to ISA Context**: Auto-processed for semantic search

## Content

{content}

---

*This document was automatically processed by ISA Universal Document Processor for context integration and semantic search.*
"""
        
        return markdown
    
    # ========================= File Type Processors =========================
    
    def _process_pdf(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process PDF files"""
        self._log(f"📄 Processing PDF: {file_path.name}", 'blue')
        
        # Try pdftotext first (from poppler)
        if self._check_tool_available('pdftotext'):
            success, text, error = self._run_command(['pdftotext', str(file_path), '-'])
            if success and text.strip():
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(), 
                    file_info, "pdftotext (Poppler)"
                )
        
        # Try textutil on macOS
        if sys.platform == 'darwin' and self._check_tool_available('textutil'):
            success, text, error = self._run_command(['textutil', '-convert', 'txt', str(file_path), '-stdout'])
            if success and text.strip():
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "textutil (macOS)"
                )
        
        return False, f"Could not extract text from PDF. Install poppler-utils (brew install poppler)"
    
    def _process_docx(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process DOCX files"""
        self._log(f"📝 Processing DOCX: {file_path.name}", 'blue')
        
        try:
            # Extract text from DOCX using python-docx or pandoc
            if self._check_tool_available('pandoc'):
                success, text, error = self._run_command(['pandoc', str(file_path), '-t', 'plain'])
                if success:
                    cleaned_text = self._clean_extracted_text(text)
                    return True, self._create_markdown_wrapper(
                        cleaned_text, file_path.stem.replace('-', ' ').title(),
                        file_info, "pandoc"
                    )
            
            # Fallback: try textutil on macOS
            if sys.platform == 'darwin' and self._check_tool_available('textutil'):
                success, text, error = self._run_command(['textutil', '-convert', 'txt', str(file_path), '-stdout'])
                if success:
                    cleaned_text = self._clean_extracted_text(text)
                    return True, self._create_markdown_wrapper(
                        cleaned_text, file_path.stem.replace('-', ' ').title(),
                        file_info, "textutil (macOS)"
                    )
            
            # Manual DOCX parsing (basic)
            return self._manual_docx_extraction(file_path, file_info)
            
        except Exception as e:
            return False, f"Error processing DOCX: {e}"
    
    def _manual_docx_extraction(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Manual DOCX text extraction"""
        try:
            text_content = []
            with zipfile.ZipFile(file_path, 'r') as docx:
                # Read the main document
                if 'word/document.xml' in docx.namelist():
                    xml_content = docx.read('word/document.xml')
                    root = ET.fromstring(xml_content)
                    
                    # Extract text from paragraphs
                    for p in root.iter():
                        if p.tag.endswith('}t'):  # Text runs
                            if p.text:
                                text_content.append(p.text)
                        elif p.tag.endswith('}p'):  # Paragraphs
                            text_content.append('\n')
            
            if text_content:
                cleaned_text = self._clean_extracted_text(''.join(text_content))
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "Manual XML extraction"
                )
            
            return False, "No text content found in DOCX"
            
        except Exception as e:
            return False, f"Manual DOCX extraction failed: {e}"
    
    def _process_doc(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process legacy DOC files"""
        self._log(f"📝 Processing DOC: {file_path.name}", 'blue')
        
        # Try textutil on macOS
        if sys.platform == 'darwin' and self._check_tool_available('textutil'):
            success, text, error = self._run_command(['textutil', '-convert', 'txt', str(file_path), '-stdout'])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "textutil (macOS)"
                )
        
        # Try antiword if available
        if self._check_tool_available('antiword'):
            success, text, error = self._run_command(['antiword', str(file_path)])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "antiword"
                )
        
        return False, "Could not process DOC file. Try converting to DOCX first."
    
    def _process_xlsx(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process XLSX files"""
        self._log(f"📊 Processing XLSX: {file_path.name}", 'blue')
        
        # Try pandas if available (would need to be installed)
        # For now, use a basic approach
        try:
            import csv
            import io
            
            # Convert to CSV first if possible
            if self._check_tool_available('xlsx2csv'):
                success, csv_text, error = self._run_command(['xlsx2csv', str(file_path)])
                if success:
                    return True, self._create_markdown_wrapper(
                        self._format_csv_as_table(csv_text),
                        file_path.stem.replace('-', ' ').title(),
                        file_info, "xlsx2csv"
                    )
            
            return False, "XLSX processing requires xlsx2csv tool"
            
        except Exception as e:
            return False, f"Error processing XLSX: {e}"
    
    def _process_xls(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process legacy XLS files"""
        self._log(f"📊 Processing XLS: {file_path.name}", 'blue')
        return False, "XLS processing not yet implemented. Convert to XLSX first."
    
    def _process_pptx(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process PPTX files"""
        self._log(f"🎭 Processing PPTX: {file_path.name}", 'blue')
        
        if self._check_tool_available('pandoc'):
            success, text, error = self._run_command(['pandoc', str(file_path), '-t', 'plain'])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "pandoc"
                )
        
        # Manual PPTX extraction
        return self._manual_pptx_extraction(file_path, file_info)
    
    def _manual_pptx_extraction(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Manual PPTX text extraction"""
        try:
            slides_content = []
            with zipfile.ZipFile(file_path, 'r') as pptx:
                # Find all slide files
                slide_files = [f for f in pptx.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
                slide_files.sort()
                
                for slide_file in slide_files:
                    xml_content = pptx.read(slide_file)
                    root = ET.fromstring(xml_content)
                    
                    slide_text = []
                    for t in root.iter():
                        if t.tag.endswith('}t') and t.text:
                            slide_text.append(t.text)
                    
                    if slide_text:
                        slides_content.append(f"## Slide {len(slides_content) + 1}\n\n" + '\n'.join(slide_text))
            
            if slides_content:
                all_content = '\n\n'.join(slides_content)
                return True, self._create_markdown_wrapper(
                    all_content, file_path.stem.replace('-', ' ').title(),
                    file_info, "Manual XML extraction"
                )
            
            return False, "No text content found in PPTX"
            
        except Exception as e:
            return False, f"Manual PPTX extraction failed: {e}"
    
    def _process_ppt(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process legacy PPT files"""
        self._log(f"🎭 Processing PPT: {file_path.name}", 'blue')
        return False, "PPT processing not yet implemented. Convert to PPTX first."
    
    def _process_odt(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process OpenDocument Text files"""
        self._log(f"📄 Processing ODT: {file_path.name}", 'blue')
        
        if self._check_tool_available('pandoc'):
            success, text, error = self._run_command(['pandoc', str(file_path), '-t', 'plain'])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "pandoc"
                )
        
        return False, "ODT processing requires pandoc"
    
    def _process_ods(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process OpenDocument Spreadsheet files"""
        self._log(f"📊 Processing ODS: {file_path.name}", 'blue')
        return False, "ODS processing not yet implemented"
    
    def _process_odp(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process OpenDocument Presentation files"""
        self._log(f"🎭 Processing ODP: {file_path.name}", 'blue')
        
        if self._check_tool_available('pandoc'):
            success, text, error = self._run_command(['pandoc', str(file_path), '-t', 'plain'])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "pandoc"
                )
        
        return False, "ODP processing requires pandoc"
    
    def _process_rtf(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process RTF files"""
        self._log(f"📝 Processing RTF: {file_path.name}", 'blue')
        
        if self._check_tool_available('pandoc'):
            success, text, error = self._run_command(['pandoc', str(file_path), '-t', 'plain'])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "pandoc"
                )
        
        # Try textutil on macOS
        if sys.platform == 'darwin' and self._check_tool_available('textutil'):
            success, text, error = self._run_command(['textutil', '-convert', 'txt', str(file_path), '-stdout'])
            if success:
                cleaned_text = self._clean_extracted_text(text)
                return True, self._create_markdown_wrapper(
                    cleaned_text, file_path.stem.replace('-', ' ').title(),
                    file_info, "textutil (macOS)"
                )
        
        return False, "RTF processing requires pandoc or textutil"
    
    def _process_text(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process plain text files"""
        self._log(f"📄 Processing TXT: {file_path.name}", 'blue')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return True, self._create_markdown_wrapper(
                content, file_path.stem.replace('-', ' ').title(),
                file_info, "Direct text read"
            )
            
        except Exception as e:
            return False, f"Error reading text file: {e}"
    
    def _process_markdown(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process markdown files (already in correct format)"""
        self._log(f"📝 Processing Markdown: {file_path.name}", 'blue')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Markdown files are already in the right format, just return content
            return True, content
            
        except Exception as e:
            return False, f"Error reading markdown file: {e}"
    
    def _process_html(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process HTML files"""
        self._log(f"🌐 Processing HTML: {file_path.name}", 'blue')
        
        if self._check_tool_available('pandoc'):
            success, text, error = self._run_command(['pandoc', str(file_path), '-t', 'markdown'])
            if success:
                return True, text
        
        # Basic HTML text extraction
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                html_content = f.read()
            
            # Very basic HTML tag removal
            import re
            text = re.sub(r'<[^>]+>', '', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return True, self._create_markdown_wrapper(
                text, file_path.stem.replace('-', ' ').title(),
                file_info, "Basic HTML tag removal"
            )
            
        except Exception as e:
            return False, f"Error processing HTML: {e}"
    
    def _process_csv(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process CSV/TSV files"""
        self._log(f"📊 Processing CSV: {file_path.name}", 'blue')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            table_content = self._format_csv_as_table(content)
            return True, self._create_markdown_wrapper(
                table_content, file_path.stem.replace('-', ' ').title(),
                file_info, "CSV to Markdown table"
            )
            
        except Exception as e:
            return False, f"Error processing CSV: {e}"
    
    def _process_json(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process JSON files"""
        self._log(f"⚙️ Processing JSON: {file_path.name}", 'blue')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            
            # Pretty print JSON
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            content = f"```json\n{formatted_json}\n```"
            
            return True, self._create_markdown_wrapper(
                content, file_path.stem.replace('-', ' ').title(),
                file_info, "JSON pretty-print"
            )
            
        except Exception as e:
            return False, f"Error processing JSON: {e}"
    
    def _process_xml(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process XML files"""
        self._log(f"⚙️ Processing XML: {file_path.name}", 'blue')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Format XML content
            formatted_content = f"```xml\n{content}\n```"
            
            return True, self._create_markdown_wrapper(
                formatted_content, file_path.stem.replace('-', ' ').title(),
                file_info, "XML formatting"
            )
            
        except Exception as e:
            return False, f"Error processing XML: {e}"
    
    def _process_yaml(self, file_path: Path, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Process YAML files"""
        self._log(f"⚙️ Processing YAML: {file_path.name}", 'blue')
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Format YAML content
            formatted_content = f"```yaml\n{content}\n```"
            
            return True, self._create_markdown_wrapper(
                formatted_content, file_path.stem.replace('-', ' ').title(),
                file_info, "YAML formatting"
            )
            
        except Exception as e:
            return False, f"Error processing YAML: {e}"
    
    # ========================= Utility Methods =========================
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text for better markdown formatting"""
        if not text:
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Clean up common document artifacts
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Remove page numbers
        text = re.sub(r'\f', '\n\n', text)  # Replace form feeds with paragraph breaks
        
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n ', '\n', text)
        
        return text.strip()
    
    def _format_csv_as_table(self, csv_content: str) -> str:
        """Convert CSV content to markdown table"""
        lines = csv_content.strip().split('\n')
        if not lines:
            return csv_content
        
        # Simple CSV to markdown table conversion
        try:
            import csv
            import io
            
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)
            
            if not rows:
                return csv_content
            
            # Create markdown table
            table_lines = []
            
            # Header row
            header = rows[0]
            table_lines.append('| ' + ' | '.join(header) + ' |')
            table_lines.append('|' + '---|' * len(header))
            
            # Data rows (limit to first 50 rows to avoid huge tables)
            for row in rows[1:51]:  
                padded_row = row + [''] * (len(header) - len(row))  # Pad short rows
                table_lines.append('| ' + ' | '.join(padded_row[:len(header)]) + ' |')
            
            if len(rows) > 51:
                table_lines.append(f'| ... | {len(rows) - 51} more rows ... |')
            
            return '\n'.join(table_lines)
            
        except Exception:
            # Fallback to formatted text
            return f"```\n{csv_content}\n```"
    
    def detect_file_type(self, file_path: Path) -> str:
        """Detect file type based on extension and content"""
        extension = file_path.suffix.lower()
        
        if extension in self.supported_types:
            return extension
        
        # Try to detect by mime type or content
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('text/'):
                return '.txt'
            elif 'pdf' in mime_type:
                return '.pdf'
        
        return 'unknown'
    
    def process_file(self, file_path: str, context_dir: str) -> Tuple[bool, str]:
        """Process a single file and convert to markdown in context directory"""
        
        source_path = Path(file_path)
        target_dir = Path(context_dir)
        
        if not source_path.exists():
            return False, f"Source file not found: {file_path}"
        
        if not target_dir.exists():
            return False, f"Context directory not found: {context_dir}"
        
        # Get file info
        file_info = self._get_file_info(source_path)
        file_type = self.detect_file_type(source_path)
        
        self._log(f"🔍 Detected file type: {file_type}", 'cyan')
        
        if file_type == 'unknown' or file_type not in self.supported_types:
            return False, f"Unsupported file type: {file_type}. Supported: {', '.join(self.supported_types.keys())}"
        
        # Process the file
        processor = self.supported_types[file_type]
        success, result = processor(source_path, file_info)
        
        if not success:
            return False, result
        
        # Save markdown file
        output_filename = self._sanitize_filename(source_path.name)
        output_path = target_dir / output_filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            self._log(f"✅ Created: {output_path}", 'green')
            return True, str(output_path)
            
        except Exception as e:
            return False, f"Error saving markdown file: {e}"
    
    def list_supported_types(self) -> None:
        """List all supported file types"""
        print(f"{self.colors['white']}📋 Supported File Types:{self.colors['nc']}")
        print()
        
        categories = {
            'Documents': ['.pdf', '.docx', '.doc', '.odt', '.rtf'],
            'Spreadsheets': ['.xlsx', '.xls', '.ods', '.csv', '.tsv'],
            'Presentations': ['.pptx', '.ppt', '.odp'],
            'Text': ['.txt', '.md', '.html', '.htm'],
            'Data': ['.json', '.xml', '.yaml', '.yml']
        }
        
        for category, extensions in categories.items():
            print(f"{self.colors['cyan']}{category}:{self.colors['nc']}")
            available = []
            for ext in extensions:
                if ext in self.supported_types:
                    available.append(ext)
            print(f"  {', '.join(available)}")
            print()


def main():
    parser = argparse.ArgumentParser(description='Universal Document Processor for ISA')
    parser.add_argument('file', nargs='?', help='File to process')
    parser.add_argument('--context', '-c', help='ISA context directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--list-types', action='store_true', help='List supported file types')
    
    args = parser.parse_args()
    
    processor = UniversalDocumentProcessor(verbose=args.verbose)
    
    if args.list_types:
        processor.list_supported_types()
        return
    
    # Require file and context for processing
    if not args.file:
        parser.error('file argument is required when not using --list-types')
    if not args.context:
        parser.error('--context/-c is required when processing files')
    
    success, result = processor.process_file(args.file, args.context)
    
    if success:
        print(f"✅ Successfully processed: {result}")
    else:
        print(f"❌ Error: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()