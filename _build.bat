@echo off
pyinstaller --onefile --name ShaderPlatformMacroGenerator --distpath ./ main.py
xcopy /Y dist\main.exe .\
pause