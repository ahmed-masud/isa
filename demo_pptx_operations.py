#!/usr/bin/env python3
"""
Demonstration of PowerPoint Manipulation Capabilities
This script showcases all the CRUD operations possible with PowerPoint presentations.
"""

import os
import sys
from tools.pptx_manager import PowerPointManager

def demo_pptx_operations():
    """Demonstrate all PowerPoint manipulation capabilities."""
    
    print("🎯 PowerPoint Manipulation Demo")
    print("=" * 50)
    
    # Create a new presentation
    print("\n1. Creating a new presentation...")
    ppt = PowerPointManager("demo_presentation.pptx")
    
    # Add slides with different content
    print("\n2. Adding slides...")
    ppt.add_slide("Welcome", "This is the introduction slide with some content.")
    ppt.add_slide("Key Features", 
                  "• Create new presentations\n• Add, update, delete slides\n• Extract text content\n• Duplicate slides")
    ppt.add_slide("Technical Details", 
                  "Built using python-pptx library\nSupports various slide layouts\nHandles text extraction efficiently")
    
    # List all slides
    print("\n3. Listing all slides...")
    ppt.list_slides()
    
    # Update a slide
    print("\n4. Updating slide 2...")
    ppt.update_slide(2, "Enhanced Features", 
                     "• Create/Read/Update/Delete slides\n• Text extraction for ISA contexts\n• Command-line interface\n• Programmatic API")
    
    # Duplicate a slide
    print("\n5. Duplicating slide 1...")
    ppt.duplicate_slide(1)
    
    # Extract text from specific slide
    print("\n6. Extracting text from slide 2...")
    extracted_text = ppt.extract_text(2)
    print("Extracted content:")
    print("-" * 30)
    print(extracted_text)
    print("-" * 30)
    
    # Save the presentation
    print("\n7. Saving presentation...")
    ppt.save()
    
    # Demonstrate loading existing presentation
    print("\n8. Loading existing presentation...")
    existing_ppt = PowerPointManager("demo_presentation.pptx")
    existing_ppt.list_slides()
    
    # Add another slide to existing presentation
    print("\n9. Adding slide to existing presentation...")
    existing_ppt.add_slide("Conclusion", "Demo completed successfully!")
    
    # Delete a slide
    print("\n10. Deleting slide 3...")
    existing_ppt.delete_slide(3)
    
    # Final save
    existing_ppt.save()
    
    # Extract all text for ISA context
    print("\n11. Extracting all text for ISA context...")
    all_text = existing_ppt.extract_text()
    
    # Save extracted text to markdown file
    output_file = "demo_presentation_extracted.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    
    print(f"✅ All text extracted to: {output_file}")
    print(f"💡 You can add to ISA with: isa ctx-add '{output_file}'")
    
    print("\n🎉 Demo completed! Files created:")
    print(f"   📄 demo_presentation.pptx")
    print(f"   📝 {output_file}")
    
    return "demo_presentation.pptx", output_file

def show_command_examples():
    """Show command-line usage examples."""
    print("\n📋 Command-Line Usage Examples:")
    print("=" * 50)
    
    examples = [
        ("Create new presentation", 
         "python tools/pptx_manager.py --create new_deck.pptx"),
        
        ("List slides in existing presentation", 
         "python tools/pptx_manager.py existing.pptx --list"),
        
        ("Add a new slide", 
         "python tools/pptx_manager.py existing.pptx --add 'New Topic' 'Slide content here'"),
        
        ("Update existing slide", 
         "python tools/pptx_manager.py existing.pptx --update 2 'Updated Title' 'Updated content'"),
        
        ("Delete a slide", 
         "python tools/pptx_manager.py existing.pptx --delete 3"),
        
        ("Duplicate a slide", 
         "python tools/pptx_manager.py existing.pptx --duplicate 1"),
        
        ("Extract text from all slides", 
         "python tools/pptx_manager.py existing.pptx --extract"),
        
        ("Extract text from specific slide", 
         "python tools/pptx_manager.py existing.pptx --extract 2"),
        
        ("Extract text to file", 
         "python tools/pptx_manager.py existing.pptx --extract --output extracted.md"),
        
        ("Save with new name", 
         "python tools/pptx_manager.py existing.pptx --add 'New' 'Content' --save-as new_version.pptx")
    ]
    
    for i, (description, command) in enumerate(examples, 1):
        print(f"\n{i:2}. {description}:")
        print(f"    {command}")
    
    print(f"\n💡 Integration with ISA:")
    print(f"    # Extract PowerPoint content for ISA context")
    print(f"    python tools/pptx_manager.py presentation.pptx --extract --output content.md")
    print(f"    isa ctx-add content.md")

def show_python_api_examples():
    """Show Python API usage examples."""
    print("\n🐍 Python API Usage Examples:")
    print("=" * 50)
    
    code_examples = '''
# Import the PowerPoint manager
from tools.pptx_manager import PowerPointManager

# Create or load a presentation
ppt = PowerPointManager("my_presentation.pptx")  # Load existing
ppt = PowerPointManager()  # Create new

# Basic operations
ppt.list_slides()                    # Show all slides
ppt.add_slide("Title", "Content")    # Add new slide
ppt.update_slide(1, "New Title")     # Update slide title
ppt.delete_slide(2)                  # Delete slide 2
ppt.duplicate_slide(1)               # Copy slide 1

# Text extraction
text = ppt.extract_text()            # Extract all text
text = ppt.extract_text(3)           # Extract from slide 3

# Save operations  
ppt.save()                           # Save to original file
ppt.save("new_name.pptx")            # Save with new name

# Advanced usage - batch operations
slides_data = [
    ("Introduction", "Welcome to our presentation"),
    ("Problem Statement", "Current challenges we face"),
    ("Solution", "Our proposed approach"),
    ("Implementation", "Technical details and roadmap"),
    ("Conclusion", "Summary and next steps")
]

for title, content in slides_data:
    ppt.add_slide(title, content)

# Extract for ISA context
extracted = ppt.extract_text()
with open("presentation_context.md", "w") as f:
    f.write(extracted)
'''
    
    print(code_examples)

def main():
    """Main demo function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--examples-only":
        show_command_examples()
        show_python_api_examples()
        return
    
    # Run the full demo
    try:
        pptx_file, md_file = demo_pptx_operations()
        show_command_examples()
        show_python_api_examples()
        
        print("\n" + "=" * 50)
        print("🎯 Key Capabilities Demonstrated:")
        print("✅ Create new PowerPoint presentations")  
        print("✅ Load and modify existing presentations")
        print("✅ Add slides with title and content")
        print("✅ Update existing slide content")
        print("✅ Delete unwanted slides")
        print("✅ Duplicate slides for templating")
        print("✅ Extract text for ISA contexts")
        print("✅ Command-line and Python API interfaces")
        print("✅ ISA integration workflows")
        
        # Clean up demo files
        cleanup = input("\n🗑️  Delete demo files? (y/N): ").lower()
        if cleanup == 'y':
            if os.path.exists(pptx_file):
                os.remove(pptx_file)
                print(f"Deleted: {pptx_file}")
            if os.path.exists(md_file):
                os.remove(md_file)
                print(f"Deleted: {md_file}")
    
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install python-pptx")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()