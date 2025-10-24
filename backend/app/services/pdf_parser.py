import PyPDF2
import pdfplumber
from pathlib import Path


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.
    Tries pdfplumber first (better formatting), falls back to PyPDF2
    """
    try:
        # Try pdfplumber first (better text extraction)
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        if text.strip():
            return text.strip()
        
    except Exception as e:
        print(f"pdfplumber failed: {str(e)}, trying PyPDF2")
    
    try:
        # Fallback to PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")


def parse_docx(file_path: str) -> str:
    """
    Extract text from DOCX file (future implementation)
    """
    try:
        import docx
        doc = docx.Document(file_path)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except ImportError:
        raise Exception("python-docx not installed. Install it to parse DOCX files")
    except Exception as e:
        raise Exception(f"Failed to parse DOCX: {str(e)}")
