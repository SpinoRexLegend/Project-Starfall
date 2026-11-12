@echo off
setlocal

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Starfall.ps1" %*
set "STARFALL_EXIT_CODE=%ERRORLEVEL%"

if not "%STARFALL_EXIT_CODE%"=="0" (
    echo.
    echo Starfall did not start. Review the message above, then press any key to close.
    pause >nul
)

exit /b %STARFALL_EXIT_CODE%
