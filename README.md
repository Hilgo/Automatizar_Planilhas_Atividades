# Automatizador de Planilhas de Atividades

Sistema para automatizar análise de pendências de alunos por turma e disciplina,
com geração de relatórios detalhados e resumo.

## ✅ O que faz

- Processa CSVs brutos (`csv_brutos/`) gerados a partir da plataforma Educação Profissional.
- Gera arquivos tratados (`csv_tratados/`) (via `pipeline_processa_csvs`).
- Gera relatórios:
  - `pendencias_detalhadas_<turma>.csv`
  - `controle_alunos_<turma>.csv` (por semana e disciplina: `Qx`, `R`)
  - `controle_alunos_resumo_<turma>.csv` (totais por aluno)
- Emite avisos por aluno em `avisos_alunos/`.

## 📁 Estrutura de pastas

- `csv_brutos/` — entrada de arquivos CSV do LMS
- `csv_tratados/` — arquivos processados
- `pendencias_detalhadas/` — relatórios gerados
- `painel_turmas/` — resultado consolidado para entrada dos professores
- `avisos_alunos/` — mensagens por aluno

## 📦 Instalação / execução

1. Tenha Python 3 instalado.
2. Crie e ative virtualenv (opcional):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instale dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copie os CSVs da plataforma para `csv_brutos` com nome padrão:
   `TURMA_DISCIPLINA.csv` (ex: `2DS_Logica.csv`).
5. Execute no terminal:
   ```powershell
   python main.py
   ```

## 📌 Instruções de download na plataforma

1. Acesse Educação Profissional.
2. Navegue até a turma/disciplina.
3. Relatórios > Conclusão de Atividades.
4. Ao final, clique em `Download em formato compatível com Excel (.csv)`.
5. Salve com nome: `TURMA_DISCIPLINA.csv`.

## 🧩 Uso do modo linha de comando

Para só o script de pendências:
```powershell
python lista_pendencias_detalhada.py 2DS 4
```
Isso gera arquivos em `pendencias_detalhadas/`.

## 📝 Legenda no relatório

- `Q1`, `Q2`, `Q3`: quizzes faltando por semana.
- `R`: registro (atividade semanal) faltando.
- vazio: sem pendências.

## 🔧 Configuração

Arquivo: `config.ini`:
```ini
[TURMAS]
lista = 2DS,3DS,2ADME,

[SEMANAS]
padrao = 7
```

## 🛠️ Componentes

- `pipeline_processa_csvs.py`
- `lista_pendencias_detalhada.py`
- `gera_aviso_alunos.py`
- `main.py` (interface tkinter)

## 🗂️ Saída

- `Kontrol`: `controle_alunos_<turma>.csv`, `controle_alunos_resumo_<turma>.csv`.
- `Pendências detalhadas`: `pendencias_detalhadas_<turma>.csv`.

## 💬 Feedback

- Se precisar de novos relatórios por disciplina ou export Excel direto, abra issue no Github.
