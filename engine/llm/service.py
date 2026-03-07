import requests
from django.conf import settings
from requests.adapters import HTTPAdapter


class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.session = requests.Session()

        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)


    def generate(self, model: str, system_prompt: str, user_prompt: str):
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "system": system_prompt,
                    "prompt": user_prompt,
                    "stream": False
                },
                timeout=300
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