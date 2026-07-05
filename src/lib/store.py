"""Simple JSON-based flow persistence."""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class FlowStore:
    """Store flow definitions as JSON files."""

    def __init__(self, storage_dir: str = "flows"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save(self, flow_id: str, nodes: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Save a flow definition."""
        if context is None:
            context = {}

        flow_spec = {
            "id": flow_id,
            "nodes": nodes,
            "context": context,
        }

        file_path = self.storage_dir / f"{flow_id}.json"
        with file_path.open("w") as f:
            json.dump(flow_spec, f, indent=2)

        return flow_spec

    def load(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Load a flow definition."""
        file_path = self.storage_dir / f"{flow_id}.json"
        if not file_path.exists():
            return None

        with file_path.open("r") as f:
            return json.load(f)

    def list(self) -> List[Dict[str, Any]]:
        """List all saved flows."""
        flows = []
        for file_path in self.storage_dir.glob("*.json"):
            with file_path.open("r") as f:
                flows.append(json.load(f))
        return sorted(flows, key=lambda f: f["id"])

    def delete(self, flow_id: str) -> bool:
        """Delete a flow definition."""
        file_path = self.storage_dir / f"{flow_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
