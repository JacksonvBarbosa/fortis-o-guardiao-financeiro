# ollama_agent_pc_fraco.py

import requests
import json
from src.agent.system_prompt import SYSTEM_PROMPT_PC_FRACO

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "phi3"  # modelo leve e estável para notebook fraco


def perguntar_fortis_ollama(pergunta_usuario: str, contexto: str) -> str:
    """
    Versão otimizada para PC fraco.
    Prioriza estabilidade e tempo de resposta.
    """

    prompt = f"""
{SYSTEM_PROMPT_PC_FRACO}

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta_usuario}

Responda de forma objetiva e responsável.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": True,  # 🔑 evita timeout interno do Ollama
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 1024,
                    #"num_predict": 128,   # limite agressivo
                    #"num_batch": 64       # ESSENCIAL para CPU fraca
                }
            },
            stream=True,
            timeout=300
        )

        texto_final = ""

        for line in response.iter_lines():
            if not line:
                continue

            try:
                data = json.loads(line.decode("utf-8"))
                texto_final += data.get("response", "")
            except json.JSONDecodeError:
                continue

        if not texto_final.strip():
            return "⚠️ Não foi possível gerar uma resposta no momento. Tente novamente."

        return texto_final.strip()

    except requests.exceptions.Timeout:
        return "⏳ O Fortis está analisando com cuidado. Tente novamente em instantes."

    except Exception as e:
        return f"❌ Erro ao chamar o Fortis (modo PC fraco): {e}"
