import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Retorna o diretório base do projeto.

    - Quando rodando como script: retorna o diretório do arquivo.
    - Quando empacotado pelo PyInstaller (onefile): retorna a pasta onde o executável está.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent
