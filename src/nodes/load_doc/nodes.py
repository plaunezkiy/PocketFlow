from pathlib import Path
from pydantic import BaseModel
from src.lib.flow import Node, register_node


class LoadDocInput(BaseModel):
    doc_path: str


class LoadDocOutput(BaseModel):
    content: str


@register_node("load_doc")
class LoadDocNode(Node):
    def run(self, context):
        doc_path = context.get("doc_path")
        if not doc_path:
            raise ValueError("doc_path is required in context")

        file_path = Path(doc_path)
        with file_path.open("r", encoding="utf-8") as f:
            context["content"] = f.read()

        return context

    def schema(self):
        return {
            "in": {
                "type": "object",
                "properties": {"doc_path": {"type": "string"}},
                "required": ["doc_path"],
            },
            "out": {
                "type": "object",
                "properties": {"content": {"type": "string"}},
            },
        }
