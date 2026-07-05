from src.nodes.load_doc import LoadDocNode, LoadDocInput, LoadDocOutput


if __name__ == "__main__":
    # Example usage of LoadDocNode
    input_ctx = LoadDocInput(doc_path="data/example.txt")

    load_doc_node = LoadDocNode()
    context = {"doc_path": input_ctx.doc_path}
    output = load_doc_node.run(context)
    print(output["content"])