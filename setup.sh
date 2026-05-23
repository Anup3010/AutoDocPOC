#!/bin/bash
# AutoDoc POC — One-Command Setup Script
# Usage: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        AutoDoc POC — Setup               ║"
echo "║  Automatic AI Documentation Generator   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ─── 1. Check Python ───────────────────────────
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "   Found: $python_version"

# ─── 2. Create virtual environment ─────────────
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "⚡ Activating virtual environment..."
source venv/bin/activate

# ─── 3. Install dependencies ───────────────────
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"

# ─── 4. Initialize git repo ────────────────────
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git config user.email "autodoc@example.com"
    git config user.name "AutoDoc Developer"
fi

# ─── 5. Install git hook ───────────────────────
echo "🪝  Installing git post-commit hook..."
cp hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
echo "   ✅ Hook installed at .git/hooks/post-commit"

# ─── 6. Create .env file ───────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "🔑 HuggingFace API Key Setup"
    echo "   Get your free key at: https://huggingface.co/settings/tokens"
    echo "   (Press Enter to skip and set it later)"
    read -p "   Enter HF_API_KEY: " hf_key
    if [ -n "$hf_key" ]; then
        echo "HF_API_KEY=$hf_key" > .env
        echo "   ✅ API key saved to .env"
    else
        echo "HF_API_KEY=hf_your_key_here" > .env
        echo "   ⚠️  Remember to edit .env and add your HuggingFace key!"
    fi
fi

# Load .env
set -a
source .env
set +a

# ─── 7. Create initial commit ──────────────────
echo ""
echo "📝 Creating initial commit to test the hook..."
mkdir -p generated_docs

git add .
git commit -m "feat: initial AutoDoc POC setup" 2>&1 | head -5

# ─── 8. Done ───────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ Setup complete!                       ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "🚀 Start the viewer:"
echo "   source venv/bin/activate"
echo "   python viewer/app.py"
echo "   → Open: http://localhost:5000"
echo ""
echo "🔧 Start the CRUD API (optional):"
echo "   uvicorn crud_app.main:app --reload --port 8000"
echo "   → Docs: http://localhost:8000/docs"
echo ""
echo "📝 Trigger documentation:"
echo "   # Make a code change, then:"
echo "   git add . && git commit -m 'your message'"
echo "   # → Docs auto-generate and appear at localhost:5000"
echo ""
echo "💡 To manually trigger doc generation:"
echo "   python -m doc_generator.generator ."
echo ""
