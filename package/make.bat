@echo off

REM This batch file will execute release_package.py with specified arguments.

REM Get the directory of make.bat
SET "SCRIPT_DIR=%~dp0"

REM Add the parent directory of make.bat to the Python path
SET "PYTHONPATH=%SCRIPT_DIR%..;%PYTHONPATH%"

REM Check if no argument is provided, default to 'release'
IF "%1"=="" (
    SET "ARG=release"
) ELSE (
    SET "ARG=%1"
)

REM Execute commands based on the argument
IF "%ARG%"=="release" (
    python release_package.py
) ELSE IF "%ARG%"=="clean" (
    REM Remove the build folder
    rmdir /s /q build
) ELSE IF "%ARG%"=="help" (
    REM Display help message
    echo Available commands:
    echo - release: Create the executable file
    echo - clean: Remove the build folder
    echo - help: Display this help message
) ELSE (
    REM Invalid argument, display error message
    echo Invalid argument. Use 'release', 'clean', or 'help'.
)

REM Add any additional commands if needed
