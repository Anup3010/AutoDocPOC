"""
Python Code Parser
Uses AST (Abstract Syntax Tree) to extract structured information
from Python source files without executing them.
"""

import ast
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    return_annotation: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    line_number: int
    is_async: bool = False
    raises: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    docstring: Optional[str]
    methods: List[FunctionInfo]
    line_number: int


@dataclass
class ModuleInfo:
    file_path: str
    module_docstring: Optional[str]
    imports: List[str]
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    global_variables: List[str]


def get_docstring(node: ast.AST) -> Optional[str]:
    """Extract docstring from a class or function node."""
    if (isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
        return node.body[0].value.value.strip()
    return None


def get_annotation_str(annotation) -> Optional[str]:
    """Convert AST annotation to string."""
    if annotation is None:
        return None
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return f"{annotation.value.id}.{annotation.attr}"
    if isinstance(annotation, ast.Subscript):
        return ast.unparse(annotation)
    try:
        return ast.unparse(annotation)
    except Exception:
        return str(annotation)


def parse_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
    """Extract detailed info from a function/method definition."""
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {get_annotation_str(arg.annotation)}"
        args.append(arg_str)

    # Varargs
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")

    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(f"@{dec.id}")
        elif isinstance(dec, ast.Attribute):
            decorators.append(f"@{dec.value.id}.{dec.attr}")
        elif isinstance(dec, ast.Call):
            try:
                decorators.append(f"@{ast.unparse(dec)}")
            except Exception:
                decorators.append("@<decorator>")

    # Find raises
    raises = []
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc:
            if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                raises.append(child.exc.func.id)
            elif isinstance(child.exc, ast.Name):
                raises.append(child.exc.id)

    return FunctionInfo(
        name=node.name,
        args=args,
        return_annotation=get_annotation_str(node.returns),
        docstring=get_docstring(node),
        decorators=decorators,
        line_number=node.lineno,
        is_async=isinstance(node, ast.AsyncFunctionDef),
        raises=list(set(raises))
    )


def parse_file(file_path: str, content: str) -> Optional[ModuleInfo]:
    """Parse a Python file and extract structural information."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    module_docstring = get_docstring(tree)
    imports = []
    classes = []
    functions = []
    global_vars = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            imports.append(f"{module}.{','.join(names)}")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [get_annotation_str(b) or "object" for b in node.bases]
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(parse_function(item))
            classes.append(ClassInfo(
                name=node.name,
                bases=bases,
                docstring=get_docstring(node),
                methods=methods,
                line_number=node.lineno
            ))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(parse_function(node))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    global_vars.append(target.id)

    return ModuleInfo(
        file_path=file_path,
        module_docstring=module_docstring,
        imports=list(set(imports))[:20],  # Limit to 20
        classes=classes,
        functions=functions,
        global_variables=global_vars
    )


def parse_project(project_code: Dict[str, str]) -> Dict[str, ModuleInfo]:
    """Parse all Python files in a project."""
    parsed = {}
    for file_path, content in project_code.items():
        info = parse_file(file_path, content)
        if info:
            parsed[file_path] = info
    return parsed


def format_module_summary(module: ModuleInfo) -> str:
    """Create a text summary of a module for AI prompt consumption."""
    lines = [f"FILE: {module.file_path}"]
    if module.module_docstring:
        lines.append(f"  Docstring: {module.module_docstring[:200]}")

    if module.classes:
        lines.append(f"  Classes ({len(module.classes)}):")
        for cls in module.classes:
            lines.append(f"    - {cls.name}(bases: {', '.join(cls.bases) or 'object'})")
            if cls.docstring:
                lines.append(f"      {cls.docstring[:150]}")
            for method in cls.methods[:10]:
                prefix = "async " if method.is_async else ""
                args_str = ", ".join(method.args[:5])
                ret = f" -> {method.return_annotation}" if method.return_annotation else ""
                lines.append(f"      {prefix}def {method.name}({args_str}){ret}")
                if method.docstring:
                    lines.append(f"        '{method.docstring[:100]}'")

    if module.functions:
        lines.append(f"  Module-level functions ({len(module.functions)}):")
        for func in module.functions[:8]:
            args_str = ", ".join(func.args[:5])
            ret = f" -> {func.return_annotation}" if func.return_annotation else ""
            lines.append(f"    - def {func.name}({args_str}){ret}")

    return "\n".join(lines)
