from src.lib.node import Node
from pydantic import BaseModel


class LoadDocInput(BaseModel):
    doc_path: str


class LoadDocOutput(BaseModel):
    content: str


class LoadDocNode(Node):
    def prep(self, input_ctx: LoadDocInput):
        doc_path = input_ctx.doc_path
        return {"doc_path": doc_path}
    
    def exec(self, prep_output):
        doc_path = prep_output["doc_path"]
        with open(doc_path, "r") as f:
            content = f.read()
        return {"content": content}
    
    def post(self, input_ctx: LoadDocInput, exec_output):
        content = exec_output.get("content", "")
        return LoadDocOutput(content=content)
 