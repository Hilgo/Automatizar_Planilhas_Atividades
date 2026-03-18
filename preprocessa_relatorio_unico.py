import pandas as pd
import sys

if len(sys.argv) != 3:
    print("Uso: python preprocessa_relatorio_unico.py <entrada.csv> <saida.csv>")
    sys.exit(1)

entrada = sys.argv[1]
saida = sys.argv[2]

try:
    df = pd.read_csv(entrada, encoding='utf-16-le', sep=None, engine='python')
except UnicodeDecodeError:
    df = pd.read_csv(entrada, encoding='utf-8-sig', sep=None, engine='python')

# Renomear primeira coluna para Nome
df = df.rename(columns={df.columns[0]: "Nome"})

cols_email = [col for col in df.columns if "e-mail" in str(col).lower() or "email" in str(col).lower()]
col_email = cols_email[0] if cols_email else None

def limpa_status(valor):
    if pd.isna(valor):
        return "Não concluído"
    s = str(valor).strip().lower()
    if "não concluído" in s or "nao concluido" in s:
        return "Não concluído"
    if "concluído" in s or "concluido" in s:
        return "Concluído"
    return "Não concluído"

# 1) Identificar todas as colunas de status (tarefas + quizzes)
status_cols = []
for col in df.columns:
    col_str = str(col)
    # Ignorar Material da Aula
    if "Material da Aula" in col_str:
        continue
    # Verificar se contém valores de status
    unique = df[col].dropna().astype(str).unique()
    if any("concluído" in v.lower() or "não concluído" in v.lower() for v in unique):
        status_cols.append(col)

print(f"Total de colunas de status (tarefas+quizzes): {len(status_cols)}")

# 2) Agrupar por semana baseado na ORDEM das colunas (3-4 colunas por semana)
semanas = {}
col_idx = 0
semana_num = 1

while col_idx < len(status_cols):
    semana_cols = []
    # Pegar até 4 colunas consecutivas por semana
    for i in range(4):
        if col_idx < len(status_cols):
            semana_cols.append(status_cols[col_idx])
            col_idx += 1
        else:
            break
    
    semanas[semana_num] = semana_cols
    semana_num += 1

print("Colunas agrupadas por semana (ordem):")
for semana, cols in semanas.items():
    print(f"  Semana {semana}: {len(cols)} colunas")

# 3) Montar df_out
df_out = pd.DataFrame()
df_out["Nome"] = df["Nome"]
df_out["Email"] = df[col_email] if col_email else ""

# Atividades e quizzes por semana
for semana_num, cols in semanas.items():
    quiz_contador = 0

    for col in cols:
        col_str = str(col)
        # É atividade (Registro da Aula)
        if "Registro da Aula" in col_str:
            df_out[f"Atividade_Semana_{semana_num}"] = df[col].apply(limpa_status).map(
                {"Concluído": "Sim", "Não concluído": "Não"}
            )
        # É quiz (Pause e Responda)
        elif "Pause e Responda" in col_str:
            quiz_contador += 1
            df_out[f"Semana_{semana_num}_Quiz_{quiz_contador}"] = df[col].apply(limpa_status).map(
                {"Concluído": "Sim", "Não concluído": "Não"}
            )

df_out.to_csv(saida, index=False, encoding='utf-8-sig', sep=';')
print(f"OK CSV salvo em: {saida}")
print("Colunas:", df_out.columns.tolist())
