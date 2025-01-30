class Node:
    """
    Represents a node in the parsed XML tree.
    Each node has:
      - name (str): The tag name
      - text (str): The accumulated text content (used mainly for root untagged).
      - children (list[Node]): Child nodes
      - raw_inner (str): The exact inner XML content of this node,
                         excluding the node's own <tag> and </tag>,
                         but including all sub-tags and text.
    """
    __slots__ = ("name", "text", "children", "raw_inner")

    def __init__(self, name: str):
        self.name = name
        self.text = ""        # Primarily used for the root node to store untagged text
        self.children = []    # List of child Node instances
        self.raw_inner = ""   # Stores the exact inner XML content

    def __repr__(self):
        return (
            f"<Node name='{self.name}' text={repr(self.text)} "
            f"children={len(self.children)} raw_inner={repr(self.raw_inner)}>"
        )
