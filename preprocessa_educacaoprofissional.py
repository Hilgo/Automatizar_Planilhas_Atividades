import pandas as pd
import sys
import numpy as np


if len(sys.argv) != 3:
    print("Uso: python preprocessa_educacaoprofissional.py <entrada.csv> <saida.csv>")
    sys.exit(1)

entrada = sys.argv[1]
saida = sys.argv[2]

# 1) Leitura com UTF-16-LE ou UTF-8-sig (se ainda não estiver UTF-16-LE)
try:
    df = pd.read_csv(entrada, encoding='utf-16-le', sep=None, engine='python')
    print("✅ Leitura com UTF-16-LE")
except UnicodeDecodeError as e:
    print("🔴 Falhou com UTF-16-LE, tentando UTF-8-sig")
    df = pd.read_csv(entrada, encoding='utf-8-sig', sep=None, engine='python')


print("📋 Colunas encontradas (repr):")
for col in df.columns:
    print(f"  {repr(col)}")

# 2) Coluna de nome do aluno
df = df.rename(columns={df.columns[0]: "Nome"})
print(f"✅ Renomeada coluna de nome para 'Nome'")

# 3) Coluna de email
cols_email = [col for col in df.columns if "e-mail" in str(col).lower()]
col_email = cols_email[0] if cols_email else None


# 4) Limpar valores de status (remover espaços extras, etc.)
def limpa_status(valor):
    if pd.isna(valor):
        return "Não concluído"
    s = str(valor).strip()
    if "Concluído" in s:
        return "Concluído"
    if "Não concluído" in s:
        return "Não concluído"
    return "Não concluído"

# 5) Identificar colunas de status de atividade
status_cols = []
for col in df.columns:
    # Se a coluna tiver valores de status, consideramos como coluna de atividade
    unique = df[col].dropna().astype(str).unique()
    if any("Concluído" in str(v) for v in unique) or any("Não concluído" in str(v) for v in unique):
        status_cols.append(col)

if not status_cols:
    raise ValueError("Nenhuma coluna de status de atividade encontrada.")

print("📊 Colunas de status encontradas:")
for col in status_cols:
    print(f"  {repr(col)}")


# 6) DataFrame de saída
df_out = pd.DataFrame()
df_out["Nome"] = df["Nome"]
df_out["Email"] = df[col_email] if col_email else df["Nome"]


# 7) Mapear status para Semana 1-7
for i in range(1, 8):
    if i <= len(status_cols):
        col = status_cols[i-1]
        df[col] = df[col].map(limpa_status).fillna("Não concluído")
        df_out[f"Semana_{i}"] = df[col].map(
            {"Concluído": "Sim", "Não concluído": "Não"},
            na_action="ignore"
        ).fillna("Não")
    else:
        df_out[f"Semana_{i}"] = "Não"


# 8) Salvar CSV com separador de ponto e vírgula (Excel Brasil)
df_out.to_csv(saida, index=False, encoding="utf-8-sig", sep=';')
print(f"✅ CSV gerado com 9 colunas (Nome, Email, Semana_1-7): {saida}")
print("📋 Colunas de saída:")
print(df_out.columns.tolist())
