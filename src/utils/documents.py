"""Process different document types for AI analysis"""
import os
import base64

def read_text_file(file_path):
    """Read text-based files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return None

def read_pdf(file_path):
    """Read PDF files"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        return "[PDF support not installed. Run: pip install PyPDF2]"
    except Exception as e:
        return f"[Error reading PDF: {e}]"

def read_docx(file_path):
    """Read Word documents"""
    try:
        import docx
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except ImportError:
        return "[DOCX support not installed. Run: pip install python-docx]"
    except Exception as e:
        return f"[Error reading DOCX: {e}]"

def read_excel(file_path):
    """Read Excel files"""
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        return df.to_string()
    except ImportError:
        return "[Excel support not installed. Run: pip install pandas openpyxl]"
    except Exception as e:
        return f"[Error reading Excel: {e}]"

def process_document(file_path):
    """Process any document type and return its content"""
    ext = os.path.splitext(file_path)[1].lower()
    
    # Text files
    if ext in ['.txt', '.md', '.log', '.json', '.xml', '.csv', '.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml', '.ini', '.conf']:
        content = read_text_file(file_path)
        if content:
            return {
                'type': 'text',
                'content': content,
                'format': ext[1:]
            }
    
    # PDF
    elif ext == '.pdf':
        content = read_pdf(file_path)
        return {
            'type': 'document',
            'content': content,
            'format': 'pdf'
        }
    
    # Word
    elif ext in ['.docx', '.doc']:
        content = read_docx(file_path)
        return {
            'type': 'document',
            'content': content,
            'format': 'docx'
        }
    
    # Excel
    elif ext in ['.xlsx', '.xls']:
        content = read_excel(file_path)
        return {
            'type': 'spreadsheet',
            'content': content,
            'format': 'excel'
        }
    
    # Images
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico']:
        return {
            'type': 'image',
            'path': file_path,
            'format': ext[1:]
        }
    
    # Unknown
    else:
        return {
            'type': 'unknown',
            'content': f'[Unsupported file type: {ext}]',
            'format': ext[1:]
        }
