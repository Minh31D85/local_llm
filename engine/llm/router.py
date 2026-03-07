import re
from .registry import MODEL_REGISTRY, DEFAULT_MODEL
from .service import OllamaService


class LLMRouter:
    def __init__(self):
        self.service = OllamaService()

    def generate(self, system_prompt: str, prompt: str):
        model = self._auto_select_model(prompt)

        response =  self.service.generate(
            model=model,
            system_prompt=system_prompt,
            user_prompt=prompt
        )
        
        return model, response
    
    def _auto_select_model(self, prompt: str):
        text = prompt.lower()

        category = "general"

        if re.search(r"traceback|execption|stack trace", text):
            category = "code"

        elif re.search(r"\bdef\b|\bclass\b|\bimport\b|\bfunction\b", text):
            category = "code"
        
        elif re.search(r"error|failed|warning|log", text):
            category = "analysis"

        elif re.search(r"docker|yaml|json|nginx|config", text):
            category = "analysis"

        for model, data in MODEL_REGISTRY.items():
            if data["type"] == category:
                return model
   
        return DEFAULT_MODEL
       
        