"""
AutoDoc Viewer
A beautiful Flask web application to view, preview, and download generated documentation.
"""

import os
import json
import glob
from pathlib import Path
from flask import Flask, render_template, send_file, jsonify, abort, request
import markdown2

app = Flask(__name__)

DOCS_DIR = os.environ.get("AUTODOC_OUTPUT_DIR", "generated_docs")


def get_all_doc_sessions():
    """Read all metadata JSON files and return sorted sessions."""
    meta_files = sorted(
        glob.glob(os.path.join(DOCS_DIR, "meta_*.json")),
        reverse=True  # Newest first
    )
    sessions = []
    for mf in meta_files:
        try:
            with open(mf) as f:
                data = json.load(f)
            data["meta_file"] = mf
            sessions.append(data)
        except Exception:
            pass
    return sessions


def read_markdown_file(filepath: str) -> str:
    """Read and convert a markdown file to HTML."""
    if not filepath or not os.path.exists(filepath):
        return "<p class='error'>Document not found.</p>"
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        html = markdown2.markdown(
            content,
            extras=["tables", "fenced-code-blocks", "header-ids", "strike", "task_list"]
        )
        return html
    except Exception as e:
        return f"<p class='error'>Error reading document: {str(e)}</p>"


@app.route("/")
def index():
    sessions = get_all_doc_sessions()
    return render_template("index.html", sessions=sessions, docs_dir=DOCS_DIR)


@app.route("/view/<doc_type>/<timestamp>")
def view_doc(doc_type, timestamp):
    """View a document as HTML."""
    sessions = get_all_doc_sessions()
    session = next((s for s in sessions if s.get("timestamp") == timestamp), None)
    if not session:
        abort(404)

    if doc_type == "full":
        filepath = session["files"]["full_doc_md"]
        title = "Project Documentation"
        doc_label = "full_doc"
    elif doc_type == "pr":
        filepath = session["files"]["pr_doc_md"]
        title = f"PR Impact Analysis — {session['commit']['short_hash']}"
        doc_label = "pr_doc"
    else:
        abort(400)

    html_content = read_markdown_file(filepath)
    return render_template(
        "doc_view.html",
        title=title,
        html_content=html_content,
        session=session,
        doc_type=doc_type,
        timestamp=timestamp
    )


@app.route("/download/<doc_type>/<format>/<timestamp>")
def download_doc(doc_type, format, timestamp):
    """Download a document in word or pdf format."""
    sessions = get_all_doc_sessions()
    session = next((s for s in sessions if s.get("timestamp") == timestamp), None)
    if not session:
        abort(404)

    key_map = {
        ("full", "docx"): "full_doc_docx",
        ("full", "pdf"): "full_doc_pdf",
        ("full", "md"): "full_doc_md",
        ("pr", "docx"): "pr_doc_docx",
        ("pr", "pdf"): "pr_doc_pdf",
        ("pr", "md"): "pr_doc_md",
    }

    file_key = key_map.get((doc_type, format))
    if not file_key:
        abort(400)

    filepath = session["files"].get(file_key)
    if not filepath:
        abort(404)

    # Try the specific format, fallback to txt
    if not os.path.exists(filepath):
        alt = filepath.replace(f".{format}", ".txt")
        if os.path.exists(alt):
            filepath = alt

    if not os.path.exists(filepath):
        abort(404)

    commit_hash = session["commit"]["short_hash"]
    if doc_type == "full":
        filename = f"project_doc_{commit_hash}.{format}"
    else:
        filename = f"pr_analysis_{commit_hash}.{format}"

    abs_filepath = os.path.abspath(filepath)
    return send_file(abs_filepath, as_attachment=True, download_name=filename)


@app.route("/api/sessions")
def api_sessions():
    """JSON API for session list."""
    return jsonify(get_all_doc_sessions())


@app.route("/api/status")
def api_status():
    """Check if docs directory exists and has content."""
    sessions = get_all_doc_sessions()
    return jsonify({
        "docs_dir": DOCS_DIR,
        "docs_dir_exists": os.path.isdir(DOCS_DIR),
        "session_count": len(sessions),
        "latest_commit": sessions[0]["commit"]["short_hash"] if sessions else None
    })


if __name__ == "__main__":
    os.makedirs(DOCS_DIR, exist_ok=True)
    print(f"🚀 AutoDoc Viewer starting at http://localhost:5000")
    print(f"📁 Looking for docs in: {os.path.abspath(DOCS_DIR)}")
    app.run(debug=True, port=5000)
