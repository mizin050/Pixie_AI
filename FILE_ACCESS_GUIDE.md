# Pixie AI - File System Access Guide

## 🗂️ File System Capabilities

Pixie can now access, read, and analyze files and folders on your computer!

## 📝 How to Use

### Reading Files

Ask Pixie to read any text file:

- "Read the file C:\Users\username\Documents\notes.txt"
- "Show me what's in my config.json"
- "Open the README.md file"

### Listing Directories

Ask Pixie to show folder contents:

- "List files in C:\Users\username\Documents"
- "Show me what's in my Downloads folder"
- "What files are in the current directory?"

### Searching for Files

Ask Pixie to find files:

- "Search for .py files in my Documents"
- "Find all images in C:\Users\username\Pictures"
- "Look for files named 'config' in my project folder"

### Getting File Information

Ask Pixie about file details:

- "Get info about myfile.txt"
- "What's the size of document.pdf?"
- "When was this file last modified?"

## 🔒 Security

- **Allowed Paths**: By default, Pixie can access:
  - Your home directory (`~`)
  - The current working directory
- **File Size Limit**: Files larger than 10MB won't be read (to prevent memory issues)

- **Binary Files**: Binary files are detected and won't display garbled text

## 💡 Example Conversations

**User**: "Read my todo.txt file"
**Pixie**: _Reads and displays the file contents_

**User**: "What Python files are in my project?"
**Pixie**: _Lists all .py files found_

**User**: "Show me the contents of my Documents folder"
**Pixie**: _Lists all files and folders with sizes_

## 🛠️ Technical Details

### Commands Pixie Uses Internally:

- `READ_FILE: path` - Reads file contents
- `LIST_DIR: path` - Lists directory contents
- `SEARCH_FILES: path pattern` - Searches for files
- `FILE_INFO: path` - Gets file metadata

### Supported Operations:

- ✅ Read text files
- ✅ List directories (recursive optional)
- ✅ Search files by name pattern
- ✅ Get file information (size, dates, type)
- ✅ Handle binary files gracefully
- ✅ Security restrictions on paths

### File Types Supported:

- Text files (.txt, .md, .log, etc.)
- Code files (.py, .js, .html, .css, etc.)
- Config files (.json, .yaml, .ini, etc.)
- Binary files (detected and handled appropriately)

## 🚀 Advanced Usage

### Recursive Directory Listing

"List all files in my project folder recursively"

### Pattern Matching

"Find all JSON files in my config directory"

### Multiple Operations

"Read config.json and list the files in the same folder"

## ⚠️ Limitations

- Cannot write/modify files (read-only for safety)
- Cannot delete files or folders
- Cannot execute files
- Limited to allowed directories
- 10MB file size limit for reading

## 🔧 Customization

To change allowed paths, edit `file_tools.py`:

```python
fs_tools = FileSystemTools(allowed_paths=[
    "C:\\MyCustomPath",
    "D:\\AnotherPath"
])
```

---

**Enjoy exploring your files with Pixie! 🦊📁**
