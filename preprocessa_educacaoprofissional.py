import pandas as pd
import sys

if len(sys.argv) != 4:
    print("Uso: python preprocessa_universal.py <entrada.csv> <tipo> <saida.csv>")
    print("  tipo = 'atividades' ou 'quizzes'")
    sys.exit(1)

entrada = sys.argv[1]
tipo = sys.argv[2].lower()
saida = sys.argv[3]

# Leitura
try:
    df = pd.read_csv(entrada, encoding='utf-16-le', sep=None, engine='python')
except UnicodeDecodeError:
    df = pd.read_csv(entrada, encoding='utf-8-sig', sep=None, engine='python')

# Renomear primeira coluna para Nome
df = df.rename(columns={df.columns[0]: "Nome"})

# Coluna de email
cols_email = [col for col in df.columns if "e-mail" in str(col).lower() or "email" in str(col).lower()]
col_email = cols_email[0] if cols_email else None

# Função corrigida: verificar "não concluído" ANTES de "concluído"
def limpa_status(valor):
    if pd.isna(valor):
        return "Não concluído"
    s = str(valor).strip().lower()
    if "não concluído" in s or "nao concluido" in s:
        return "Não concluído"
    if "concluído" in s or "concluido" in s:
        return "Concluído"
    return "Não concluído"

# Identificar colunas de status
status_cols = []
for col in df.columns:
    unique = df[col].dropna().astype(str).unique()
    if any("concluído" in str(v).lower() for v in unique):
        status_cols.append(col)

print(f"📊 Total de colunas de status: {len(status_cols)}")

# Configurar tipo
if tipo == 'atividades':
    num_cols = 7
    prefixo = "Semana"
elif tipo == 'quizzes':
    num_cols = len(status_cols)
    prefixo = "Quiz"
else:
    raise ValueError("Tipo deve ser 'atividades' ou 'quizzes'")

# Criar DataFrame de saída
df_out = pd.DataFrame()
df_out["Nome"] = df["Nome"]
df_out["Email"] = df[col_email] if col_email else ""

for i in range(1, num_cols + 1):
    if i <= len(status_cols):
        col_status = status_cols[i - 1]
        df_out[f'{prefixo}_{i}'] = df[col_status].apply(limpa_status).map(
            {"Concluído": "Sim", "Não concluído": "Não"}
        )
    else:
        df_out[f'{prefixo}_{i}'] = "Não"

df_out.to_csv(saida, index=False, encoding='utf-8-sig', sep=';')
print(f"✅ CSV salvo em: {saida}")
print(f"📋 Colunas: {df_out.columns.tolist()}")
