from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


@dataclass
class CodeChunk:
    """A semantic unit of code (function, class, or method)."""
    content: str
    chunk_type: str
    file_path: str
    start_line: int
    end_line: int
    name: str
    parent_class: Optional[str] = None
    docstring: Optional[str] = None
    calls: list[str] = field(default_factory=list)


class Chunker:
    """Parse Python files into semantic chunks using AST."""
    
    SKIP_PATTERNS = {
        "__pycache__", ".git", "venv", ".venv", "env", ".env",
        "node_modules", ".tox", ".pytest_cache", "dist", "build", "egg-info",
    }
    
    def __init__(self):
        self.parser = Parser(Language(tspython.language()))
    
    def chunk_repo(self, repo_path: Path) -> list[CodeChunk]:
        """Walk repo and chunk all Python files."""
        all_chunks = []
        
        for py_file in repo_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue
            
            try:
                content = py_file.read_text()
                rel_path = str(py_file.relative_to(repo_path))
                chunks = self._chunk_file(rel_path, content)
                all_chunks.extend(chunks)
            except Exception:
                continue
        
        return all_chunks
    
    def _should_skip(self, path: Path) -> bool:
        return any(skip in path.parts for skip in self.SKIP_PATTERNS)
    
    def _chunk_file(self, file_path: str, content: str) -> list[CodeChunk]:
        try:
            tree = self.parser.parse(bytes(content, "utf-8"))
        except Exception:
            return []
        
        chunks = []
        self._walk_node(tree.root_node, content, file_path, chunks)
        return chunks
    
    def _walk_node(self, node, content: str, file_path: str, chunks: list, parent_class: str = None):
        if node.type == "function_definition":
            chunks.append(self._extract_function(node, content, file_path, parent_class))
        
        elif node.type == "class_definition":
            class_name = self._get_node_name(node)
            chunks.append(self._extract_class(node, content, file_path))
            
            for child in node.children:
                if child.type == "block":
                    for stmt in child.children:
                        self._walk_node(stmt, content, file_path, chunks, class_name)
            return
        
        for child in node.children:
            self._walk_node(child, content, file_path, chunks, parent_class)
    
    def _extract_function(self, node, content: str, file_path: str, parent_class: str) -> CodeChunk:
        name = self._get_node_name(node)
        func_content = content[node.start_byte:node.end_byte]
        
        return CodeChunk(
            content=func_content,
            chunk_type="method" if parent_class else "function",
            file_path=file_path,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            name=name,
            parent_class=parent_class,
            docstring=self._extract_docstring(node, content),
            calls=self._extract_calls(node)
        )
    
    def _extract_class(self, node, content: str, file_path: str) -> CodeChunk:
        name = self._get_node_name(node)
        class_content = content[node.start_byte:node.end_byte]
        lines = class_content.split("\n")
        
        header_lines = []
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped = line.strip()
            
            if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                docstring_char = stripped[:3]
                in_docstring = True
                header_lines.append(line)
                if stripped.count(docstring_char) >= 2:
                    in_docstring = False
                continue
            
            if in_docstring:
                header_lines.append(line)
                if docstring_char in stripped:
                    in_docstring = False
                continue
            
            if stripped.startswith("def "):
                break
            
            header_lines.append(line)
        
        return CodeChunk(
            content="\n".join(header_lines),
            chunk_type="class",
            file_path=file_path,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            name=name,
            docstring=self._extract_docstring(node, content)
        )
    
    def _get_node_name(self, node) -> str:
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode()
        return "unknown"
    
    def _extract_docstring(self, node, content: str) -> Optional[str]:
        for child in node.children:
            if child.type == "block":
                for stmt in child.children:
                    if stmt.type == "expression_statement":
                        for expr in stmt.children:
                            if expr.type == "string":
                                doc = expr.text.decode().strip("\"'").strip()
                                return doc[:300] if len(doc) > 300 else doc
        return None
    
    def _extract_calls(self, node) -> list[str]:
        calls = []
        self._find_calls(node, calls)
        return list(dict.fromkeys(calls))[:15]
    
    def _find_calls(self, node, calls: list):
        if node.type == "call":
            func = node.children[0] if node.children else None
            if func:
                if func.type == "identifier":
                    calls.append(func.text.decode())
                elif func.type == "attribute":
                    calls.append(func.text.decode())
        
        for child in node.children:
            self._find_calls(child, calls)