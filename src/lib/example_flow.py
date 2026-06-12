from src.lib.flow import Node, Flow
from pydantic import BaseModel


class TextIn(BaseModel):
    text: str


class LenOut(BaseModel):
    length: int


class LenNode(Node[TextIn, LenOut]):
    in_model = TextIn
    out_model = LenOut

    def run(self, data: TextIn) -> LenOut:
        return LenOut.model_validate({"length": len(data.text)})


class IncNode(Node[LenOut, LenOut]):
    in_model = LenOut
    out_model = LenOut

    def run(self, data: LenOut) -> LenOut:
        return LenOut.model_validate({"length": data.length + 1})


def demo():
    flow = Flow()
    # register nodes
    idx_len = flow.add(LenNode())
    idx_inc = flow.add(IncNode())
    # echo: returns same LenOut
    class EchoNode(Node[LenOut, LenOut]):
        in_model = LenOut
        out_model = LenOut

        def run(self, data: LenOut) -> LenOut:
            return data

    idx_echo = flow.add(EchoNode())

    # conditional transitions: if length >= 10 -> increment, else -> echo
    flow.connect(idx_len, idx_inc, lambda out: out.length >= 10)
    flow.connect(idx_len, idx_echo, lambda out: out.length < 10)

    return flow.run({"text": "hello elliott and julia"})


if __name__ == "__main__":
    print(demo())
