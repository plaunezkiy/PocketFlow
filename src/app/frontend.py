from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Any, Dict, List
from pathlib import Path

from src.lib.flow import discover_nodes, list_nodes_info, get_node, build_flow, Flow

# Discover nodes automatically via the nodes package
discover_nodes("src.nodes")

app = FastAPI(title="Flow UI")

# mount static frontend using path relative to this file
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.get("/")
async def root():
    return FileResponse(static_dir / "index.html")


class FlowRunRequest(BaseModel):
    nodes: list[str]
    context: Dict[str, Any] = {}


@app.get("/nodes")
def nodes_endpoint():
    return list_nodes_info()


@app.post("/run/{name}")
def run_node(name: str, context: Dict[str, Any]):
    try:
        node = get_node(name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Node '{name}' not found")
    try:
        result = node.run(context.copy())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=result)


@app.post("/flow/run")
def run_flow(body: FlowRunRequest):
    print(f"[flow/run] nodes={body.nodes} context={body.context}")
    try:
        flow = build_flow(body.nodes)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        result, trace = flow.run_with_trace(body.context.copy())
    except Exception as e:
        print(f"[flow/run] error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    print(f"[flow/run] result={result}")
    print(f"[flow/run] trace={trace}")
    return {"context": result, "trace": trace}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app.frontend:app", host="127.0.0.1", port=8000, reload=True)
