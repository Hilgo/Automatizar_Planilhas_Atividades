import sys
from pathlib import Path

import pandas as pd


def limpa_status(valor):
    if pd.isna(valor):
        return "Não concluído"
    s = str(valor).strip().lower()
    if "não concluído" in s or "nao concluido" in s:
        return "Não concluído"
    if "concluído" in s or "concluido" in s:
        return "Concluído"
    return "Não concluído"


def processa_relatorio_unico(entrada, saida, semanas_sem_registro=None):
    """
    Processa um CSV bruto para um CSV tratado.

    semanas_sem_registro: lista de inteiros indicando quais semanas NÃO possuem
    Registro da Aula no CSV (ex: [5] para Mobile onde a semana 5 está faltando).
    Se None ou lista vazia, o script detecta automaticamente (comportamento anterior).
    """
    if semanas_sem_registro is None:
        semanas_sem_registro = []
        print("Sem registros faltantes declarados. O script tentará detectar automaticamente com base nos dados.")

    try:
        df = pd.read_csv(entrada, encoding="utf-16-le", sep=None, engine="python")
    except UnicodeDecodeError:
        df = pd.read_csv(entrada, encoding="utf-8-sig", sep=None, engine="python")

    df = df.rename(columns={df.columns[0]: "Nome"})

    cols_email = [
        col
        for col in df.columns
        if "e-mail" in str(col).lower() or "email" in str(col).lower()
    ]
    col_email = cols_email[0] if cols_email else None

    # Identificar colunas de status (excluindo Material da Aula)
    status_cols = []
    for col in df.columns:
        col_str = str(col)
        if "Material da Aula" in col_str:
            continue
        unique = df[col].dropna().astype(str).unique()
        if any("conclu" in v.lower() for v in unique):
            status_cols.append(col)

    registro_cols = [c for c in status_cols if "Registro da Aula" in str(c)]
    quiz_cols     = [c for c in status_cols if "Pause e Responda" in str(c)]

    semanas_estimadas = len(quiz_cols) // 3

    print(f"Registros encontrados : {len(registro_cols)}")
    print(f"Quizzes encontrados   : {len(quiz_cols)}")
    print(f"Semanas estimadas     : {semanas_estimadas}")
    print(f"Semanas sem registro  : {semanas_sem_registro}")

    # ----------------------------------------------------------------
    # Montar status_cols_corrigidas NA ORDEM CORRETA,
    # inserindo fake na semana exata indicada por semanas_sem_registro
    # ----------------------------------------------------------------
    status_cols_corrigidas = []
    quiz_buffer    = []
    registro_usado = 0
    semana_atual   = 1

    for col in quiz_cols:
        quiz_buffer.append(col)

        if len(quiz_buffer) == 3:
            # Adicionar os 3 quizzes desta semana
            status_cols_corrigidas.extend(quiz_buffer)
            quiz_buffer = []

            if semana_atual in semanas_sem_registro:
                # Semana declarada sem registro → inserir fake aqui
                fake_col = f"Registro_Faltante_Semana_{semana_atual}"
                print(f"Inserindo registro fake na semana {semana_atual}")
                df[fake_col] = "Não concluído"
                status_cols_corrigidas.append(fake_col)
            else:
                # Semana com registro → consumir próximo registro disponível
                if registro_usado < len(registro_cols):
                    status_cols_corrigidas.append(registro_cols[registro_usado])
                    registro_usado += 1
                else:
                    # Fallback automático: registro faltante não declarado
                    fake_col = f"Registro_Faltante_Semana_{semana_atual}"
                    print(f"[AUTO] Inserindo registro fake na semana {semana_atual}")
                    df[fake_col] = "Não concluído"
                    status_cols_corrigidas.append(fake_col)

            semana_atual += 1

    print(f"\nTotal final de colunas de status: {len(status_cols_corrigidas)}")
    print("\nSequência final de colunas detectadas:")
    for c in status_cols_corrigidas:
        print(" ", c)

    # ----------------------------------------------------------------
    # Agrupar por semana (4 colunas por semana: 3 quizzes + 1 registro)
    # ----------------------------------------------------------------
    semanas = {}
    col_idx    = 0
    semana_num = 1

    while col_idx < len(status_cols_corrigidas):
        semana_cols = []
        for _ in range(4):
            if col_idx < len(status_cols_corrigidas):
                semana_cols.append(status_cols_corrigidas[col_idx])
                col_idx += 1
        semanas[semana_num] = semana_cols
        semana_num += 1

    # ----------------------------------------------------------------
    # Montar df_out
    # ----------------------------------------------------------------
    df_out = pd.DataFrame()
    df_out["Nome"]  = df["Nome"]
    df_out["Email"] = df[col_email] if col_email else [""] * len(df)

    for semana_num, cols in semanas.items():
        quiz_contador = 0
        for col in cols:
            col_str = str(col)
            if "Registro da Aula" in col_str or "Registro_Faltante" in col_str:
                df_out[f"Atividade_Semana_{semana_num}"] = (
                    df[col]
                    .apply(limpa_status)
                    .map({"Concluído": "Sim", "Não concluído": "Não"})
                )
            elif "Pause e Responda" in col_str:
                quiz_contador += 1
                df_out[f"Semana_{semana_num}_Quiz_{quiz_contador}"] = (
                    df[col]
                    .apply(limpa_status)
                    .map({"Concluído": "Sim", "Não concluído": "Não"})
                )

    df_out.to_csv(saida, index=False, encoding="utf-8-sig", sep=";")
    print(f"\nArquivo salvo em: {saida}")


def main(entrada, saida, semanas_sem_registro=None):
    processa_relatorio_unico(entrada, saida, semanas_sem_registro)


if __name__ == "__main__":
    # Uso: python script.py entrada.csv saida.csv [semanas_sem_registro ...]
    # Exemplo Mobile (sem registro semana 5):
    #   python script.py 3DS_Mobile.csv saida.csv 5
    # Múltiplas semanas faltando:
    #   python script.py entrada.csv saida.csv 5 6

    if len(sys.argv) < 3:
        print("Uso: python preprocessa_relatorio_unico.py <entrada> <saida> [semana_sem_reg ...]")
        sys.exit(1)

    entrada = sys.argv[1]
    saida   = sys.argv[2]
    semanas_sem_registro = [int(s) for s in sys.argv[3:]] if len(sys.argv) > 3 else []

    main(entrada, saida, semanas_sem_registro)
