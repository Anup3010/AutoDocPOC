@echo off
REM AutoDoc Windows Git Hook — post-commit.bat

REM Load .env file if it exists
if exist "%~dp0..\..\..env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0..\..\..env") do (
        if "%%A"=="HF_API_KEY" set HF_API_KEY=%%B
    )
)

REM Check key is set
if "%HF_API_KEY%"=="" (
    echo.
    echo [AutoDoc] WARNING: HF_API_KEY not set. Skipping doc generation.
    echo [AutoDoc] Add HF_API_KEY=hf_your_key to your .env file
    exit /b 0
)

echo.
echo [AutoDoc] Generating documentation for this commit...

REM .git\hooks\ -> up 2 levels -> project root
set REPO_ROOT=%~dp0..\..
set PYTHONPATH=%REPO_ROOT%

REM Run the generator
"C:\Users\anup.shembade\AppData\Local\Programs\Python\Python313\python.exe" -m doc_generator.generator "%REPO_ROOT%"

if %errorlevel% equ 0 (
    echo [AutoDoc] Documentation updated! View at: http://localhost:5000
) else (
    echo [AutoDoc] Documentation generation had errors. Check output above.
)

exit /b 0