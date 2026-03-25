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

- `csv_brutos/` — entrada de arquivos CSV únicos do LMS (nome: `TURMA_DISCIPLINA.csv`) para disciplinas com ordem correta
- `csv_fora_ordem/` — entrada de pares CSV desordenados (nomes: `TURMA_DISCIPLINA_Quiz.csv` e `TURMA_DISCIPLINA_Registros.csv`) para disciplinas que precisam de reordenação cronológica
- `csv_tratados/` — arquivos processados (saída automática)
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
4. Copie os CSVs da plataforma para a pasta apropriada:
   - **Disciplinas com ordem correta**: `csv_brutos/` com nome `TURMA_DISCIPLINA.csv` (ex: `2DS_Logica.csv`)
   - **Disciplinas fora de ordem**: `csv_fora_ordem/` com nomes `TURMA_DISCIPLINA_Quiz.csv` e `TURMA_DISCIPLINA_Registros.csv` (ex: `2DS_Carreiras_Quiz.csv` e `2DS_Carreiras_Registros.csv`)
5. Execute no terminal:
   ```powershell
   python main.py
   ```

## ⚠️ Problema da Ordem Cronológica

A plataforma Educação Profissional nem sempre exporta os dados na ordem esperada das semanas. Em algumas disciplinas, os registros e quizzes aparecem fora da sequência cronológica (ex: Semana 6, depois 5, 4, 7, 2, 1, 3), o que dificulta acompanhar o verdadeiro progresso dos alunos ao longo do tempo.

Para resolver isso, o sistema oferece duas abordagens:

- **Disciplinas normais**: Use `csv_brutos/` para arquivos únicos já organizados
- **Disciplinas desordenadas**: Use `csv_fora_ordem/` para combinar e reordenar automaticamente

## 📌 Instruções de download na plataforma

### Para disciplinas com ordem correta:
1. Acesse Educação Profissional.
2. Navegue até a turma/disciplina.
3. Relatórios > Conclusão de Atividades.
4. Ao final, clique em `Download em formato compatível com Excel (.csv)`.
5. Salve em `csv_brutos/` com nome: `TURMA_DISCIPLINA.csv`.

### Para disciplinas fora de ordem:
**Por que isso acontece?** Em algumas disciplinas, a plataforma Educação Profissional exporta os dados fora da ordem cronológica (ex: Semana 6, 5, 4, 7, 2, 1, 3), o que prejudica a compreensão real do andamento dos registros e tarefas dos alunos ao longo do tempo.

**Como resolver:**
1. Acesse Educação Profissional e navegue até a disciplina.
2. Em Relatórios, baixe **separadamente**:
   - O relatório de **Registros da Aula** (atividades de participação)
   - O relatório de **Pause e Responda** (quizzes)
3. Salve em `csv_fora_ordem/` com nomes padronizados:
   - `TURMA_DISCIPLINA_Registros.csv` (ex: `2DS_Carreiras_Registros.csv`)
   - `TURMA_DISCIPLINA_Quiz.csv` (ex: `2DS_Carreiras_Quiz.csv`)
4. O sistema irá combinar ambos os arquivos e reordenar automaticamente para ordem cronológica (Semanas 1-7), intercalando registros e quizzes por semana.

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
