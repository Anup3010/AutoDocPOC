# 🪟 Windows Setup Guide — AutoDoc POC

Complete guide for running AutoDoc POC on Windows.

---

## Prerequisites

Install these first (in order):

| Tool | Where to get | Why needed |
|---|---|---|
| Python 3.9+ | [python.org/downloads](https://python.org/downloads) | Runs everything |
| Git for Windows | [git-scm.com](https://git-scm.com/download/win) | Git + the commit hook |
| VS Code (optional) | [code.visualstudio.com](https://code.visualstudio.com) | Editing code |

**Important during Python install:** Check the box **"Add Python to PATH"**.

**Important during Git install:** Choose **"Git from the command line and also from 3rd-party software"** when asked about PATH.

---

## Step-by-Step Setup

Open **Command Prompt** (cmd) or **PowerShell** — all commands below work in both.

### 1. Extract the project
```cmd
REM Extract autodoc-poc.zip to a folder, then:
cd C:\path\to\autodoc-poc
```

### 2. Create virtual environment
```cmd
python -m venv venv
venv\Scripts\activate
```
Your prompt should now show `(venv)` at the start.

### 3. Install dependencies
```cmd
pip install -r requirements.txt
```

### 4. Initialize Git repository
```cmd
git init
git config user.email "you@example.com"
git config user.name "Your Name"
```

### 5. Install the Git hook (Windows requires TWO files)
```cmd
copy hooks\post-commit     .git\hooks\post-commit
copy hooks\post-commit.bat .git\hooks\post-commit.bat
```
> **Why two files?** Git for Windows first tries `post-commit.bat`, then falls back to `post-commit` (Python). Both are provided so it works in all Git for Windows configurations.

### 6. Set your HuggingFace API key
Create a `.env` file in the project root:
```cmd
echo HF_API_KEY=hf_your_actual_key_here > .env
```
Get a free key at: https://huggingface.co/settings/tokens

### 7. Make the first commit (this triggers doc generation)
```cmd
git add .
git commit -m "feat: initial AutoDoc POC setup"
```

You'll see:
```
[AutoDoc] Generating documentation for this commit...
[AutoDoc] Documentation updated! View at: http://localhost:5000
```

### 8. Start the viewer
```cmd
python viewer\app.py
```
Open: **http://localhost:5000**

---

## Running the CRUD API (optional)

Open a **second** Command Prompt:
```cmd
cd C:\path\to\autodoc-poc
venv\Scripts\activate
uvicorn crud_app.main:app --reload --port 8000
```
Open: **http://localhost:8000/docs** — Swagger UI

---

## How to Test It End-to-End on Windows

### Test 1: Basic API works
```cmd
REM With uvicorn running in another window:
curl http://localhost:8000/health
REM Expected: {"status":"healthy","version":"1.0.0"}

curl http://localhost:8000/api/users/
REM Expected: list of users
```

### Test 2: Trigger doc generation manually
```cmd
venv\Scripts\activate
set HF_API_KEY=hf_your_key_here
python -m doc_generator.generator .
```

### Test 3: Make a code change and commit
```cmd
REM Open crud_app\services\user_service.py and add a new method or comment
REM Then:
git add crud_app\services\user_service.py
git commit -m "feat: test change to trigger autodoc"
REM --> Watch the terminal for AutoDoc output
REM --> Refresh http://localhost:5000
```

---

## Troubleshooting (Windows-specific)

| Problem | Fix |
|---|---|
| `'python' is not recognized` | Re-install Python and check "Add to PATH" |
| `'git' is not recognized` | Re-install Git for Windows |
| Hook not firing after commit | See "Hook not running" section below |
| `ModuleNotFoundError` | Run `venv\Scripts\activate` first |
| `.env` key not loading | Make sure `.env` is in project root, not in a subfolder |
| Port 5000 blocked | Windows Defender may block it; allow it or use port 8001 |

### Hook not running after commit

**Option A** — Run doc generation manually after each commit:
```cmd
python -m doc_generator.generator .
```

**Option B** — Check which Git you have:
```cmd
git --version
where git
```
If it's Git for Windows (most common), the hook should work. If using WSL git or another variant, hooks behave differently.

**Option C** — Verify hook files exist:
```cmd
dir .git\hooks\
REM Should show: post-commit and post-commit.bat
```

**Option D** — Test the hook manually:
```cmd
python .git\hooks\post-commit
```

---

## Windows vs Mac/Linux — What's Different

| Feature | Mac/Linux | Windows |
|---|---|---|
| Setup script | `bash setup.sh` | `setup.bat` |
| Activate venv | `source venv/bin/activate` | `venv\Scripts\activate` |
| Git hook | `post-commit` (shebang) | `post-commit.bat` + `post-commit` |
| Set env var | `export HF_API_KEY=...` | `set HF_API_KEY=...` or `.env` file |
| Run commands | Forward slashes `/` | Backslashes `\` (Python handles internally) |
| File permissions | `chmod +x` needed | Not needed on Windows |

---

## Environment Variables in Windows

The `.env` file approach is the easiest on Windows. The hook automatically loads it.

Alternatively, set it for the current session:
```cmd
set HF_API_KEY=hf_your_key_here
```

Or permanently via System Properties:
1. Search "Environment Variables" in Start menu
2. Click "Environment Variables..."
3. Under "User variables" → New
4. Variable: `HF_API_KEY` / Value: `hf_your_key...`
