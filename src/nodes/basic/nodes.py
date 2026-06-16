from pydantic import BaseModel
from src.lib.flow import Node, register_node


class TextInput(BaseModel):
    text: str


class LengthOutput(BaseModel):
    length: int


@register_node("len")
class LenNode(Node):
    def run(self, context):
        text = context.get("text", "")
        context["length"] = len(text)
        return context

    def schema(self):
        return {
            "in": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            "out": {
                "type": "object",
                "properties": {"length": {"type": "integer"}},
            },
        }


@register_node("inc")
class IncNode(Node):
    def run(self, context):
        length = context.get("length", 0)
        context["length"] = length + 1
        return context

    def schema(self):
        return {
            "in": {
                "type": "object",
                "properties": {"length": {"type": "integer"}},
                "required": ["length"],
            },
            "out": {
                "type": "object",
                "properties": {"length": {"type": "integer"}},
            },
        }
