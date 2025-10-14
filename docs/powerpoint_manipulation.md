# PowerPoint Manipulation with ISA

## Overview

Based on the template from `~/projects/gpt-fixes/extract_pptx_for_isa.py`, we've created a comprehensive PowerPoint manipulation system that provides full CRUD (Create, Read, Update, Delete) operations for PowerPoint presentations.

## Key Components

### 1. PowerPoint Manager (`tools/pptx_manager.py`)

A comprehensive Python class and CLI tool for manipulating PowerPoint presentations:

**Core Capabilities:**
- ✅ **Create** new presentations from scratch
- ✅ **Read** and load existing presentations  
- ✅ **Update** slide titles, content, and properties
- ✅ **Delete** unwanted slides
- ✅ **Duplicate** slides for templating
- ✅ **Extract** text content for ISA contexts
- ✅ **List** all slides with summaries
- ✅ **Save** presentations with version control

### 2. Library Dependencies

The system uses the `python-pptx` library (version 1.0.2+):

```bash
pip install python-pptx
```

**Key library features utilized:**
- `Presentation()` - Create/load presentations
- `add_slide()` - Add new slides with layouts
- `slide.shapes` - Access and modify slide content
- `slide.placeholders` - Work with slide templates
- Text extraction and formatting
- Slide manipulation and deletion

## Usage Examples

### Command Line Interface

```bash
# Create new presentation
python tools/pptx_manager.py --create presentation.pptx

# List all slides
python tools/pptx_manager.py presentation.pptx --list

# Add a new slide
python tools/pptx_manager.py presentation.pptx --add "New Topic" "Content here"

# Update existing slide
python tools/pptx_manager.py presentation.pptx --update 2 "Updated Title" "New content"

# Delete a slide
python tools/pptx_manager.py presentation.pptx --delete 3

# Duplicate a slide
python tools/pptx_manager.py presentation.pptx --duplicate 1

# Extract text from all slides
python tools/pptx_manager.py presentation.pptx --extract --output content.md

# Extract text from specific slide
python tools/pptx_manager.py presentation.pptx --extract 2
```

### Python API

```python
from tools.pptx_manager import PowerPointManager

# Initialize
ppt = PowerPointManager("presentation.pptx")  # Load existing
ppt = PowerPointManager()                     # Create new

# Basic operations
ppt.add_slide("Title", "Content")
ppt.update_slide(1, "New Title", "New Content")
ppt.delete_slide(2)
ppt.duplicate_slide(1)

# Information and extraction
ppt.list_slides()
text = ppt.extract_text()      # All slides
text = ppt.extract_text(3)     # Specific slide

# Save operations
ppt.save()                     # Save to original
ppt.save("new_name.pptx")      # Save as new file
```

## Integration with ISA

### Workflow for Adding PowerPoint Content to ISA

1. **Extract text content:**
   ```bash
   python tools/pptx_manager.py presentation.pptx --extract --output extracted.md
   ```

2. **Add to ISA context:**
   ```bash
   isa ctx-add extracted.md
   ```

3. **Use semantic search:**
   ```bash
   isa ctx-search "presentation topic"
   computer ask "summarize the presentation"
   ```

### Automated ISA Integration

The extraction process creates ISA-compatible markdown:

```markdown
# presentation_name

## Slide 1
Title: Introduction
Content goes here...

## Slide 2
Title: Key Points
• Bullet point 1
• Bullet point 2
```

## Advanced Features

### 1. Slide Layout Support

The system supports different PowerPoint slide layouts:
- **Layout 0**: Title slide
- **Layout 1**: Title + Content (default)
- **Layout 2**: Section header
- **Layout 3**: Two content areas
- **Layout 4**: Comparison
- And more...

```python
# Use specific layout when adding slides
ppt.add_slide("Title", "Content", layout_index=0)  # Title slide
```

### 2. Text Box Management

When slides don't have content placeholders, the system automatically creates text boxes:

```python
def _add_text_box(self, slide, text):
    """Add a text box to a slide."""
    left = Inches(1)
    top = Inches(1.5) 
    width = Inches(8)
    height = Inches(5)
    
    textbox = slide.shapes.add_textbox(left, top, width, height)
    textbox.text_frame.text = text
```

### 3. Smart Content Detection

The system intelligently detects and handles:
- Title shapes vs. content shapes
- Text placeholders vs. manual text boxes  
- Empty slides vs. content-rich slides
- Duplicate content prevention

### 4. Batch Operations

Support for bulk slide operations:

```python
# Batch slide creation
slides_data = [
    ("Introduction", "Welcome message"),
    ("Problem", "Current challenges"), 
    ("Solution", "Our approach"),
    ("Implementation", "Technical details"),
    ("Conclusion", "Next steps")
]

for title, content in slides_data:
    ppt.add_slide(title, content)
```

## Error Handling

The system includes comprehensive error handling:

- **File not found**: Graceful handling of missing files
- **Invalid slide numbers**: Bounds checking
- **Corrupted presentations**: Exception handling
- **Missing dependencies**: Clear error messages
- **Permission issues**: File access validation

## Performance Considerations

- **Memory efficient**: Loads presentations on-demand
- **Incremental saves**: Only saves when modified
- **Text extraction**: Optimized for large presentations
- **Batch operations**: Minimize file I/O operations

## ISA-First Integration

Following ISA-first principles:

1. **Local processing**: All operations happen locally
2. **Context integration**: Seamless ISA context addition
3. **Semantic search**: Extracted content is searchable
4. **Token conservation**: Local processing reduces API calls

## File Structure

```
/Users/masud/projects/isa/
├── tools/
│   └── pptx_manager.py           # Main PowerPoint manager
├── demo_pptx_operations.py       # Demonstration script
├── docs/
│   └── powerpoint_manipulation.md # This documentation
└── extract_pptx_for_isa.py      # Original extraction script
```

## Testing and Validation

The `demo_pptx_operations.py` script provides:
- **Live demonstration** of all capabilities
- **Example code** for integration
- **Error testing** scenarios
- **Performance benchmarks**

Run the demo:
```bash
python demo_pptx_operations.py
```

## Future Enhancements

Potential additions to the PowerPoint manipulation system:

1. **Image handling**: Extract and process embedded images
2. **Chart data**: Access and modify chart data
3. **Animation support**: Handle slide transitions and animations  
4. **Template management**: Create and apply custom templates
5. **Collaboration features**: Track changes and comments
6. **Advanced formatting**: Font, color, and style management
7. **Export options**: Convert to other formats (PDF, HTML, etc.)

## Dependencies and Requirements

- **Python 3.7+**
- **python-pptx 1.0.2+**
- **pathlib** (standard library)
- **argparse** (standard library)
- **os/sys** (standard libraries)

## Troubleshooting

Common issues and solutions:

**ImportError: No module named 'pptx'**
```bash
pip install python-pptx
```

**Permission denied when saving**
- Ensure the presentation isn't open in PowerPoint
- Check file permissions
- Use `--save-as` to save with a different name

**Slide deletion errors**
- Verify slide number exists
- Some presentations may have protected slides
- Try duplicating and modifying instead of deleting

**Text extraction issues**  
- Some slides may have complex layouts
- Images and charts won't be extracted as text
- Consider using OCR for image-based content

---

*This documentation demonstrates comprehensive PowerPoint manipulation capabilities based on the template from `~/projects/gpt-fixes/extract_pptx_for_isa.py`, extended with full CRUD operations and ISA integration.*