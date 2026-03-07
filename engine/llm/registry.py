DEFAULT_MODEL = "llama3:8b"

MODEL_REGISTRY = {
    "deepseek-coder:6.7b": {
        "type": "code",
        "priority": 1
    },
    "mixtral:8x7b": {
        "type": "analysis",
        "priority": 2
    },
    "llama3:8b": {
        "type": "general",
        "priority": 3
    },
  
}