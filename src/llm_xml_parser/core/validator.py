from llm_xml_parser.exceptions.errors import XMLStructureError
from llm_xml_parser.exceptions.warnings import XMLNestedWarning, XMLSingleItemWarning
from llm_xml_parser.structures.result import ParseResult
from llm_xml_parser.structures.node import Node
from llm_xml_parser.utils.logger import get_logger

logger = get_logger(__name__)

def validate_and_flatten_tree(
    nodes: list[Node],
    config: dict,
    parse_result: ParseResult,
    strict_mode: bool,
    parent_tag: str = "root",
):
    """
    Recursively validates the given list of nodes against the configuration,
    flattening their raw_inner content into the ParseResult.
    Configured tags retain their complete inner XML. Unconfigured tags
    generate warnings, even if they appear as children of a configured tag.

    :param nodes: List of Node objects to validate and flatten.
    :param config: Configuration dictionary defining expected tags and their types.
    :param parse_result: The ParseResult object to populate with parsed data.
    :param strict_mode: If True, warnings are treated as errors.
    :param parent_tag: The name of the parent tag for context in warnings.
    :raises XMLStructureError: If the XML structure does not comply with the configuration.
    """

    # TODO: Evaluate alternative solutions to handle deep configurations more robustly and efficiently (currently limited by depth filter)

    used_tags = {}
    unconfigured_nodes = []

    # Classify nodes based on configuration
    for node in nodes:
        tag_lower = node.name.lower()
        if tag_lower in config:
            used_tags.setdefault(tag_lower, []).append(node)
        else:
            # Unconfigured tag: generate a warning
            warning_msg = f"Unconfigured tag <{node.name}> found inside '{parent_tag}'"
            handle_warning(parse_result, XMLNestedWarning(warning_msg), strict_mode)
            unconfigured_nodes.append(node)

    # For each unconfigured node, recursively check its children,  so that deeper unconfigured tags also produce warnings.
    for unconf_node in unconfigured_nodes:
        validate_and_flatten_tree(
            unconf_node.children,
            {},  # empty config → all children are unconfigured
            parse_result,
            strict_mode,
            parent_tag=unconf_node.name
        )

    # Handle each configured tag
    for tag_name, conf_val in config.items():
        nodes_for_tag = used_tags.get(tag_name, [])

        ttype, children_cfg = extract_type_and_children(tag_name, conf_val)

        if ttype == "single":
            if len(nodes_for_tag) == 0:
                raise XMLStructureError(
                    f"Tag <{tag_name}> not found (single required)."
                )
            if len(nodes_for_tag) > 1:
                raise XMLStructureError(
                    f"Multiple <{tag_name}> found, but 'single' is required."
                )

            node_obj = nodes_for_tag[0]

            # If children_cfg is None, we treat it as an empty dict so child tags are checked.
            if children_cfg is None:
                children_cfg = {}

            # Recursively process the node's children (unconfigured children will raise warnings)
            validate_and_flatten_tree(
                node_obj.children,
                children_cfg,
                parse_result,
                strict_mode,
                parent_tag=tag_name
            )

            # Store the entire raw_inner of this node
            store_single_value(parse_result, tag_name, node_obj.raw_inner)

        elif ttype == "list":
            if len(nodes_for_tag) == 0:
                raise XMLStructureError(
                    f"List <{tag_name}> is empty (1+ elements required)."
                )
            if len(nodes_for_tag) == 1:
                warn_msg = f"List <{tag_name}> contains only 1 element."
                handle_warning(parse_result, XMLSingleItemWarning(warn_msg), strict_mode)

            # If children_cfg is None, treat it as empty for recursion
            if children_cfg is None:
                children_cfg = {}

            stored_list = []
            for node_obj in nodes_for_tag:
                # Validate children for potential warnings or deeper configurations
                validate_and_flatten_tree(
                    node_obj.children,
                    children_cfg,
                    parse_result,
                    strict_mode,
                    parent_tag=tag_name
                )
                # Append the entire raw_inner of each element
                stored_list.append(node_obj.raw_inner)
            store_list_value(parse_result, tag_name, stored_list)


def extract_type_and_children(tag_name: str, conf_val):
    """
    Extracts the type ('single' or 'list') and children configuration for a given tag.

    :param tag_name: The name of the tag.
    :param conf_val: The configuration value for the tag.
    :return: A tuple (type_str, children_config). children_config will always be a dictionary (even empty).
    :raises XMLStructureError: If the configuration for the tag is invalid.
    """
    if isinstance(conf_val, str):
        # e.g. "single" or "list"
        return conf_val, {}  # Return an empty dictionary instead of None
    elif isinstance(conf_val, dict):
        ttype = conf_val.get("type")
        children = conf_val.get("children", {}) # If 'children' is missing, use an empty dict as default
        return ttype, children
    else:
        raise XMLStructureError(
            f"Invalid config entry for tag <{tag_name}>. Must be str or dict."
        )


def handle_warning(parse_result: ParseResult, warning_obj: Warning, strict_mode: bool):
    """
    Handles warnings by logging them and adding them to the ParseResult.
    If strict_mode is True, warnings are elevated to XMLStructureError.

    :param parse_result: The ParseResult object to populate with warnings.
    :param warning_obj: The warning object to handle.
    :param strict_mode: If True, warnings become blocking errors.
    """
    warning_msg = str(warning_obj)
    logger.warning(warning_msg)
    if strict_mode:
        raise XMLStructureError(f"Strict mode error: {warning_msg}")
    else:
        parse_result.add_warning(warning_msg)


def store_single_value(parse_result: ParseResult, tag_name: str, text_value: str):
    """
    Stores a single value for a tag in the ParseResult.

    :param parse_result: The ParseResult object to populate.
    :param tag_name: The name of the tag.
    :param text_value: The raw_inner XML content to store for this tag.
    :raises XMLStructureError: If multiple single tags are found.
    """
    if parse_result.get_tag_value(tag_name) is not None:
        raise XMLStructureError(
            f"Multiple <{tag_name}> found, but 'single' is required."
        )
    parse_result.set_tag_value(tag_name, text_value)


def store_list_value(parse_result: ParseResult, tag_name: str, text_list: list[str]):
    """
    Stores a list of values for a tag in the ParseResult.

    :param parse_result: The ParseResult object to populate.
    :param tag_name: The name of the tag.
    :param text_list: A list of raw_inner XML contents to store for this tag.
    :raises XMLStructureError: If a tag is inconsistently used as both single and list.
    """
    existing = parse_result.get_tag_value(tag_name)
    if existing is None:
        parse_result.set_tag_value(tag_name, text_list)
    else:
        if not isinstance(existing, list):
            raise XMLStructureError(
                f"Tag <{tag_name}> was previously single, now list encountered."
            )
        existing.extend(text_list)
        parse_result.set_tag_value(tag_name, existing)
