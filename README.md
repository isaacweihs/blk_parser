# blk_parser
A python parser for .blk files commonly found in the game War Thunder.

# Notes
I haven't tested parsing anything other than .blk files for custom user missions, meaning that I can't guarantee that it works correctly for .blk files not initiated by the War Thunder Mission Editor.

17/6/2024:
  
I have expanded the parser and fixed a lot of issues that were less apparent at first. Will publish on the 18th, as soon as possible.
  
New changes will include:
    
- Will now parse .blk into a nested tuple to store positions and paths to elements.
    
- A function to access individual parts within the nested tuple using simple pathing
    
- Reverse parsing allowing for the tuple to be reverted back into a valid .blk format
    
- Tons of fixes for stuff that was being incorrectly parsed (matrixes, recursively nested nodes, duplicate nodes, etc.)

# Instructions
Use the file as a Python module to parse .blk files into a Python Dictionary.
The function takes a string as input - ideally a .blk converted to .txt and then joined into a single string.

v1.0
