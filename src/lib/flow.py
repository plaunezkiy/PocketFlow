from typing import Generic, TypeVar, Any, List, Dict, Tuple, Callable
from pydantic import BaseModel

InT = TypeVar("InT", bound=BaseModel)
OutT = TypeVar("OutT", bound=BaseModel)


class Node(Generic[InT, OutT]):
    """Generic Node with pydantic models for input and output."""
    in_model: type[InT]
    out_model: type[OutT]

    def run(self, data: InT) -> OutT:
        raise NotImplementedError

    def __call__(self, raw_input: Any) -> OutT:
        in_obj = self.in_model.model_validate(raw_input)
        out_obj = self.run(in_obj)
        return self.out_model.model_validate(out_obj)


class Flow:
    """Flow that supports conditional transitions between nodes.

    Use `add()` to register nodes (returns an index), and `connect()` to
    create conditional transitions from one node to another. Predicates
    receive the output model instance returned by the source node.
    """

    def __init__(self) -> None:
        self.nodes: List[Node] = []
        # transitions[from_index] = list of (predicate, to_index)
        self.transitions: Dict[int, List[Tuple[Callable[[Any], bool], int]]] = {}

    def add(self, node: Node) -> int:
        """Register a node and return its index."""
        idx = len(self.nodes)
        self.nodes.append(node)
        return idx

    def connect(self, from_idx: int, to_idx: int, predicate: Callable[[Any], bool]) -> None:
        """Connect two nodes with a predicate that selects the transition.

        Raises TypeError if the output type of `from_idx` is incompatible
        with the input type of `to_idx`.
        """
        if from_idx < 0 or from_idx >= len(self.nodes):
            raise IndexError("from_idx out of range")
        if to_idx < 0 or to_idx >= len(self.nodes):
            raise IndexError("to_idx out of range")

        from_out = self.nodes[from_idx].out_model
        to_in = self.nodes[to_idx].in_model
        try:
            compatible = from_out is to_in or issubclass(from_out, to_in) or issubclass(to_in, from_out)
        except Exception:
            compatible = from_out is to_in
        if not compatible:
            raise TypeError(f"Incompatible transition: {from_out} -> {to_in}")

        self.transitions.setdefault(from_idx, []).append((predicate, to_idx))

    def run(self, raw_input: Any) -> Any:
        if not self.nodes:
            raise RuntimeError("Flow has no nodes")

        idx = 0
        current = raw_input
        while idx is not None:
            node = self.nodes[idx]
            current = node(current)

            # evaluate transitions for this node in insertion order
            next_idx = None
            for pred, target in self.transitions.get(idx, []):
                try:
                    ok = bool(pred(current))
                except Exception:
                    ok = False
                if ok:
                    next_idx = target
                    break

            idx = next_idx

        return current
