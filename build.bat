@echo off
call venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --onedir --windowed ^
  --name "Automatizador_Atividades_v3" ^
  --add-data "INSTRUCOES.txt;." ^
  --add-data "README.md;." ^
  --add-data "config.ini;." ^
  --distpath dist ^
  main.py
deactivate
echo Gerado em: dist/Automatizador_Atividades_v3/
pause
