import pandas as pd
import re

from common import get_base_dir

BASE_DIR = get_base_dir()
TRATADOS_DIR = BASE_DIR / "csv_tratados"
AVISOS_DIR = BASE_DIR / "avisos_alunos"
AVISOS_DIR.mkdir(exist_ok=True)


def extrair_info_coluna(coluna):
    """
    Extrai semana e tipo da coluna.
    Ex:
    Semana_1_Quiz_1 -> (1, quiz_1)
    Atividade_Semana_1 -> (1, registro)
    """
    if "Quiz" in coluna:
        match = re.match(r"Semana_(\d+)_Quiz_(\d+)", coluna)
        if match:
            semana = int(match.group(1))
            quiz = match.group(2)
            return semana, f"quiz_{quiz}"

    elif "Atividade" in coluna:
        match = re.match(r"Atividade_Semana_(\d+)", coluna)
        if match:
            semana = int(match.group(1))
            return semana, "registro"

    return None, None


def gera_aviso_alunos(turma_prefixo: str, ate_semana: int = None):
    arquivos = sorted(TRATADOS_DIR.glob(f"{turma_prefixo}*_tratado.csv"))

    if not arquivos:
        print(f"Atenção - Nenhum arquivo tratado encontrado para {turma_prefixo}")
        return

    print(f"Ok - Encontrados {len(arquivos)} arquivos tratados")

    avisos = {}

    for arq in arquivos:
        df = pd.read_csv(arq, sep=';')

        # Extrai disciplina do nome do arquivo
        nome_arquivo = arq.stem  # ex: 2DS_Carreira_tratado
        partes = nome_arquivo.split('_')
        disciplina = partes[1] if len(partes) >= 3 else "Desconhecida"

        for _, row in df.iterrows():
            nome = row['Nome']
            email = row.get('Email', '')

            if nome not in avisos:
                avisos[nome] = {
                    'email': email,
                    'pendencias': {}
                }

            for coluna in df.columns:
                if coluna in ['Nome', 'Email']:
                    continue

                valor = str(row[coluna]).strip().lower()

                # Só considera pendência
                if valor != 'não':
                    continue

                semana, tipo = extrair_info_coluna(coluna)

                if semana is None:
                    continue

                if ate_semana and semana > ate_semana:
                    continue

                chave = f"{disciplina} - Semana {semana}"

                if chave not in avisos[nome]['pendencias']:
                    avisos[nome]['pendencias'][chave] = {
                        'quizzes': set(),   # evita duplicação
                        'registro': False
                    }

                if "quiz" in tipo:
                    avisos[nome]['pendencias'][chave]['quizzes'].add(tipo)
                elif tipo == "registro":
                    avisos[nome]['pendencias'][chave]['registro'] = True

    # Montar mensagens
    resultado = []

    for nome, info in avisos.items():
        linhas = []

        for chave, dados in sorted(info['pendencias'].items()):
            linha = f"{chave}:\n"

            if dados['quizzes']:
                quizzes = ", ".join(sorted(dados['quizzes']))
                linha += f"  - Quizzes pendentes: {quizzes}\n"

            if dados['registro']:
                linha += f"  - Registro pendente\n"

            linhas.append(linha)

        # Se não tiver pendência, ignora
        if not linhas:
            continue

        mensagem = f"""Olá {nome},

Você ainda possui pendências na plataforma Educação Profissional:

{chr(10).join(linhas)}

Por favor, regularize o quanto antes.
"""

        resultado.append({
            'Nome': nome,
            'Email': info['email'],
            'Mensagem': mensagem
        })

    df_final = pd.DataFrame(resultado)

    saida = AVISOS_DIR / f"avisos_{turma_prefixo}{f'_ate_semana_{ate_semana}' if ate_semana else ''}.csv"
    df_final.to_csv(saida, index=False, encoding='utf-8-sig', sep=';')

    print(f"Ok - Avisos gerados: {saida}")


def main(turma_prefixo: str, ate_semana: int = None):
    gera_aviso_alunos(turma_prefixo, ate_semana)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("  python gera_aviso_alunos.py 2DS")
        print("  python gera_aviso_alunos.py 2DS 4")
        sys.exit(1)

    turma = sys.argv[1]
    ate_semana = int(sys.argv[2]) if len(sys.argv) >= 3 else None

    main(turma, ate_semana)