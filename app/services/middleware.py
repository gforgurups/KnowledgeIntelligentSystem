import re
from typing import Dict, List, Tuple
import logging

#Configre logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    A unified middleware guardrail class for LiteLLM.
    Scans and redacts multiple PII pattern categories from user payloads.
    """
    
    # Class-level dictionary containing raw regex patterns
    PII_PATTERNS = {
        "EMAIL":       r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "PHONE_IN":    r"(\+91[\-\s]?)?[6-9]\d{9}",                  # Indian mobile
        "PHONE_US":    r"(\+1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}",
        "SSN":         r"\b\d{3}-\d{2}-\d{4}\b",
        "AADHAAR":     r"\b\d{4}\s?\d{4}\s?\d{4}\b",                 # Indian Aadhaar
        "PAN":         r"\b[A-Z]{5}\d{4}[A-Z]\b",                    # Indian PAN
        "CREDIT_CARD": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
        "IP_ADDRESS":  r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|prior|above) (instructions?|prompts?|rules?)",
    r"disregard (the |all )?(previous|prior|earlier)",
    r"forget (everything|your instructions?|the rules?)",
    r"you are (now |a )?(DAN|jailbroken|unrestricted|unfiltered)",
    r"pretend (you are|to be) .{0,40}(no restrictions?|uncensored)",
    r"</?(system|user|assistant|im_start|im_end)>",
    r"new (instructions?|system prompt|rules?):",
    r"reveal your (system )?prompt",
    r"what (are|were) your (original )?instructions?",
    ]
    
    INJECTION_REGEX = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    # Keywords your assistant should refuse to discuss
    FORBIDDEN_TOPICS = [
        "weapon", "bomb", "explosive",
        "hack", "exploit", "malware",
        "drugs", "illegal substance",
        "self-harm", "suicide",
    ]

    def __init__(self):
        # Pre-compile the regex strings for optimal execution performance
        self.compiled_patterns = {
            label: re.compile(pattern) 
            for label, pattern in self.PII_PATTERNS.items()
        }
        

    def redact_pii(self, text: str) -> Tuple[str, List[Dict[str, int]]]:
        """
        Replace PII in text with placeholders. 
        Returns (clean_text, detected_list).
        """
        detected = []
        clean = text
        
        for label, pattern in self.compiled_patterns.items():
            matches = pattern.findall(clean)
            if matches:
                detected.append({"type": label, "count": len(matches)})
                clean = pattern.sub(f"<{label}_REDACTED>", clean)
                
        return clean, detected

    #PII input guardrail
    def pii_input_guardrail(self, kwargs: Dict) -> Dict:
        """
        LiteLLM pre-call hook: scrub PII from user messages.
        Modifies input payload in-place and logs detections.
        """
        messages = kwargs.get("messages", [])
        
        for msg in messages:
            if msg.get("role") == "user" and "content" in msg:
                clean, detected = self.redact_pii(msg["content"])
                if detected:
                    logger.warning(f"PII detected and redacted: {detected}")
                    msg["content"] = clean
                    
        return kwargs

    #Prompt injection guardrail
    def injection_guardrail(self, kwargs):
        messages = kwargs.get("messages", [])
        for msg in messages:
            if msg.get("role") == "user":
                content = msg["content"]
                for regex in self.INJECTION_REGEX:
                    if regex.search(content):
                        logger.warning(f"Prompt injection attempt detected: {content}")
                        raise GuardrailViolation("Blocked: prompt injection attempt")

    #Forbidden Topic guardrail
    def forbidden_topic_guardrail(self, kwargs):
        messages = kwargs.get("messages", [])
        for msg in messages:
            if msg.get("role") == "user":
                content_lower = msg["content"].lower()
                for keyword in self.FORBIDDEN_TOPICS:
                    if keyword in content_lower:
                        logger.warning(f"Forbidden topic detected: {keyword} in message: {msg['content']}")
                        raise GuardrailViolation(
                            f"This assistant doesn't discuss topics related to '{keyword}'."
                        )

class GuardrailViolation(Exception):
    """Raised when a guardrail blocks a request."""
    pass