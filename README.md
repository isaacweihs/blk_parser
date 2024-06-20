# blk_parser
A python parser for .blk files commonly found in the game War Thunder.

# Features
- Parsing a .blk into a list of tuples. This allows it to store positions and paths to elements, as well as making it easy to access elements and their values using the provided functions.

- Reverse parsing allowing for the list of tuples to be reverted back into a valid .blk-formatted string.

# Instructions
Use the file as a Python module to parse .blk files into a Python Dictionary.
The function takes a string as input - ideally a .blk converted to .txt and then joined into a single string.

# Notes
I haven't tested parsing anything other than .blk files for custom user missions, meaning that I can't guarantee that it works correctly for .blk files not initiated by the War Thunder Mission Editor.
If you're looking to convert .blkx files, try making them into .json files first - they _seem_ to be the exact same format wise, and it has worked for me in other projects.

v2.0
