
# 📊 Controle de Registros e Quizzes – Educação Profissional

Sistema para análise de **registros semanais** e **quizzes** exportados da plataforma Educação Profissional.

O objetivo é automatizar a verificação de quais alunos responderam quizzes e fizeram registros semanais, gerando relatórios de acompanhamento e pendências.

Este projeto foi pensado para **professores**, inclusive aqueles que **não têm experiência com programação**.

---

# 🖥️ Interface gráfica (modo recomendado)

Para facilitar o uso, o projeto possui um programa com **interface gráfica**:

📄 `main.py`

Esse programa permite executar todo o processo **sem precisar usar comandos no terminal**.

A interface permite:

✔ listar automaticamente os arquivos da pasta `csv_brutos`  
✔ escolher a **turma** que será analisada  
✔ executar todo o **pipeline automaticamente**  

Ou seja, basta:

1. Abrir o programa
2. Selecionar a turma
3. Incluir até qual semana gerar as pendências
4. Clicar em **Executar**

O sistema irá:

✔ processar os CSVs  
✔ combinar dados se necessário  
✔ gerar relatórios de pendências

---

# 🧠 Visão Geral do Funcionamento

1. O professor exporta os **CSVs da plataforma Educação Profissional** (Relatórios -> Conclusão de Atividades)
2. Os arquivos são colocados nas pastas do projeto
3. O programa `main.py` executa o processamento
4. O sistema gera relatórios automáticos

---

# 📁 Estrutura do Projeto

projeto/

csv_brutos/  
csv_fora_ordem/  

pipeline_processa_csvs.py  
combina_reordena.py  
main.py  
config.ini  

saida/

Descrição:

📂 **csv_brutos** → CSV exportado da plataforma já pronto  
📂 **csv_fora_ordem** → arquivos separados de quiz e registros  
⚙️ **config.ini** → configurações do sistema  
🐍 **pipeline_processa_csvs.py** → script principal que executa as rotinas de tratamento dos arquivos e geração de planilhas detalhadas
🖥️ **main.py** → interface gráfica para executar o sistema  

---

# ⚠️ Problema da Ordem Cronológica

Em algumas disciplinas a plataforma exporta as semanas fora da ordem correta.

Exemplo exportado:

Semana 6, Semana 5, Semana 4, Semana 7, Semana 2, Semana 1, Semana 3

Mas o correto seria:

Semana 1, Semana 2, Semana 3, Semana 4, Semana 5, Semana 6, Semana 7

O script `combina_reordena.py` resolve isso automaticamente.

---

# ⚙️ Configuração de Ordem de Semanas

Se uma disciplina exportar as semanas em uma ordem diferente, você pode configurar no arquivo **config.ini**.

Exemplo:

[ORDENS]

2DS_Carreiras = S6,S5,S4,S7,S2,S1,S3  
3DS_Versionamento = S1,S2,S3,S4,S5,S7,S6

Como funciona:

Se os arquivos forem:

2DS_Carreiras_Quiz.csv  
2DS_Carreiras_Registros.csv

O sistema identifica automaticamente a chave:

2DS_Carreiras

E aplica a ordem definida.

Se não houver configuração, a ordem padrão será usada.

---

# 📦 Exemplo de Arquivos

csv_brutos/

2DS_Logica.csv

csv_fora_ordem/

2DS_Carreiras_Quiz.csv  
2DS_Carreiras_Registros.csv  

3DS_Versionamento_Quiz.csv  
3DS_Versionamento_Registros.csv

---

# ▶️ Execução do Sistema

## Método recomendado (interface gráfica)

Executar:

python main.py Ou iniciar o arquivo exe

Depois:

1. Selecionar a turma
2. Clicar em **Executar**

---

## Método avançado (linha de comando)

Também é possível executar manualmente.

Para corrigir arquivos fora de ordem:

python combina_reordena.py csv_fora_ordem/2DS_Carreiras_Registros.csv csv_fora_ordem/2DS_Carreiras_Quiz.csv

Depois executar:

python controle_alunos.py

---

# 📊 Saídas Geradas

O sistema gera:

📄 controle_alunos_<turma>.csv  
📄 controle_alunos_resumo_<turma>.csv  
📄 pendencias_detalhadas_<turma>.csv

---

# 👨‍🏫 Objetivo Educacional

Este projeto foi criado para ajudar professores a:

✔ acompanhar participação dos alunos  
✔ identificar pendências rapidamente  
✔ reduzir trabalho manual de conferência  

