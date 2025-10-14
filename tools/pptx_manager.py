#!/usr/bin/env python3
"""
PowerPoint Presentation Manager - Create, Update, Delete slides
Based on the extract_pptx_for_isa.py template but extended for full CRUD operations.
"""

import sys
import os
import argparse
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

class PowerPointManager:
    def __init__(self, pptx_path=None):
        """Initialize with existing presentation or create new one."""
        if pptx_path and os.path.exists(pptx_path):
            self.prs = Presentation(pptx_path)
            self.pptx_path = pptx_path
            print(f"Loaded existing presentation: {pptx_path}")
        else:
            self.prs = Presentation()  # Create new presentation
            self.pptx_path = pptx_path or "new_presentation.pptx"
            print(f"Created new presentation: {self.pptx_path}")
    
    def save(self, output_path=None):
        """Save the presentation."""
        save_path = output_path or self.pptx_path
        self.prs.save(save_path)
        print(f"Saved presentation to: {save_path}")
        return save_path
    
    def list_slides(self):
        """List all slides with their content summary."""
        print(f"\nPresentation has {len(self.prs.slides)} slides:")
        print("-" * 50)
        
        for slide_num, slide in enumerate(self.prs.slides, 1):
            print(f"Slide {slide_num}:")
            
            # Get slide title if available
            title = self._get_slide_title(slide)
            if title:
                print(f"  Title: {title}")
            
            # Count text shapes
            text_shapes = [s for s in slide.shapes if hasattr(s, "text") and s.text.strip()]
            print(f"  Text shapes: {len(text_shapes)}")
            
            # Show first few lines of content
            if text_shapes:
                first_text = text_shapes[0].text.strip()[:100]
                if len(first_text) == 100:
                    first_text += "..."
                print(f"  Preview: {first_text}")
            
            print()
    
    def _get_slide_title(self, slide):
        """Extract title from slide if available."""
        try:
            if slide.shapes.title:
                return slide.shapes.title.text.strip()
        except:
            pass
        
        # Fallback: look for the first text shape
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                return shape.text.strip()
        
        return None
    
    def add_slide(self, title="New Slide", content=None, layout_index=1):
        """Add a new slide with title and content."""
        # Get slide layout (0=title, 1=title+content, 2=section header, etc.)
        slide_layout = self.prs.slide_layouts[layout_index]
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = title
        
        # Add content if provided
        if content and len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = content
        
        slide_num = len(self.prs.slides)
        print(f"Added slide {slide_num}: '{title}'")
        return slide_num
    
    def update_slide(self, slide_num, title=None, content=None):
        """Update an existing slide's title and/or content."""
        if slide_num < 1 or slide_num > len(self.prs.slides):
            print(f"Error: Slide {slide_num} does not exist")
            return False
        
        slide = self.prs.slides[slide_num - 1]
        
        # Update title
        if title is not None and slide.shapes.title:
            slide.shapes.title.text = title
            print(f"Updated slide {slide_num} title to: '{title}'")
        
        # Update content
        if content is not None:
            # Find text placeholders or shapes
            updated = False
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape != slide.shapes.title:
                    shape.text = content
                    updated = True
                    break
            
            if updated:
                print(f"Updated slide {slide_num} content")
            else:
                # Add new text box if no content placeholder found
                self._add_text_box(slide, content)
                print(f"Added content to slide {slide_num}")
        
        return True
    
    def _add_text_box(self, slide, text):
        """Add a text box to a slide."""
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(8)
        height = Inches(5)
        
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.text = text
        
        return textbox
    
    def delete_slide(self, slide_num):
        """Delete a slide by number."""
        if slide_num < 1 or slide_num > len(self.prs.slides):
            print(f"Error: Slide {slide_num} does not exist")
            return False
        
        # Get slide title for confirmation
        slide = self.prs.slides[slide_num - 1]
        title = self._get_slide_title(slide) or f"Slide {slide_num}"
        
        # Remove the slide
        slide_id = slide.slide_id
        self.prs.part.drop_rel(slide.part.partname)
        slide_rIds = [rel.rId for rel in self.prs.part.rels.values() 
                     if rel.target_part is slide.part]
        for rId in slide_rIds:
            del self.prs.part.rels[rId]
        
        # Remove from slides collection
        del self.prs.slides._sldIdLst[slide_num - 1]
        
        print(f"Deleted slide {slide_num}: '{title}'")
        return True
    
    def duplicate_slide(self, slide_num):
        """Duplicate an existing slide."""
        if slide_num < 1 or slide_num > len(self.prs.slides):
            print(f"Error: Slide {slide_num} does not exist")
            return False
        
        source_slide = self.prs.slides[slide_num - 1]
        
        # Get the layout of the source slide
        layout = source_slide.slide_layout
        new_slide = self.prs.slides.add_slide(layout)
        
        # Copy all shapes from source to new slide
        for shape in source_slide.shapes:
            if hasattr(shape, 'text'):
                # Copy text shapes
                new_shape = None
                if shape == source_slide.shapes.title:
                    if new_slide.shapes.title:
                        new_slide.shapes.title.text = shape.text + " (Copy)"
                else:
                    # Add as text box
                    self._add_text_box(new_slide, shape.text)
        
        new_slide_num = len(self.prs.slides)
        title = self._get_slide_title(source_slide) or f"Slide {slide_num}"
        print(f"Duplicated slide {slide_num} as slide {new_slide_num}: '{title} (Copy)'")
        return new_slide_num
    
    def extract_text(self, slide_num=None):
        """Extract text from specific slide or all slides."""
        if slide_num:
            if slide_num < 1 or slide_num > len(self.prs.slides):
                print(f"Error: Slide {slide_num} does not exist")
                return None
            slides_to_process = [self.prs.slides[slide_num - 1]]
            slide_numbers = [slide_num]
        else:
            slides_to_process = self.prs.slides
            slide_numbers = range(1, len(self.prs.slides) + 1)
        
        content = []
        filename = Path(self.pptx_path).stem
        content.append(f"# {filename}")
        content.append("")
        
        for slide, num in zip(slides_to_process, slide_numbers):
            content.append(f"## Slide {num}")
            content.append("")
            
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())
            
            if slide_text:
                content.extend(slide_text)
            else:
                content.append("(No text content)")
            
            content.append("")
        
        return "\n".join(content)

