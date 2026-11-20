"""
EduPath AI - Text Cleaning and Normalization
Cleans extracted document text before chunking and embedding.
"""

import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Normalize text encoding, strip excessive whitespace, and remove noisy formatting artifacts.
    """
    if not text:
        return ""
        
    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)
    
    # Replace non-breaking spaces and unusual whitespace
    text = text.replace("\xa0", " ").replace("\u200b", "")
    
    # Remove control characters except newline and tab
    text = "".join(ch for ch in text if ch in ("\n", "\t") or (ch >= " " and ord(ch) < 65534))
    
    # Replace consecutive spaces/tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)
    
    # Replace 3 or more consecutive newlines with 2 newlines (paragraph boundary)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Strip leading/trailing line whitespace
    lines = [line.strip() for line in text.split("\n")]
    
    return "\n".join(lines).strip()
