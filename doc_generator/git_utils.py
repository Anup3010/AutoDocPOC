"""
Git Utilities Module
Extracts git commit information, diffs, and file change analysis.
"""

import subprocess
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class CommitInfo:
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    branch: str


@dataclass
class FileChange:
    path: str
    status: str  # A=Added, M=Modified, D=Deleted, R=Renamed
    additions: int
    deletions: int
    diff: str
    file_type: str


@dataclass
class GitDiffResult:
    commit: CommitInfo
    changed_files: List[FileChange]
    total_additions: int
    total_deletions: int
    summary: str


def run_git(args: List[str], cwd: str = ".") -> Tuple[str, str, int]:
    """Run a git command and return stdout, stderr, returncode."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Git command timed out", 1
    except FileNotFoundError:
        return "", "Git not found in PATH", 1


def get_current_commit_info(repo_path: str = ".") -> Optional[CommitInfo]:
    """Get information about the latest commit."""
    format_str = "%H|%h|%an|%ae|%ci|%s"
    stdout, stderr, code = run_git(
        ["log", "-1", f"--format={format_str}"], cwd=repo_path
    )
    if code != 0 or not stdout:
        return None

    parts = stdout.split("|", 5)
    if len(parts) < 6:
        return None

    branch_out, _, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)

    return CommitInfo(
        hash=parts[0],
        short_hash=parts[1],
        author=parts[2],
        email=parts[3],
        date=parts[4],
        message=parts[5],
        branch=branch_out or "unknown"
    )


def get_diff_for_commit(repo_path: str = ".", commit_hash: str = "HEAD") -> List[FileChange]:
    """Get the file changes for a specific commit."""
    # Get list of changed files with status
    stdout, _, code = run_git(
        ["diff-tree", "--no-commit-id", "-r", "--name-status", commit_hash],
        cwd=repo_path
    )
    if code != 0:
        # Might be first commit
        stdout, _, code = run_git(
            ["show", "--name-status", "--format=", commit_hash],
            cwd=repo_path
        )

    changed_files = []
    file_statuses = {}

    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, filepath = parts[0].strip(), parts[1].strip()
            file_statuses[filepath] = status[0]  # First char: A, M, D, R

    # Get stats
    stats_out, _, _ = run_git(
        ["show", "--stat", "--format=", commit_hash],
        cwd=repo_path
    )

    file_stats = {}
    for line in stats_out.splitlines():
        match = re.match(r'\s*(.+?)\s+\|\s+(\d+)\s+([+-]+)', line)
        if match:
            filepath = match.group(1).strip()
            total = int(match.group(2))
            changes = match.group(3)
            additions = changes.count('+')
            deletions = changes.count('-')
            file_stats[filepath] = (additions, deletions)

    # Get full diffs per file
    for filepath, status in file_statuses.items():
        if not filepath.endswith('.py'):
            continue  # Focus on Python files for this POC

        diff_out, _, _ = run_git(
            ["show", commit_hash, "--", filepath],
            cwd=repo_path
        )

        stats = file_stats.get(filepath, (0, 0))
        ext = os.path.splitext(filepath)[1].lstrip('.')

        changed_files.append(FileChange(
            path=filepath,
            status=status,
            additions=stats[0],
            deletions=stats[1],
            diff=diff_out[:3000],  # Limit diff size
            file_type=ext or "unknown"
        ))

    return changed_files


def get_full_project_code(repo_path: str = ".", extensions: List[str] = None) -> Dict[str, str]:
    """Read all source files in the project."""
    if extensions is None:
        extensions = [".py"]

    ignore_dirs = {".git", "__pycache__", "venv", "env", ".venv", "node_modules",
                   "generated_docs", ".mypy_cache", ".pytest_cache"}
    ignore_files = {"setup.py", "conftest.py"}

    project_code = {}

    for root, dirs, files in os.walk(repo_path):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            if any(filename.endswith(ext) for ext in extensions):
                if filename in ignore_files:
                    continue
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, repo_path)

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    project_code[rel_path] = content
                except Exception:
                    pass

    return project_code


def build_diff_result(repo_path: str = ".") -> Optional[GitDiffResult]:
    """Build a complete diff result for the latest commit."""
    commit = get_current_commit_info(repo_path)
    if not commit:
        return None

    changed_files = get_diff_for_commit(repo_path, commit.hash)
    total_add = sum(f.additions for f in changed_files)
    total_del = sum(f.deletions for f in changed_files)

    status_map = {"A": "Added", "M": "Modified", "D": "Deleted", "R": "Renamed"}
    summary_parts = []
    for f in changed_files:
        status_label = status_map.get(f.status, f.status)
        summary_parts.append(f"{status_label}: {f.path} (+{f.additions}/-{f.deletions})")

    summary = "; ".join(summary_parts) if summary_parts else "No Python files changed"

    return GitDiffResult(
        commit=commit,
        changed_files=changed_files,
        total_additions=total_add,
        total_deletions=total_del,
        summary=summary
    )
