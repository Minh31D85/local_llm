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


    def _detect_category(self, prompt: str):
        text = prompt.lower()
        scores = {k: 0 for k in CATEGORY_PATTERNS}

        for name, pattern in CATEGORY_PATTERNS.items():
            matches = pattern.findall(text)
            scores[name] += len(matches)

        if not any(scores.values()):
            return "general"
        
        return max(scores, key=scores.get)


    def _estimate_size(self, prompt: str):
        tokens = len(prompt.split())
        if tokens < 150:
            return "small"
        
        if tokens < 800:
            return "medium"
        
        return "large"


    def _score_model(self, model_data, size):
        score = model_data["priority"]

        if size == "small" and model_data["speed"] == "fast":
            score -= 1

        if size == "large" and model_data["context"] > 16000:
            score -= 1
        
        return score


    def _auto_select_model(self, prompt: str):
        category = self._detect_category(prompt)
        size = self._estimate_size(prompt)

        candidates = [
            (model, data)
            for model, data in MODEL_REGISTRY.items()
            if data["type"] == category
        ]

        if not candidates:
            return DEFAULT_MODEL
        
        best_model = min(
            candidates,
            key=lambda x: self._score_model(x[1], size)
        )

        return best_model[0]