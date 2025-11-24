@echo off
REM write_env.bat - Windows wrapper for scripts/write_env.py
REM Usage: write_env.bat "gems_hub:YOUR_KEY" or write_env.bat
REM If not provided, you will be prompted for a key.

setlocal enabledelayedexpansion
set "KEY=%~1"
if "%KEY%"=="" (
    set /p KEY=Enter GEMDB API key (e.g. gems_hub:KEY): 
)

REM find python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python was not found in PATH. Please install Python or add it to PATH.
        exit /b 1
    ) else (
        set "PYEXEC=py"
    )
) else (
    set "PYEXEC=python"
)

REM Determine script path and run
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%write_env.py
if exist "%SCRIPT_PATH%" (
    "%PYEXEC%" "%SCRIPT_PATH%" --key "%KEY%"
    exit /b %ERRORLEVEL%
) else (
    echo write_env.py not found in %SCRIPT_DIR%
    exit /b 1
)

endlocal
