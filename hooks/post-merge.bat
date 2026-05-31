@echo off
REM AutoDoc Post-Merge Hook — Windows
REM Fires when any branch is merged

REM Load .env file
if exist "%~dp0..\..\..\.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0..\..\..\.env") do (
        if "%%A"=="GEMINI_API_KEY" set GEMINI_API_KEY=%%B
    )
)

REM Check key is set
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo [AutoDoc] WARNING: GEMINI_API_KEY not set. Skipping.
    echo [AutoDoc] Add GEMINI_API_KEY=your_key to .env file
    exit /b 0
)

echo.
echo [AutoDoc] Merge detected - generating full documentation...

REM Always both on merge
set AUTODOC_MODE=both
set REPO_ROOT=%~dp0..\..
set PYTHONPATH=%REPO_ROOT%

REM Run generator
"C:/Users/anup.shembade/AppData/Local/Programs/Python/Python313/python.exe" -m doc_generator.generator "%REPO_ROOT%"

if %errorlevel% equ 0 (
    echo [AutoDoc] Done! View at: http://localhost:5000
) else (
    echo [AutoDoc] Generation had errors.
)

exit /b 0