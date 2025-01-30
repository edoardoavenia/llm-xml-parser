from llm_xml_parser.utils.logger import get_logger
from llm_xml_parser.utils.preprocessor import preprocess_xml
from llm_xml_parser.exceptions.errors import XMLFormatError, XMLStructureError
from llm_xml_parser.exceptions.warnings import XMLNestedWarning, XMLSingleItemWarning
from llm_xml_parser.structures.config import validate_config
from llm_xml_parser.structures.result import ParseResult
from llm_xml_parser.structures.node import Node
from llm_xml_parser.core.lexer import tokenize
from llm_xml_parser.core.validator import validate_and_flatten_tree

logger = get_logger(__name__)

def parse(xml_input: str, config: dict, strict_mode: bool = False) -> ParseResult:
    """
    Parses XML string to tree, validates, and flattens to ParseResult.
    Preserves full content of configured tags (sub-tags, text).

    :param xml_input: Raw XML string.
    :param config: Tag extraction configuration.
    :param strict_mode: Treat warnings as errors if True.
    :return: ParseResult with structured data and warnings.
    :raises XMLFormatError: For malformed XML.
    :raises XMLStructureError: For config mismatch.
    """
    # Validate the configuration
    validate_config(config)

    # Preprocess the XML (remove comments and add <root>...</root> if necessary)
    processed_xml = preprocess_xml(xml_input)

    # Tokenize the preprocessed XML
    tokens = tokenize(processed_xml)

    # Build the tree using a stack of Node objects
    root_node = Node("root")
    stack = [root_node]

    for token_type, token_value in tokens:
        # Ignore the artificial <root> tags
        if token_type == "OPEN_TAG" and token_value == "root":
            continue
        if token_type == "CLOSE_TAG" and token_value == "root":
            continue

        if token_type == "OPEN_TAG":
            # Create a new child node
            child_node = Node(token_value)
            # Append the child to the current node's children
            stack[-1].children.append(child_node)
            
            # If the current node is not root, append the opening tag to its raw_inner
            if stack[-1].name != "root":
                stack[-1].raw_inner += f"<{token_value}>"

            # Push the new child onto the stack
            stack.append(child_node)

        elif token_type == "TEXT":
            if stack[-1].name == "root":
                # Accumulate untagged text in the root node
                root_node.text += token_value
            else:
                # Accumulate text and sub-tags in the current node's raw_inner
                stack[-1].raw_inner += token_value

        elif token_type == "CLOSE_TAG":
            if not stack:
                raise XMLFormatError(f"Unexpected closing tag </{token_value}>")

            top_node = stack.pop()
            if top_node.name != token_value:
                raise XMLFormatError(
                    f"Mismatched tags: opened <{top_node.name}>, "
                    f"but closed </{token_value}>"
                )

            if stack:
                parent_node = stack[-1]
                # If the parent is not root, append the closing tag and the child's raw_inner
                if parent_node.name != "root":
                    parent_node.raw_inner += top_node.raw_inner
                    parent_node.raw_inner += f"</{token_value}>" # TODO: Optimize raw_inner concatenation performance 

    # After processing, ensure only the root node remains in the stack
    if len(stack) != 1 or stack[0].name != "root":
        raise XMLFormatError("Unclosed tags remain. Malformed XML structure.")

    # 5) Create the ParseResult object
    parse_result = ParseResult()
    parse_result.untagged = root_node.text  # Store untagged text

    # 6) Validate and flatten the node tree into the ParseResult
    validate_and_flatten_tree(
        root_node.children,  # Top-level nodes
        config,
        parse_result,
        strict_mode
    )

    logger.debug("Parsing complete with %d warnings.", len(parse_result.warnings))
    return parse_result