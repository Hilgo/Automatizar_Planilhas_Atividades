import sys
import pandas as pd
import re
from pathlib import Path
import configparser


def limpa_status(valor):
    if pd.isna(valor):
        return "Não concluído"
    s = str(valor).strip().lower()
    if "não concluído" in s or "nao concluido" in s:
        return "Não concluído"
    if "concluído" in s or "concluido" in s:
        return "Concluído"
    return "Não concluído"


def extrair_chave(nome_arquivo):
    """
    Extrai TURMA_DISCIPLINA do nome do arquivo.
    Ex:
    2DS_Carreiras_Quiz.csv -> 2DS_Carreiras
    2DS_Carreiras_Registros.csv -> 2DS_Carreiras
    """
    nome = Path(nome_arquivo).stem
    chave = re.sub(r'_(Quiz|Quizzes|Registros?)$', '', nome, flags=re.I)
    return chave


def carregar_ordem(chave):
    """
    Lê a ordem das semanas no config.ini
    """
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    ordem_padrao = ['S1','S2','S3','S4','S5','S6','S7']

    if "ORDENS" not in config:
        return ordem_padrao

    if chave not in config["ORDENS"]:
        return ordem_padrao

    ordem = config["ORDENS"][chave].split(",")

    ordem = [o.strip() for o in ordem]

    return ordem


def processa_csv(entrada):
    try:
        df = pd.read_csv(entrada, encoding='utf-16-le', sep=None, engine='python')
    except UnicodeDecodeError:
        df = pd.read_csv(entrada, encoding='utf-8-sig', sep=None, engine='python')

    df = df.rename(columns={df.columns[0]: "Nome"})

    cols_email = [
        col for col in df.columns
        if "e-mail" in str(col).lower() or "email" in str(col).lower()
    ]

    col_email = cols_email[0] if cols_email else None

    df["Email"] = df[col_email] if col_email else ""

    status_cols = []

    for col in df.columns:
        col_str = str(col)

        if "Material da Aula" in col_str:
            continue

        unique = df[col].dropna().astype(str).unique()

        if any("concluído" in v.lower() or "não concluído" in v.lower() for v in unique):
            status_cols.append(col)

    return df, status_cols


def main(regs_csv=None, quiz_csv=None):

    if regs_csv is None or quiz_csv is None:
        if len(sys.argv) != 3:
            print("Uso: python combina_reordena.py <registros.csv> <quizzes.csv>")
            sys.exit(1)

        regs_csv = sys.argv[1]
        quiz_csv = sys.argv[2]

    p_regs = Path(regs_csv)

    base_name = re.sub(
        r'_(Registros?|Quiz|Quizzes)$',
        '',
        p_regs.stem,
        flags=re.I
    )

    saida = Path("csv_tratados") / (base_name + "_tratado.csv")

    print(f"Processando -> {saida.name}")

    df_regs, status_regs = processa_csv(regs_csv)
    df_quiz, status_quiz = processa_csv(quiz_csv)

    # chave TURMA_DISCIPLINA
    chave = extrair_chave(regs_csv)

    # ordem definida no config.ini
    ordem_atual = carregar_ordem(chave)

    # ordem correta
    ordem_cronologica = ['S1','S2','S3','S4','S5','S6','S7']

    print(f"Usando ordem {ordem_atual} para {chave}")

    # mapeia registros
    mapping_regs = {}

    for semana in range(1, 8):

        bloco = ordem_cronologica[semana - 1]

        pos = ordem_atual.index(bloco)

        if pos < len(status_regs):
            mapping_regs[status_regs[pos]] = f'Atividade_Semana_{semana}'

    # mapeia quizzes
    mapping_quiz = {}

    for semana in range(1, 8):

        bloco = ordem_cronologica[semana - 1]

        pos = ordem_atual.index(bloco)

        start_idx = pos * 3

        for j in range(3):

            quiz_idx = start_idx + j

            if quiz_idx < len(status_quiz):

                mapping_quiz[status_quiz[quiz_idx]] = f'Semana_{semana}_Quiz_{j+1}'

    df_regs_out = df_regs.rename(columns=mapping_regs)
    df_quiz_out = df_quiz.rename(columns=mapping_quiz)

    # limpar status
    for col in df_regs_out.columns:

        if col.startswith('Atividade_Semana_'):

            df_regs_out[col] = (
                df_regs_out[col]
                .apply(limpa_status)
                .map({"Concluído": "Sim", "Não concluído": "Não"})
            )

    for col in df_quiz_out.columns:

        if col.startswith('Semana_') and '_Quiz_' in col:

            df_quiz_out[col] = (
                df_quiz_out[col]
                .apply(limpa_status)
                .map({"Concluído": "Sim", "Não concluído": "Não"})
            )

    cols_final = ['Nome', 'Email']

    for semana in range(1, 8):

        col_reg = f'Atividade_Semana_{semana}'

        if col_reg in df_regs_out.columns:
            cols_final.append(col_reg)

        for quiz in range(1, 4):

            col_quiz = f'Semana_{semana}_Quiz_{quiz}'

            if col_quiz in df_quiz_out.columns:
                cols_final.append(col_quiz)

    df_final = pd.merge(
        df_regs_out,
        df_quiz_out,
        on=['Nome', 'Email'],
        how='outer'
    )

    df_final = df_final[cols_final]

    df_final.to_csv(
        saida,
        index=False,
        encoding='utf-8-sig',
        sep=';'
    )

    print(f"SALVO: {saida}")

    print("Colunas finais:", df_final.columns.tolist())

    # validação
    print("\n=== VALIDACAO ===")

    print(f"Numero de alunos: {len(df_final)}")
    print(f"Numero de colunas: {len(df_final.columns)} (esperado: 30)")

    for col in df_final.columns:

        if col in ['Nome', 'Email']:
            continue

        unique_vals = df_final[col].dropna().unique()

        if set(unique_vals) - {'Sim', 'Não'}:
            print(f"ERRO: Coluna {col} tem valores invalidos: {unique_vals}")

        else:

            sim_count = (df_final[col] == 'Sim').sum()
            nao_count = (df_final[col] == 'Não').sum()

            print(f"OK: {col}: Sim={sim_count}, Nao={nao_count}")

    print("=== FIM VALIDACAO ===")


if __name__ == "__main__":
    main()