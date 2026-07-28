@echo off
title KaiRest - Detener
cd /d "%~dp0"
echo Deteniendo KaiRest...
echo.
docker compose down
echo.
echo KaiRest detenido. Los datos se conservan.
echo Puedes cerrar esta ventana.
pause >nul
