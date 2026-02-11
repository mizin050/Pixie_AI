import os
import json
from pathlib import Path

class FileSystemTools:
    """Tools for file system access and manipulation"""
    
    def __init__(self, allowed_paths=None):
        """
        Initialize with optional allowed paths for security
        If None, allows access to entire system (use with caution)
        """
        self.allowed_paths = allowed_paths or []
    
    def is_path_allowed(self, path):
        """Check if path is within allowed directories"""
        if not self.allowed_paths:
            return True  # No restrictions
        
        abs_path = os.path.abspath(path)
        for allowed in self.allowed_paths:
            if abs_path.startswith(os.path.abspath(allowed)):
                return True
        return False
    
    def read_file(self, file_path, max_size_mb=10):
        """Read and return file contents"""
        try:
            if not self.is_path_allowed(file_path):
                return {"error": "Access denied: Path not in allowed directories"}
            
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > max_size_mb * 1024 * 1024:
                return {"error": f"File too large: {file_size / (1024*1024):.2f}MB (max {max_size_mb}MB)"}
            
            # Try to read as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "success": True,
                    "path": file_path,
                    "content": content,
                    "size": file_size,
                    "type": "text"
                }
            except UnicodeDecodeError:
                # Binary file
                return {
                    "success": True,
                    "path": file_path,
                    "content": "[Binary file - cannot display as text]",
                    "size": file_size,
                    "type": "binary"
                }
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}
    
    def list_directory(self, dir_path, recursive=False, max_depth=3):
        """List contents of a directory"""
        try:
            if not self.is_path_allowed(dir_path):
                return {"error": "Access denied: Path not in allowed directories"}
            
            if not os.path.exists(dir_path):
                return {"error": f"Directory not found: {dir_path}"}
            
            if not os.path.isdir(dir_path):
                return {"error": f"Not a directory: {dir_path}"}
            
            items = []
            
            if recursive:
                for root, dirs, files in os.walk(dir_path):
                    depth = root[len(dir_path):].count(os.sep)
                    if depth >= max_depth:
                        dirs.clear()
                        continue
                    
                    for file in files:
                        full_path = os.path.join(root, file)
                        items.append({
                            "name": file,
                            "path": full_path,
                            "type": "file",
                            "size": os.path.getsize(full_path)
                        })
                    
                    for dir_name in dirs:
                        full_path = os.path.join(root, dir_name)
                        items.append({
                            "name": dir_name,
                            "path": full_path,
                            "type": "directory"
                        })
            else:
                for item in os.listdir(dir_path):
                    full_path = os.path.join(dir_path, item)
                    item_info = {
                        "name": item,
                        "path": full_path,
                        "type": "directory" if os.path.isdir(full_path) else "file"
                    }
                    if item_info["type"] == "file":
                        item_info["size"] = os.path.getsize(full_path)
                    items.append(item_info)
            
            return {
                "success": True,
                "path": dir_path,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"error": f"Error listing directory: {str(e)}"}
    
    def search_files(self, search_path, pattern, max_results=50):
        """Search for files matching a pattern"""
        try:
            if not self.is_path_allowed(search_path):
                return {"error": "Access denied: Path not in allowed directories"}
            
            results = []
            pattern_lower = pattern.lower()
            
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if pattern_lower in file.lower():
                        full_path = os.path.join(root, file)
                        results.append({
                            "name": file,
                            "path": full_path,
                            "size": os.path.getsize(full_path)
                        })
                        
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
            
            return {
                "success": True,
                "pattern": pattern,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": f"Error searching files: {str(e)}"}
    
    def get_file_info(self, file_path):
        """Get detailed information about a file"""
        try:
            if not self.is_path_allowed(file_path):
                return {"error": "Access denied: Path not in allowed directories"}
            
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "extension": os.path.splitext(file_path)[1]
            }
        except Exception as e:
            return {"error": f"Error getting file info: {str(e)}"}
    
    def write_file(self, file_path, content):
        """Write content to a file"""
        try:
            if not self.is_path_allowed(file_path):
                return {"error": "Access denied: Path not in allowed directories"}
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": file_path,
                "message": "File written successfully"
            }
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}
    
    def create_directory(self, dir_path):
        """Create a new directory"""
        try:
            if not self.is_path_allowed(dir_path):
                return {"error": "Access denied: Path not in allowed directories"}
            
            os.makedirs(dir_path, exist_ok=True)
            
            return {
                "success": True,
                "path": dir_path,
                "message": "Directory created successfully"
            }
        except Exception as e:
            return {"error": f"Error creating directory: {str(e)}"}

# Global instance with common allowed paths
fs_tools = FileSystemTools(allowed_paths=[
    os.path.expanduser("~"),  # User home directory
    os.getcwd(),  # Current working directory
])
