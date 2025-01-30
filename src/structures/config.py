"""
Validates the user-defined configuration for the XML parser,
ensuring:
  - Up to 4 levels of nested 'children'
  - Either 'single' or 'list' for simple tags
  - Correct structure when specifying nested dictionaries
"""

from ..exceptions.errors import XMLConfigError

def validate_config(config: dict, current_depth: int = 0, max_depth: int = 4):
    """
    Recursively validates the parser configuration.

    :param config: The configuration dict to validate.
    :param current_depth: The current level of nesting.
    :param max_depth: The maximum allowed nesting depth.
    :raises XMLConfigError: If the configuration is invalid.
    """
    if current_depth > max_depth:
        raise XMLConfigError(
            f"Configuration too deep: maximum {max_depth} levels supported"
        )
    
    if not isinstance(config, dict):
        raise XMLConfigError("Configuration must be a dict at each level.")
    
    for tag, value in config.items():
        # 'value' can be:
        # 1. A string: 'single' or 'list'
        # 2. A dictionary: { 'type': 'single'/'list', 'children': { ... } }
        if isinstance(value, str):
            # Must be 'single' or 'list'
            if value not in ("single", "list"):
                raise XMLConfigError(
                    f"Tag '{tag}' has invalid configuration: '{value}'. "
                    "Must be 'single' or 'list'."
                )
        elif isinstance(value, dict):
            # Must have a 'type' field
            if 'type' not in value:
                raise XMLConfigError(
                    f"Tag '{tag}' configuration dictionary must have a 'type' key."
                )
            if value['type'] not in ("single", "list"):
                raise XMLConfigError(
                    f"Tag '{tag}' has invalid 'type': {value['type']}. "
                    "Must be 'single' or 'list'."
                )
            
            # If children exist, recurse
            if 'children' in value:
                if not isinstance(value['children'], dict):
                    raise XMLConfigError(
                        f"Tag '{tag}' has 'children' but it is not a dict."
                    )
                # Recurse deeper
                validate_config(value['children'], current_depth + 1, max_depth)
        else:
            raise XMLConfigError(
                f"Tag '{tag}' has invalid config type: {type(value)}. "
                "Must be str or dict."
            )
