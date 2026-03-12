import requests
import json
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
                    "stream": True,
                    "keep_alive": -1,
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "num_predict": 1000,
                        "num_thread": 3,
                        "num_ctx": 2048
                    }
                },
                stream=True,
                timeout=1000
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line.decode("utf-8"))
                
                except json.JSONDecodeError:
                    continue

                if "response" in data:
                    yield data["response"]

                if data.get("done"):
                    break
        
        except requests.exceptions.Timeout:
            return "LLM timeout error"
        
        except requests.exceptions.ConnectionError:
            return "LLM connection error"
        
        except Exception as e:
            return f"LLM error: {str(e)}"
        
        finally:
            if response is not None:
                response.close()