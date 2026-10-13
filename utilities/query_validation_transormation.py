import re
from typing import Dict, List, Tuple

ALLOWED_QUERY_PATTERNS = re.compile(r"^[a-zA-Z0-9\s?@#\-_.,'""()]+$")
STOP_WORDS = {"the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "of"}
SYNONYMS = {
    "quick": "fast",
    "slow": "sluggish",
    "happy": "joyful",
    "sad": "unhappy",
    "buy": "purchase",
    "find": "search",
    "latest": "recent"
}

def validate_query(query: str) -> bool:
    """
    Validates the input query against allowed patterns and checks for stop words.
    Returns a tuple of (is_valid, issues).
    """
    
    if not query or len(query.strip()) < 3:
        raise ValueError("Query must be at least 3 characters long.")
    if not ALLOWED_QUERY_PATTERNS.match(query):
        raise ValueError("Query contains invalid characters.")
    return True

def transform_query(query: str) -> Dict[str, str]:
    """
    Transforms the input query by normalizing case, removing stop words, and replacing synonyms.
    """
    # Normalize case
    query = query.strip().lower()
    normalized_query = re.sub(r'\s+', ' ', query)  # Replace multiple spaces with a single space
    
    # Remove stop words
    words = normalized_query.split()
    filtered_words = [word for word in words if word not in STOP_WORDS]
    
    # Replace synonyms
    transformed_words = [SYNONYMS.get(word, word) for word in filtered_words]
    
    return {
        'original': query,
        'normalized': normalized_query,
        'transformed': ' '.join(transformed_words)
    }


def process_query(query: str) -> Dict[str, str]:
    """
    Validates and transforms the input query.
    Returns a dictionary with original, normalized, transformed, and signature.
    """
    validate_query(query)
    return transform_query(query)


