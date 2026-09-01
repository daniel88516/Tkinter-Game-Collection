@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_game.ps1"
set "BUILD_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%BUILD_EXIT_CODE%"=="0" (
  echo Build finished successfully.
) else (
  echo Build failed. Review the error message above.
)
pause
exit /b %BUILD_EXIT_CODE%
