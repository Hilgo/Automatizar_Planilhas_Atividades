from pathlib import Path

from common import get_base_dir
from preprocessa_relatorio_unico import processa_relatorio_unico

BASE_DIR = get_base_dir()
RAW_DIR = BASE_DIR / "csv_brutos"
OUT_DIR = BASE_DIR / "csv_tratados"

RAW_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)


def processa_arquivo(arquivo: Path):
    nome_base = arquivo.stem  # ex: 2DS_Logica
    saida = OUT_DIR / f"{nome_base}_tratado.csv"

    print(f"\n=== {arquivo.name} ===")
    print("Processando relatório único...")
    processa_relatorio_unico(arquivo, saida)
    print("OK")

def main():
    arquivos = sorted(RAW_DIR.glob("*.csv"))
    if not arquivos:
        print("Atenção - Nenhum CSV encontrado em csv_brutos/.")
        return

    for arq in arquivos:
        processa_arquivo(arq)

    print("\n Ok Pipeline concluída.")
    print(f"Arquivos tratados em: {OUT_DIR}")

if __name__ == "__main__":
    main()
