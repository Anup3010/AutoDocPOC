@echo off
if exist "%~dp0..\..\..\.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0..\..\..\.env") do (
        if "%%A"=="GEMINI_API_KEY" set GEMINI_API_KEY=%%B
    )
)
if "%GEMINI_API_KEY%"=="" (
    echo [AutoDoc] WARNING: GEMINI_API_KEY not set. Skipping.
    exit /b 0
)
echo [AutoDoc] Merge detected - generating full documentation...
set AUTODOC_MODE=both
set REPO_ROOT=%~dp0..\..
set PYTHONPATH=%REPO_ROOT%
"C:/Users/anup.shembade/AppData/Local/Programs/Python/Python313/python.exe" -m doc_generator.generator "%REPO_ROOT%"
if %errorlevel% equ 0 (
    echo [AutoDoc] Done! http://localhost:5000
) else (
    echo [AutoDoc] Had errors.
)
exit /b 0