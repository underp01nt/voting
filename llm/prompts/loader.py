# def load_prompt(path: str) -> str:
#     with open(path, "r", encoding="utf-8") as md_file:
#         return md_file.read()

from pathlib import Path
def load_md(name: str) -> str:
    # "prompts/...""
    path = Path(__file__).parent / f"{name}.md"
    return path.read_text(encoding="utf-8")