@echo off
setlocal
REM ============================================================
REM  Instala / repara ActivosApp como servicio de Windows (NSSM)
REM  Copia este .bat Y nssm.exe junto a run.py y ejecuta como ADMIN.
REM  Se puede correr varias veces: limpia lo previo y reinstala.
REM ============================================================

set "PROYECTO=%~dp0"
if "%PROYECTO:~-1%"=="\" set "PROYECTO=%PROYECTO:~0,-1%"

set "ENTRADA=run.py"
set "PYTHON=%PROYECTO%\venv\Scripts\python.exe"
set "SERVICIO=ActivosApp"

set "NSSM=%PROYECTO%\nssm.exe"
if exist "%NSSM%" goto nssm_ok
where nssm.exe >nul 2>&1 && set "NSSM=nssm.exe" && goto nssm_ok
echo [ERROR] No encuentro nssm.exe. Copialo (carpeta win64) junto a este .bat.
pause & exit /b 1
:nssm_ok

echo.
echo   Proyecto: %PROYECTO%
echo   Python:   %PYTHON%
echo   NSSM:     %NSSM%
echo.

if not exist "%PYTHON%" (echo [ERROR] No existe %PYTHON% & pause & exit /b 1)
if not exist "%PROYECTO%\%ENTRADA%" (echo [ERROR] No existe %PROYECTO%\%ENTRADA% & pause & exit /b 1)

echo Limpiando instalacion previa (si existe)...
"%NSSM%" stop %SERVICIO% >nul 2>&1
"%NSSM%" remove %SERVICIO% confirm >nul 2>&1

echo Instalando servicio %SERVICIO%...
"%NSSM%" install %SERVICIO% "%PYTHON%"

REM --- CLAVE: guardar la ruta de run.py CON comillas literales ---
REM     (por los espacios en la ruta de OneDrive)
"%NSSM%" set %SERVICIO% AppParameters "\"%PROYECTO%\%ENTRADA%\""

"%NSSM%" set %SERVICIO% AppDirectory "%PROYECTO%"
if not exist "%PROYECTO%\logs" mkdir "%PROYECTO%\logs"
"%NSSM%" set %SERVICIO% AppStdout "%PROYECTO%\logs\servicio.log"
"%NSSM%" set %SERVICIO% AppStderr "%PROYECTO%\logs\error.log"
"%NSSM%" set %SERVICIO% AppEnvironmentExtra MODO_SERVICIO=1 PYTHONUTF8=1
"%NSSM%" set %SERVICIO% Start SERVICE_AUTO_START

echo Iniciando...
"%NSSM%" start %SERVICIO%

echo.
echo ================= ESTADO =================
"%NSSM%" status %SERVICIO%
echo =========================================
echo   RUNNING = quedo. Abre http://localhost:5000
echo   Otra cosa = revisa %PROYECTO%\logs\error.log
pause
