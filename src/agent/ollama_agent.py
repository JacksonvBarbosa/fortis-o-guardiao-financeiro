# Libs
import requests
from src.agent.system_prompt import SYSTEM_PROMPT, SYSTEM_PROMPT_01

OLLAMA_URL = "http://localhost:11434/api/generate"
#MODELO = "mistral:7b-instruct"  # modelo correto e confiável
MODELO = "mistral:7b"  # modelo correto e confiável


def perguntar_fortis_ollama(pergunta_usuario: str, contexto: str) -> str:
    prompt = f"""
{SYSTEM_PROMPT_01}

CONTEXTO DO CLIENTE:
{contexto}

PERGUNTA DO USUÁRIO:
{pergunta_usuario}

Responda de forma clara, responsável e didática.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 4096
                }
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        # 🔑 Campo correto do generate
        return data.get("response", "").strip()

    except requests.exceptions.Timeout:
        return "⏳ O Fortis está analisando com cuidado. Tente novamente em instantes."

    except Exception as e:
        return f"❌ Erro ao chamar o Fortis (Ollama): {e}"
