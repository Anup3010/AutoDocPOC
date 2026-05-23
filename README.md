# 📄 AutoDoc POC — Automatic AI Code Documentation

> Every git commit → AI reads your code → 2 documents generated automatically.
> No more stale wikis. No more KT sessions. PR reviews made easy.

---

## 🎯 What This Does

| Problem | AutoDoc Solution |
|---|---|
| New developer joins → needs 2-week KT | Get the latest Project Doc instantly |
| Senior dev reviews a PR blind | AI-generated Impact Analysis shows exactly what changed |
| Docs go stale after a week | Docs auto-update on every git commit |
| Manual documentation is tedious | Fully automated — zero extra effort from developers |

---

## 🗂️ Project Structure

```
autodoc-poc/
├── crud_app/                    ← 🐍 Sample FastAPI CRUD app (the project being documented)
│   ├── main.py                  ←   FastAPI app + router registration
│   ├── models/
│   │   ├── user.py              ←   Pydantic User models
│   │   └── item.py              ←   Pydantic Item models
│   ├── services/
│   │   ├── user_service.py      ←   User business logic (CRUD + validation)
│   │   ├── item_service.py      ←   Item business logic
│   │   └── db_service.py        ←   In-memory database
│   └── api/
│       ├── users.py             ←   /api/users endpoints
│       └── items.py             ←   /api/items endpoints
│
├── doc_generator/               ← 🤖 AI Documentation Engine
│   ├── generator.py             ←   MAIN: Orchestrates all doc generation
│   ├── git_utils.py             ←   Git commit info, diffs, changed files
│   └── code_parser.py           ←   Python AST parser (classes, methods, routes)
│
├── viewer/                      ← 🌐 Web UI to view & download docs
│   ├── app.py                   ←   Flask app
│   └── templates/
│       ├── index.html           ←   Session list with token usage
│       └── doc_view.html        ←   Document preview page
│
├── hooks/
│   └── post-commit              ← 🪝 Git hook (auto-triggers on commit)
│
├── generated_docs/              ← 📁 All generated docs saved here
│   ├── project_doc_*.md/docx/pdf
│   ├── pr_analysis_*.md/docx/pdf
│   └── meta_*.json              ←   Token usage + file paths metadata
│
├── requirements.txt
├── setup.sh                     ← ⚡ One-command setup
└── README.md
```

---

## ⚡ Quick Start

### 1. Get a HuggingFace API Key (Free)
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token (Read access is enough)
3. Copy it — looks like `hf_xxxxxxxxxxxxxxxxxxxxxx`

### 2. Install & Setup
```bash
# Clone / download this project, then:
bash setup.sh
# → Installs deps, installs git hook, prompts for HF key
```

### 3. Start the Viewer
```bash
source venv/bin/activate
python viewer/app.py
# → Open http://localhost:5000
```

### 4. Make a Change & Commit
```bash
# Edit any file in crud_app/ (e.g., add a new method to user_service.py)
git add .
git commit -m "feat: add user search by name endpoint"
# → Docs auto-generate! Refresh http://localhost:5000
```

---

## 📊 Two Documents Generated Per Commit

### Document 1: Full Project Documentation
Updated on every commit. Includes:
- **Project Overview** — What the app does
- **Architecture** — How it's structured
- **API Reference** — All endpoints with parameters
- **Data Models** — All Pydantic models
- **Service Layer** — Business logic explained
- **Business Rules** — Validation rules
- **Getting Started** — How to run it

**Who reads it:** New developers joining the team

### Document 2: PR Impact Analysis
Specific to each commit. Includes:
- **What Changed** — Plain English summary
- **Impact Analysis** — What other code is affected
- **Breaking Changes** — Any API contract changes
- **Risk Assessment** — Low / Medium / High
- **Reviewer Checklist** — Specific items to verify
- **Recommendation** — Approve / Request Changes

**Who reads it:** Senior developer reviewing the PR

---

## 🤖 HuggingFace Model

Default model: `mistralai/Mistral-7B-Instruct-v0.3`

To change the model, edit `doc_generator/generator.py`:
```python
HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"        # Alternative 1
HF_MODEL = "microsoft/Phi-3-mini-4k-instruct"     # Alternative 2 (faster)
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"     # Alternative 3 (better quality)
```

---

## 💰 Token Usage & Cost Tracking

The viewer shows for every generation:
- **Input tokens** (your code + prompts sent to AI)
- **Output tokens** (AI-generated documentation)  
- **Total tokens**
- **Estimated cost** (HuggingFace free tier = $0, Pro = ~$0.0004/1K tokens)

Token counts are estimated at ~4 chars/token (industry standard approximation).
Exact counts vary by tokenizer — treat as ballpark for POC cost planning.

---

## 🔧 Manual Trigger (without git commit)

```bash
source venv/bin/activate
export HF_API_KEY=hf_your_key
python -m doc_generator.generator .
```

---

## 🌐 Running the CRUD API

The sample app runs independently:
```bash
source venv/bin/activate
uvicorn crud_app.main:app --reload --port 8000
# → API docs: http://localhost:8000/docs
# → API root: http://localhost:8000/api/users
```

---

## 🔮 Extending to .NET / Java

The `doc_generator/` module is language-agnostic at the AI layer. To support .NET or Java:

1. **Replace `code_parser.py`** — Use Roslyn (C#) or JavaParser instead of Python AST
2. **Keep `git_utils.py` as-is** — Git diff works the same for all languages
3. **Keep `generator.py` as-is** — The HuggingFace prompts are language-agnostic
4. **Change file extension filter** in `git_utils.py`:
   ```python
   extensions = [".cs"]     # C# / .NET
   extensions = [".java"]   # Java
   ```

For .NET/Java parsing, consider calling CLI tools from Python:
- **C#**: `dotnet-script` or Roslyn scripting API
- **Java**: `javalang` Python library, or call `javap` CLI

---

## ❓ Troubleshooting

| Issue | Fix |
|---|---|
| `HF_API_KEY not set` | `export HF_API_KEY=hf_...` or edit `.env` |
| Model loading (503 error) | Free tier models sleep — script auto-retries after 20s |
| Hook not running | `chmod +x .git/hooks/post-commit` |
| No Python files detected | Ensure you're committing `.py` files |
| Viewer shows no sessions | Run `python -m doc_generator.generator .` manually first |

---

## 📋 License

POC / Educational use. Free to adapt for your team.
