@echo off
echo ========================================
echo Preparando pacote de distribuicao v3.2
echo ========================================

if not exist "dist\Automatizador_Atividades_v3\Automatizador_Atividades_v3.exe" (
    echo ERRO: Execute build.bat primeiro!
    pause
    exit /b
)

REM Limpar release anterior
if exist release rmdir /s /q release
mkdir release

REM Copiar aplicativo com todos os arquivos
xcopy /E /I /Y "dist\Automatizador_Atividades_v3" "release\Automatizador_Atividades_v3"

REM Criar pastas de dados
mkdir release\csv_brutos
mkdir release\csv_fora_ordem
mkdir release\avisos_alunos
mkdir release\csv_tratados
mkdir release\pendencias_detalhadas
mkdir release\painel_turmas

REM Copiar arquivos de instrucoes e configuracao para dentro da pasta do app
if not exist "release\Automatizador_Atividades_v3\INSTRUCOES.txt" copy INSTRUCOES.txt "release\Automatizador_Atividades_v3\INSTRUCOES.txt"
if not exist "release\Automatizador_Atividades_v3\README.md" copy README.md "release\Automatizador_Atividades_v3\README.md"
if not exist "release\Automatizador_Atividades_v3\config.ini" copy config.ini "release\Automatizador_Atividades_v3\config.ini"

echo.
echo Arquivo gerado em: release\
echo Arquivos de instrucoes estao em: release\Automatizador_Atividades_v3\INSTRUCOES.txt
echo.

REM Gerar zip apenas com o conteudo da pasta do app (sem nivel extra de release)
powershell Compress-Archive -Path "release\Automatizador_Atividades_v3\*" -DestinationPath "automatizador_v3_professor.zip" -Force
echo Pacote criado: automatizador_v3_professor.zip
pause
