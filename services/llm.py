import requests
from django.conf import settings

class OllamaService:
    def generate(self, prompt: str, language: str):
        system_prompt = (
            f"You are a senior software engineer. "
            f"Return only production ready {language} code. "
            f"No explanations."
        )

        response = requests.post(
            f"{settings.OLLAMA}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": system_prompt + "\n\n" + prompt,
                "stream": False
            }
        )
        return response.json()["response"]