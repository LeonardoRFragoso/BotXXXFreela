@echo off
setlocal enabledelayedexpansion

REM Verifica se o diretório Log existe, se não, cria
if not exist Log (
    mkdir Log
)

:loop
set "datetime=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "datetime=!datetime: =0!"
"C:\Users\Administrador\AppData\Local\Programs\Python\Python312\python.exe" Bot.py > Log/!datetime!.txt 2>&1
if %errorlevel% neq 0 (
    echo Script falhou com código de erro %errorlevel%. Verifique os logs.
    timeout /t 5
)
timeout /t 5
goto loop
