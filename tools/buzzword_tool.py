import re
from typing import List, Tuple
from config import PROHIBITED_BUZZWORDS

def check_and_clean_buzzwords(text: str) -> Tuple[str, List[str]]:
    """
    Checks text for prohibited marketing buzzwords and dash punctuation.
    Returns cleaned text and a list of detected/removed words.
    """
    detected = []
    cleaned_text = text
    
    # Check for prohibited buzzwords (case-insensitive)
    for word in PROHIBITED_BUZZWORDS:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        if pattern.search(cleaned_text):
            detected.append(word)
            # Remove or replace prohibited buzzword
            cleaned_text = pattern.sub("", cleaned_text)
            
    # Clean up double dashes or em-dashes
    cleaned_text = re.sub(r'—|--', ',', cleaned_text)
    
    # Clean extra whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text, detected
