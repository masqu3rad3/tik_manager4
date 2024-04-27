@echo off

SET "SCRIPT_DIR=%~dp0"
set "TARGET_DIR=%SCRIPT_DIR%..\..\..\"

echo %TARGET_DIR%
echo %SCRIPT_DIR%

set PYTHONPATH=%PYTHONPATH%;%TARGET_DIR%

Rem run the standalone script from the script directory
python %SCRIPT_DIR%\tik4_standalone.py

pause