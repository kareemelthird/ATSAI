import PyPDF2
import pdfplumber
from pathlib import Path


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.
    Tries pdfplumber first (better formatting), falls back to PyPDF2
    Handles various PDF issues gracefully
    """
    # Check if file exists and is readable
    if not Path(file_path).exists():
        raise Exception(f"File not found: {file_path}")
    
    if Path(file_path).stat().st_size == 0:
        raise Exception("PDF file is empty")
    
    text = ""
    
    try:
        # Try pdfplumber first (better text extraction)
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise Exception("PDF contains no pages")
            
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                except Exception as page_error:
                    print(f"Error extracting text from page {page_num + 1}: {page_error}")
                    continue
        
        if text.strip():
            return text.strip()
        else:
            print("pdfplumber extracted no text, trying PyPDF2...")
        
    except Exception as e:
        print(f"pdfplumber failed: {str(e)}, trying PyPDF2")
    
    try:
        # Fallback to PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise Exception("PDF is password-protected and cannot be processed")
            
            if len(pdf_reader.pages) == 0:
                raise Exception("PDF contains no pages")
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                except Exception as page_error:
                    print(f"Error extracting text from page {page_num + 1} with PyPDF2: {page_error}")
                    continue
        
        if text.strip():
            return text.strip()
        else:
            raise Exception("PDF appears to contain no extractable text (may be image-based or scanned)")
        
    except Exception as e:
        # Provide more specific error messages
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            raise Exception("PDF is password-protected. Please provide an unprotected version.")
        elif "damaged" in error_msg or "corrupted" in error_msg or "invalid" in error_msg:
            raise Exception("PDF file appears to be corrupted or invalid.")
        elif "no text" in error_msg or "image" in error_msg:
            raise Exception("PDF contains no extractable text. It may be an image-based or scanned document.")
        else:
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
