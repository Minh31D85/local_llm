from .registry import MODEL_REGISTRY, DEFAULT_MODEL, CATEGORY_PATTERNS
from .service import OllamaService


class LLMRouter:
    def __init__(self):
        self.service = OllamaService()


    def stream(self, system_prompt: str, prompt: str):
        model = self._auto_select_model(prompt)

        stream = self.service.generate(
            model=model,
            system_prompt=system_prompt,
            user_prompt=prompt
        )
        return model, stream


    def _auto_select_model(self, prompt: str):
        text = prompt.lower()
        category = "general"

        for name, pattern in CATEGORY_PATTERNS.items():
            if pattern.search(text):
                category = name
                break

        candidates = [
            (model, data)
            for model, data in MODEL_REGISTRY.items()
            if data["type"] == category
        ]
            
        if not candidates: 
            return DEFAULT_MODEL
   
        candidates.sort(key=lambda x: x[1]["priority"])
        selected_model = candidates[0][0]

        return selected_model
       
        