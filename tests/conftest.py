"""
Config compartilhada dos testes.

REGRA DE OURO: nenhum teste pode tocar a rede / OpenAI. Tudo que é LLM é
mockado via monkeypatch. Não precisa de OPENAI_API_KEY pra rodar `pytest`.

Garante que a raiz do projeto está no sys.path pra `import src...` e `import app`
funcionarem rodando `pytest` da raiz.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
