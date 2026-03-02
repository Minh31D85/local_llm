import requests
from django.conf import settings

class OllamaService:
    def generate(self, prompt: str, language: str):
        system_prompt = (
            f"You are a senior software engineer. "
            f"Return only production ready {language} code. "
            f"No explanations."
            f"No markdown."
            f"No backticks"
        )

        try:
            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": system_prompt + "\n\n" + prompt,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            data = response.json()


            if "response" not in data:
                raise ValueError("Invalid LLM response")
            
            cleaned = self._clean_output(data["response"])
            return cleaned
        
        except requests.exceptions.Timeout:
            return "LLM timeout error"
        
        except requests.exceptions.ConnectionError:
            return "LLM connection error"
            
        except Exception as e:
            return f"LLM connection error: {str(e)}"


    def _clean_output(self, text: str) -> str:
        """
        Entfernt Markdown und Backticks
        """
        text = text.strip()

        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        
        return text.strip()