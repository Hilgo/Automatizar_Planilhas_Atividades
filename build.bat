@echo off
call venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --onefile --windowed --noconsole ^
  --name "Automatizador_Atividades_v3" ^
  --distpath dist ^
  main.py
deactivate
echo  dist/Automatizador_Atividades_v3.exe
pause
