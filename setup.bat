@echo off
REM AutoDoc POC — Windows Setup Script
REM Run this from: Command Prompt or PowerShell

echo.
echo ==========================================
echo   AutoDoc POC — Windows Setup
echo   Automatic AI Documentation Generator
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo Found: %%i

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo    Dependencies installed

REM Init git if needed
if not exist ".git" (
    echo Initializing git repository...
    git init
    git config user.email "autodoc@example.com"
    git config user.name "AutoDoc Developer"
)

REM Install git hook (Windows version)
echo Installing git hook...
copy /Y hooks\post-commit.bat .git\hooks\post-commit.bat >nul
copy /Y hooks\post-commit     .git\hooks\post-commit     >nul
echo    Hook installed

REM Set API key
if not exist ".env" (
    echo.
    echo HuggingFace API Key Setup
    echo Get your free key at: https://huggingface.co/settings/tokens
    set /p HF_KEY="Enter HF_API_KEY (or press Enter to skip): "
    if not "!HF_KEY!"=="" (
        echo HF_API_KEY=!HF_KEY! > .env
        echo    API key saved to .env
    ) else (
        echo HF_API_KEY=hf_your_key_here > .env
        echo    Remember to edit .env and add your HuggingFace key!
    )
)

REM Make initial commit
echo.
echo Making initial commit...
mkdir generated_docs 2>nul
git add .
git commit -m "feat: initial AutoDoc POC setup"

echo.
echo ==========================================
echo   Setup complete!
echo ==========================================
echo.
echo Start the viewer:
echo   venv\Scripts\activate
echo   python viewer\app.py
echo   Open: http://localhost:5000
echo.
echo Start the CRUD API (optional):
echo   uvicorn crud_app.main:app --reload --port 8000
echo   Open: http://localhost:8000/docs
echo.
echo Trigger documentation:
echo   Make a code change, then:
echo   git add . ^&^& git commit -m "your message"
echo.
pause
