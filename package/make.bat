@echo off

REM Set the QT_PREFERRED_BINDING_JSON environment variable
set "QT_PREFERRED_BINDING_JSON={"tik_manager4.ui.Qt": ["PySide2"], "default":["PySide2"]}"

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
) ELSE IF "%ARG%"=="testrelease" (
    python release_package.py --testrelease
) ELSE IF "%ARG%"=="debug" (
    python release_package.py --debug
) ELSE IF "%ARG%"=="build" (
    python release_package.py --build
) ELSE IF "%ARG%"=="package" (
    python release_package.py --package
) ELSE IF "%ARG%"=="clean" (
    REM Remove the build folder
    rmdir /s /q build
) ELSE IF "%ARG%"=="help" (
    REM Display help message
    echo Available commands:
    echo - release: Create the executable file
    echo - testrelease: To hand out the executable to testers
    echo - debug: Create the executables with debug specs
    echo - build: Freeze and generate sanitized release notes (pre-signing step)
    echo - package: Package the signed EXEs into installer
    echo - clean: Remove the build folder
    echo - help: Display this help message
) ELSE (
    REM Invalid argument, display error message
    echo Invalid argument. Use 'release', 'debug', 'testrelease', 'build', 'package', 'clean', or 'help'.
)
