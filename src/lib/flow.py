import importlib
import pkgutil
from typing import Any, List, Dict, Tuple, Callable, Optional

# Global registry of nodes
_NODE_REGISTRY: Dict[str, "Node"] = {}


def register_node(name: str):
    """Decorator to register a node singleton by name."""
    def decorator(node_class):
        instance = node_class()
        _NODE_REGISTRY[name] = instance
        return node_class
    return decorator


def get_node(name: str) -> "Node":
    """Retrieve a registered node by name."""
    if name not in _NODE_REGISTRY:
        raise KeyError(f"Node '{name}' not registered")
    return _NODE_REGISTRY[name]


def list_nodes() -> List[str]:
    """List all registered node names."""
    return list(_NODE_REGISTRY.keys())


def list_nodes_info() -> List[Dict[str, Any]]:
    """List registered nodes with optional metadata."""
    return [
        {"name": name, "schema": node.schema()}
        for name, node in _NODE_REGISTRY.items()
    ]


def discover_nodes(package_name: str = "src.nodes") -> List[str]:
    """Discover node modules under a package and import them to register nodes."""
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        raise ValueError(f"Package {package_name} is not a package")

    for finder, module_name, _ in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + "."):
        importlib.import_module(module_name)

    return list_nodes()


class Node:
    """Base stateless node: reads from context, transforms, returns modified context."""

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node on the shared context.
        
        Args:
            context: shared mutable context dict
        
        Returns:
            the modified context (may be the same object)
        """
        raise NotImplementedError

    def schema(self) -> Optional[Dict[str, Any]]:
        """Return optional node schema metadata for UI inspection."""
        return None


class Flow:
    """Flow that chains nodes and supports conditional transitions via predicates."""

    def __init__(self) -> None:
        self.nodes: List[Node] = []
        # transitions[from_index] = list of (predicate, to_index)
        self.transitions: Dict[int, List[Tuple[Callable[[Dict[str, Any]], bool], int]]] = {}

    def add(self, node: Node) -> int:
        """Register a node and return its index."""
        idx = len(self.nodes)
        self.nodes.append(node)
        return idx

    def connect(self, from_idx: int, to_idx: int, predicate: Callable[[Dict[str, Any]], bool]) -> None:
        """Connect two nodes with a predicate that evaluates the full context.
        
        Args:
            from_idx: source node index
            to_idx: target node index
            predicate: function(context: dict) -> bool to select the transition
        """
        if from_idx < 0 or from_idx >= len(self.nodes):
            raise IndexError("from_idx out of range")
        if to_idx < 0 or to_idx >= len(self.nodes):
            raise IndexError("to_idx out of range")

        self.transitions.setdefault(from_idx, []).append((predicate, to_idx))

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the flow on the shared context.
        
        Args:
            context: initial context dict (will be mutated)
        
        Returns:
            the final context after all nodes execute
        """
        result, _trace = self.run_with_trace(context)
        return result

    def run_with_trace(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Execute the flow and return execution trace for each node."""
        if not self.nodes:
            raise RuntimeError("Flow has no nodes")

        trace: List[Dict[str, Any]] = []
        idx = 0
        step = 0
        while idx is not None:
            node = self.nodes[idx]
            before = context.copy()
            after = node.run(context)
            trace.append({
                "step": step,
                "node": type(node).__name__,
                "name": self.nodes[idx].__class__.__name__,
                "before": before,
                "after": after.copy() if isinstance(after, dict) else after,
                "idx": idx,
            })
            context = after

            next_idx = None
            for pred, target in self.transitions.get(idx, []):
                try:
                    ok = bool(pred(context))
                except Exception:
                    ok = False
                if ok:
                    next_idx = target
                    break

            if next_idx is None and idx + 1 < len(self.nodes):
                next_idx = idx + 1

            idx = next_idx
            step += 1

        return context, trace

    @classmethod
    def from_node_names(cls, names: List[str]) -> "Flow":
        """Construct a flow from an ordered list of registered node names."""
        flow = cls()
        for name in names:
            flow.add(get_node(name))
        return flow


def build_flow(node_names: List[str]) -> Flow:
    """Build a flow from a list of registered node names."""
    return Flow.from_node_names(node_names)
