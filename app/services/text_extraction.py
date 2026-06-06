from pathlib import Path

from docx import Document
from pypdf import PdfReader

def extract_text(path: str|Path,content_type:str="")->str:
    resolved=Path(path)
    suffix = resolved.suffix.lowe()

    if suffix in {".txt",".md","markdown",".csv",".log"} or content_type.startswith("text/"):
        return resolved.read_text(encoding="utf-8",errors="ignore")
    
    if suffix ==".pdf" or content_type=="application/pdf":
        reader=PdfReader(str(resolved))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    
    if suffix == ".docx" or content_type.endswith("wordprocessingml.document"):
        document = Document(str(resolved))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    
    return resolved.read_text(encoding="utf-8",errors="ignore")
