@echo off
echo ========================================
echo 📦 ZIP PROFESSOR v3.2
echo ========================================

if not exist dist\Automatizador_v3.exe (
    echo ❌ pyinstaller primeiro!
    pause
    exit /b
)

REM Limpar
if exist release rmdir /s /q release
mkdir release

REM Pastas vazias
mkdir release\csv_brutos
mkdir release\avisos_alunos
mkdir release\csv_tratados
mkdir release\pendencias_detalhadas

REM ARQUIVOS ESSENCIAIS
copy dist\Automatizador_v3.exe release\
REM ✅ CONFIG NA MESMA PASTA DO EXE
copy config.ini release\config.ini
copy INSTRUCOES.txt release\INSTRUCOES.txt

echo ✅ release/ pronto com config.ini!
powershell Compress-Archive release automatizador_v3_professor.zip -Force
echo 📦 ZIP: automatizador_v3_professor.zip
pause
