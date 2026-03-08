import re

DEFAULT_MODEL = "llama3:8b"

MODEL_REGISTRY = {
    "deepseek-coder:6.7b": {
        "type": "code",
        "priority": 1
    },
    "qwen2.5-coder:7b": {
        "type": "code",
        "priority": 2
    },
    "mixtral:8x7b": {
        "type": "analysis",
        "priority": 3
    },
    "llama3:8b": {
        "type": "general",
        "priority": 4
    },
}

CATEGORY_PATTERNS = {
    "code": re.compile(r"traceback|exception|stack trace|\bdef\b|\bclass\b|\bimport\b|\bfunction\b|python|javascript|typescript"),
    "analysis": re.compile(r"error|failed|warning|log|docker|yaml|json|nginx|config|deployment|server")
}