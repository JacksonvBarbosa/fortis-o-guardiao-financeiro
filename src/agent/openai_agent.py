import os
from dotenv import load_dotenv
from openai import OpenAI

from src.agent.system_prompt import SYSTEM_PROMPT_02_FLUIDEZ

# Carrega variáveis do .env
load_dotenv()

# 🔑 Lê exatamente a variável que você criou
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY não encontrada no .env")

# Inicializa cliente OpenAI corretamente
client = OpenAI(api_key=OPENAI_API_KEY)


def perguntar_fortis_openai(pergunta_usuario: str, contexto: str) -> str:
    """
    Envia pergunta + contexto ao agente Fortis usando OpenAI
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_02_FLUIDEZ},
                {"role": "system", "content": contexto},
                {"role": "user", "content": pergunta_usuario},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erro ao consultar OpenAI: {str(e)}"