def main():
    parser = argparse.ArgumentParser(description="PowerPoint Presentation Manager")
    parser.add_argument("pptx_file", nargs="?", help="PowerPoint file to work with")
    parser.add_argument("--create", action="store_true", help="Create new presentation")
    parser.add_argument("--list", action="store_true", help="List all slides")
    parser.add_argument("--extract", metavar="SLIDE_NUM", type=int, nargs="?", 
                       const=0, help="Extract text from slide (or all slides)")
    
    # Slide operations
    parser.add_argument("--add", metavar=("TITLE", "CONTENT"), nargs=2,
                       help="Add new slide with title and content")
    parser.add_argument("--update", metavar=("SLIDE_NUM", "TITLE", "CONTENT"), nargs=3,
                       help="Update existing slide")
    parser.add_argument("--delete", metavar="SLIDE_NUM", type=int,
                       help="Delete slide by number")
    parser.add_argument("--duplicate", metavar="SLIDE_NUM", type=int,
                       help="Duplicate slide by number")
    
    # Output options
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--save-as", help="Save presentation with new name")
    
    args = parser.parse_args()
    
    if not args.pptx_file and not args.create:
        parser.print_help()
        sys.exit(1)
    
    # Initialize PowerPoint Manager
    try:
        ppt_mgr = PowerPointManager(args.pptx_file)
    except Exception as e:
        print(f"Error loading presentation: {e}")
        sys.exit(1)
    
    # Execute operations
    modified = False
    
    if args.list:
        ppt_mgr.list_slides()
    
    if args.extract is not None:
        slide_num = args.extract if args.extract > 0 else None
        content = ppt_mgr.extract_text(slide_num)
        if content:
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Extracted text saved to: {args.output}")
            else:
                print(content)
    
    if args.add:
        title, content = args.add
        ppt_mgr.add_slide(title, content)
        modified = True
    
    if args.update:
        slide_num, title, content = args.update
        ppt_mgr.update_slide(int(slide_num), title, content)
        modified = True
    
    if args.delete:
        ppt_mgr.delete_slide(args.delete)
        modified = True
    
    if args.duplicate:
        ppt_mgr.duplicate_slide(args.duplicate)
        modified = True
    
    # Save if modified
    if modified:
        if args.save_as:
            ppt_mgr.save(args.save_as)
        else:
            ppt_mgr.save()

if __name__ == "__main__":
    main()