@echo off
echo ========================================
echo 📦 CRIANDO ZIP PROFESSOR v3.2
echo ========================================

REM Limpar release anterior
if exist release rmdir /s /q release

REM Criar estrutura
mkdir release
mkdir release\csv_brutos
mkdir release\painel_turmas  
mkdir release\avisos_alunos

REM Copiar arquivos
copy dist\Automatizador_v3.exe release\
copy config.ini.example release\config.ini
copy INSTRUCOES.md release\INSTRUCOES.txt

REM ZIP (Windows 11+)
powershell Compress-Archive -Path release\* -DestinationPath automatizador_v3_professor.zip -Force

echo.
echo ✅ ZIP criado: automatizador_v3_professor.zip (40MB)
echo 📁 Conteúdo:
dir release
pause
