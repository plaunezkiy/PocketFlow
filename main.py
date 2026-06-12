from src.flows.load_doc.nodes import LoadDocNode, LoadDocInput, LoadDocOutput


if __name__ == "__main__":
    # Example usage of LoadDocNode
    input_ctx = LoadDocInput(doc_path="data/example.txt")
    
    load_doc_node = LoadDocNode()
    output = load_doc_node.run(input_ctx)
    print(output.content)