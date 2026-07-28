@echo off
title KaiRest - Reiniciar
cd /d "%~dp0"
echo Reiniciando KaiRest...
echo.
docker compose restart
echo.
echo KaiRest reiniciado.
echo Puedes cerrar esta ventana.
pause >nul
