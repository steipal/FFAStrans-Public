@echo off
set "SCRIPT_DIR=%~dp0"
set API_PORT=8081
echo Starting FFAStrans API...
"%SCRIPT_DIR%node\node.exe" "%SCRIPT_DIR%server.js"
pause