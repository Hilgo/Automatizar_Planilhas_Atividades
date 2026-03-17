import pandas as pd
from pathlib import Path
import os
import sys

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
TRATADOS_DIR = BASE_DIR / "csv_tratados"
Saida_DIR = BASE_DIR / "pendencias_detalhadas"
Saida_DIR.mkdir(exist_ok=True)

def parse_col_name(col: str) -> (str, int, str):
    """
    Retorna: (disciplina, semana, tipo)
    - Atividade_Semana_3 -> (Logica, 3, "registro")
    - Semana_3_Quiz_1   -> (Logica, 3, "quiz_1")
    """
    # Extraia disciplina do arquivo (assumindo 2DS_Logica, 2DS_Redes, etc.)
    # disciplina vem do nome do arquivo
    return None, None, None  # placeholder

def lista_pendencias(turma_prefixo: str, ate_semana: int = None):
    arquivos = sorted(TRATADOS_DIR.glob(f"{turma_prefixo}*_tratado.csv"))
    if not arquivos:
        print(f"Nenhum arquivo tratado para {turma_prefixo}")
        return

    detalhes = []

    for arq in arquivos:
        df = pd.read_csv(arq, sep=';')
        nome_arquivo = arq.stem
        disciplina = nome_arquivo.replace("_tratado", "").split("_")[-1]  # Logica, Redes, etc.

        for col in df.columns:
            if col in ["Nome", "Email"]:
                continue
            if not (col.startswith("Atividade_Semana_") or col.startswith("Semana_")):
                continue

            try:
                semana = None
                if col.startswith("Atividade_Semana_"):
                    semana = int(col.replace("Atividade_Semana_", ""))
                    tipo = "registro"
                elif col.startswith("Semana_"):
                    partes = col.split("_")
                    if len(partes) >= 3 and "Quiz" in col:
                        semana = int(partes[1])
                        tipo = f"quiz_{partes[3] if len(partes) > 3 else '1'}"
            except Exception as e:
                print(f"Erro na coluna {col}: {e}")
                continue

            if ate_semana is not None and semana > ate_semana:
                continue

            for _, row in df.iterrows():
                valor = str(row[col])
                if valor.strip().lower() == "não":
                    nome = row["Nome"]
                    email = row.get("Email", "")
                    detalhes.append({
                        "Nome": nome,
                        "Email": email,
                        "Disciplina": disciplina,
                        "Semana": semana,
                        "Tipo": tipo
                    })

    if not detalhes:
        print(f"Nenhuma pendência encontrada para {turma_prefixo}")
        return

    df = pd.DataFrame(detalhes)
    df.sort_values(["Nome", "Disciplina", "Semana", "Tipo"], inplace=True)

    saida = Saida_DIR / f"pendencias_detalhadas_{turma_prefixo}.csv"
    df.to_csv(saida, index=False, encoding='utf-8-sig', sep=';')
    print(f"✅ Pendências detalhadas geradas em: {saida}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python lista_pendencias_detalhada.py 2DS")
        print("  python lista_pendencias_detalhada.py 2DS 4")
        sys.exit(1)

    turma = sys.argv[1]
    ate_semana = int(sys.argv[2]) if len(sys.argv) >= 3 else None

    lista_pendencias(turma, ate_semana)
