from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
from pathlib import Path

from src.lib.example_flow import LenNode, IncNode, LoadDocNode

app = FastAPI(title="Flow UI")

# mount static frontend using path relative to this file
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.get("/")
async def root():
    return FileResponse(static_dir / "index.html")

# register available nodes here
_NODES: Dict[str, Any] = {
    "len": LenNode(),
    "inc": IncNode(),
    "load_doc": LoadDocNode(),
}


class FlowRunRequest(BaseModel):
    nodes: list[str]
    payload: Dict[str, Any] = {}


@app.get("/nodes")
def list_nodes():
    return list(_NODES.keys())


@app.get("/schema/{name}")
def node_schema(name: str):
    node = _NODES.get(name)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    in_schema = node.in_model.model_json_schema()
    out_schema = node.out_model.model_json_schema()
    return {"in": in_schema, "out": out_schema}


@app.post("/run/{name}")
def run_node(name: str, payload: Dict[str, Any]):
    node = _NODES.get(name)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    try:
        in_obj = node.in_model.model_validate(payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    out_obj = node.run(in_obj)
    return JSONResponse(content=out_obj.model_dump())


@app.post("/flow/run")
def run_flow(body: FlowRunRequest):
    current = body.payload
    steps = []
    for name in body.nodes:
        node = _NODES.get(name)
        if not node:
            raise HTTPException(status_code=404, detail={"node": name, "message": "node not found"})
        try:
            in_obj = node.in_model.model_validate(current)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail={"node": name, "errors": e.errors()})
        out_obj = node.run(in_obj)
        current = out_obj.model_dump()
        steps.append({"node": name, "output": current})
    return {"output": current, "steps": steps}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app.frontend:app", host="127.0.0.1", port=8000, reload=True)
