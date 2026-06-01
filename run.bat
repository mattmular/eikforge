@echo off
:loop
echo [%date% %time%] Starting Eikforge BOT...

python "%~dp0bot.py"

echo [%date% %time%] Script ended or crashed. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul

goto loop

pause