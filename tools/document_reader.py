import os
from typing import Optional


class DocumentReaderTool:
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html", ".pdf"}

    def read_file(self, filepath: str, max_chars: int = 100000) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS and ext != ".pdf":
            return f"Unsupported file type: {ext}"

        try:
            if ext == ".pdf":
                return self._read_pdf(filepath, max_chars)
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(max_chars)
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    def _read_pdf(self, filepath: str, max_chars: int) -> str:
        try:
            import pdfminer.high_level

            text = pdfminer.high_level.extract_text(filepath)
            return text[:max_chars]
        except ImportError:
            return "PDF support requires pdfminer.six: pip install pdfminer.six"
        except Exception as e:
            return f"Error reading PDF: {e}"

    def read_directory(self, dirpath: str, pattern: str = "") -> dict:
        files = {}
        for root, _, filenames in os.walk(dirpath):
            for f in filenames:
                if pattern and pattern not in f:
                    continue
                ext = os.path.splitext(f)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    filepath = os.path.join(root, f)
                    files[f] = self.read_file(filepath)
        return files
