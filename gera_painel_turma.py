import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
TRATADOS_DIR = BASE_DIR / "csv_tratados"
PAINEL_DIR = BASE_DIR / "painel_turmas"
PAINEL_DIR.mkdir(exist_ok=True)

def gera_resumo_pendencias(turma_prefixo: str):
    arquivos = sorted(TRATADOS_DIR.glob(f"{turma_prefixo}*_tratado.csv"))
    if not arquivos:
        print(f"Nenhum arquivo tratado para {turma_prefixo}")
        return

    registros = []  # cada item será uma pendência (linha no resumo)

    for arq in arquivos:
        df = pd.read_csv(arq, sep=';')
        nome_disc = arq.stem.replace('_tratado', '')  # ex: 2DS_Logica
        turma = nome_disc.split('_')[0]               # 2DS
        disciplina = '_'.join(nome_disc.split('_')[1:]) or nome_disc  # Logica

        for col in df.columns:
            if col in ['Nome', 'Email']:
                continue

            # Só colunas de atividade/quiz
            if col.startswith('Atividade_Semana_') or col.startswith('Semana_'):
                for _, row in df.iterrows():
                    valor = str(row[col])
                    if valor.strip().lower() == 'não':  # pendência
                        nome = row['Nome']
                        email = row['Email'] if 'Email' in df.columns else ''

                        if col.startswith('Atividade_Semana_'):
                            semana = col.replace('Atividade_Semana_', '')
                            tipo = 'Atividade'
                            quiz_num = ''
                        else:
                            # Formato: Semana_X_Quiz_Y
                            partes = col.split('_')  # ['Semana','X','Quiz','Y']
                            semana = partes[1] if len(partes) > 1 else ''
                            tipo = 'Quiz'
                            quiz_num = partes[3] if len(partes) > 3 else ''

                        registros.append({
                            'Turma': turma,
                            'Disciplina': disciplina,
                            'Nome': nome,
                            'Email': email,
                            'Semana': semana,
                            'Tipo': tipo,
                            'Quiz_num': quiz_num,
                        })

    if not registros:
        print(f"Nenhuma pendência encontrada para {turma_prefixo}")
        return

    resumo_df = pd.DataFrame(registros)
    resumo_df = resumo_df.sort_values(['Nome', 'Semana', 'Disciplina', 'Tipo', 'Quiz_num'])

    saida = PAINEL_DIR / f"resumo_pendencias_{turma_prefixo}.csv"
    resumo_df.to_csv(saida, index=False, encoding='utf-8-sig', sep=';')
    print(f"✅ Resumo de pendências salvo em: {saida}")


if __name__ == "__main__":
    # Exemplo: gerar para 2DS e 3DS
    gera_resumo_pendencias("2DS")
    gera_resumo_pendencias("3DS")
