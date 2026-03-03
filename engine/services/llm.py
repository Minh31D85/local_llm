import requests
from django.conf import settings

class OllamaService:
    def generate(self, system_prompt: str, user_prompt: str):
        try:
            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "system": system_prompt,
                    "prompt": user_prompt,
                    "stream": False
                },
                timeout=120
            )

            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                raise ValueError ("Invalid LLM response")
            
            return self._clean_output(data["response"])
        
        except requests.exceptions.Timeout:
            return "LLM timeout error"
        
        except requests.exceptions.ConnectionError:
            return "LLM connection error"
        
        except Exception as e:
            return f"LLM error: {str(e)}"
        
    
    def _clean_output(self, text: str) -> str:
        text = text.strip()

        if text.startswith("```"):
            lines = text.split("\n")[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
                text = "\n".join(lines)

        return text.strip()