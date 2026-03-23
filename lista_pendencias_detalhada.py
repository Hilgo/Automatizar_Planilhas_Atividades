import pandas as pd

from common import get_base_dir

BASE_DIR = get_base_dir()
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
    print(f"Ok - Pendências detalhadas geradas em: {saida}")

def controle_por_aluno(turma_prefixo: str, ate_semana: int = None):
    """
    Gera um relatório consolidado dinamicamente baseado nas disciplinas e semanas encontradas.
    Formato: Nome | Disciplina S1 | Disciplina S2 | ... | Total
    Para cada célula: Q1,Q2,Q3,R (quizes/registro faltando seguindo padrão 3 quizzes + 1 registro)
    """
    arquivos = sorted(TRATADOS_DIR.glob(f"{turma_prefixo}*_tratado.csv"))
    if not arquivos:
        print(f"Nenhum arquivo tratado para {turma_prefixo}")
        return

    # Descobrir quais semanas existem por disciplina
    colunas_encontradas = set()  # Set de (disciplina, semana)

    for arq in arquivos:
        df = pd.read_csv(arq, sep=';')
        nome_arquivo = arq.stem
        disciplina = nome_arquivo.replace(f"{turma_prefixo}_", "").replace("_tratado", "")

        for col in df.columns:
            if col in ["Nome", "Email"]:
                continue

            if col.startswith("Atividade_Semana_"):
                try:
                    semana = int(col.replace("Atividade_Semana_", ""))
                except ValueError:
                    continue
                if ate_semana is None or semana <= ate_semana:
                    colunas_encontradas.add((disciplina, semana))

            elif col.startswith("Semana_"):
                partes = col.split("_")
                if len(partes) >= 3 and partes[2].lower() == "quiz":
                    try:
                        semana = int(partes[1])
                    except ValueError:
                        continue
                    if ate_semana is None or semana <= ate_semana:
                        colunas_encontradas.add((disciplina, semana))

    if not colunas_encontradas:
        print(f"Nenhuma coluna encontrada para {turma_prefixo}")
        return

    colunas_ordenadas = sorted(colunas_encontradas, key=lambda x: (x[0], x[1]))

    # Dicionário para armazenar pendências de cada aluno
    # {Nome: {(disciplina, semana): {'registro_faltante': bool, 'quizzes_presentes': set(int)}}}
    alunos_pendencias = {}

    # Processar cada arquivo para contagem de pendências
    for arq in arquivos:
        df = pd.read_csv(arq, sep=';')
        nome_arquivo = arq.stem
        disciplina = nome_arquivo.replace(f"{turma_prefixo}_", "").replace("_tratado", "")

        for _, row in df.iterrows():
            nome = row["Nome"]
            if nome not in alunos_pendencias:
                alunos_pendencias[nome] = {}
                for disc, semana in colunas_ordenadas:
                    alunos_pendencias[nome][(disc, semana)] = {
                        'registro_faltante': False,
                        'quizzes_presentes': set(),
                        'quizzes_faltantes': set()
                    }

            # Inicializa se disciplina/semana potencialmente não houver para esse aluno
            if (disciplina, None) not in alunos_pendencias[nome]:
                pass

            for col in df.columns:
                if col in ["Nome", "Email"]:
                    continue
                if not (col.startswith("Atividade_Semana_") or col.startswith("Semana_")):
                    continue

                semana = None
                tipo = None
                quiz_num = None

                if col.startswith("Atividade_Semana_"):
                    try:
                        semana = int(col.replace("Atividade_Semana_", ""))
                        tipo = "registro"
                    except ValueError:
                        continue
                elif col.startswith("Semana_"):
                    partes = col.split("_")
                    if len(partes) >= 3 and partes[2].lower() == "quiz":
                        try:
                            semana = int(partes[1])
                        except ValueError:
                            continue
                        tipo = "quiz"
                        try:
                            quiz_num = int(partes[3]) if len(partes) > 3 else 1
                        except ValueError:
                            quiz_num = 1
                    else:
                        continue

                if semana is None or (ate_semana is not None and semana > ate_semana):
                    continue

                valor = str(row[col]).strip().lower()

                key = (disciplina, semana)
                if key not in alunos_pendencias[nome]:
                    # Adiciona caso não esteja inicializada (novas semanas inesperadas)
                    alunos_pendencias[nome][key] = {
                        'registro_faltante': False,
                        'quizzes_presentes': set(),
                        'quizzes_faltantes': set()
                    }

                if tipo == "registro":
                    if valor == "não":
                        alunos_pendencias[nome][key]['registro_faltante'] = True
                elif tipo == "quiz" and quiz_num is not None:
                    if valor != "não":
                        alunos_pendencias[nome][key]['quizzes_presentes'].add(quiz_num)

    # Calcula os quizzes faltantes com base no padrão 3 quizzes semanais
    for nome, pendencias in alunos_pendencias.items():
        for key, info in pendencias.items():
            present = info['quizzes_presentes']
            all_expected = {1, 2, 3}
            missing = sorted(list(all_expected - present))
            info['quizzes_faltantes'] = missing

    if not alunos_pendencias:
        print(f"Nenhum aluno encontrado para {turma_prefixo}")
        return

    # Monta o DataFrame com colunas dinamicas
    dados = []
    for nome, pendencias in alunos_pendencias.items():
        linha = {"Nome": nome}
        total_geral = 0

        for disc, semana in colunas_ordenadas:
            info = pendencias.get((disc, semana), {
                'registro_faltante': False,
                'quizzes_faltantes': []
            })
            faltas = []
            for q in info['quizzes_faltantes']:
                faltas.append(f"Q{q}")
            if info.get('registro_faltante'):
                faltas.append("R")

            total_geral += len(info['quizzes_faltantes']) + (1 if info.get('registro_faltante') else 0)
            linha[f"{disc} S{semana}"] = ",".join(faltas) if faltas else ""

        linha["Total"] = total_geral
        dados.append(linha)

    df = pd.DataFrame(dados)
    df.sort_values("Nome", inplace=True)

    saida_principal = Saida_DIR / f"controle_alunos_{turma_prefixo}.csv"
    df.to_csv(saida_principal, index=False, encoding='utf-8-sig', sep=';')

    # adiciona legenda ao final do arquivo CSV principal
    with open(saida_principal, 'a', encoding='utf-8-sig', newline='') as f:
        f.write('\n')
        f.write('Legenda: Q1/Q2/Q3 = quizzes faltando; R = registro faltando; vazio = sem pendência.\n')

    # Gera CSV adicional apenas com contagem total de registros e quizzes faltantes
    resumo = []
    for nome, pendencias in alunos_pendencias.items():
        total_registros = 0
        total_quizzes = 0
        for key, info in pendencias.items():
            if info.get('registro_faltante'):
                total_registros += 1
            total_quizzes += len(info.get('quizzes_faltantes', []))

        resumo.append({
            'Nome': nome,
            'Registros_Faltando': total_registros,
            'Quizzes_Faltando': total_quizzes,
            'Total_Faltas': total_registros + total_quizzes
        })

    df_resumo = pd.DataFrame(resumo)
    df_resumo.sort_values('Nome', inplace=True)

    saida_resumo = Saida_DIR / f"controle_alunos_resumo_{turma_prefixo}.csv"
    df_resumo.to_csv(saida_resumo, index=False, encoding='utf-8-sig', sep=';')

    # adiciona título de contexto no arquivo de resumo sem reescrever o cabeçalho
    with open(saida_resumo, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    semana_contexto = ate_semana if ate_semana is not None else 'todas'
    with open(saida_resumo, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(f"Resumo de pendências até semana: {semana_contexto}\n")
        f.write(content)

    print(f"Ok - Controle por aluno gerado em: {saida_principal} (incluindo legenda)")
    print(f"Ok - Resumo por aluno gerado em: {saida_resumo}")


def main(turma_prefixo: str, ate_semana: int = None):
    lista_pendencias(turma_prefixo, ate_semana)
    controle_por_aluno(turma_prefixo, ate_semana)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("  python lista_pendencias_detalhada.py 2DS")
        print("  python lista_pendencias_detalhada.py 2DS 4")
        sys.exit(1)

    turma = sys.argv[1]
    ate_semana = int(sys.argv[2]) if len(sys.argv) >= 3 else None

    main(turma, ate_semana)
