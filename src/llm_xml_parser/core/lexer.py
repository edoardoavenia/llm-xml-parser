import re
from ..exceptions.errors import XMLFormatError
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Regex to match tags or text content.
LEXER_PATTERN = re.compile(r'(<[^>]*>|[^<]+)')

def tokenize(xml_input: str):
    """
    Tokenizes XML string into (type, value) tuples.
    Types: 'OPEN_TAG', 'CLOSE_TAG', 'TEXT'.

    :param xml_input: XML input string.
    :return: List of (token_type, token_value).
    :raises XMLFormatError: For invalid tag names.
    """
    tokens = []
    matches = LEXER_PATTERN.findall(xml_input)

    for match in matches:
        match = match.strip('\r')  # Strip carriage returns
        if match.startswith("<"):
            if match.startswith("</"):
                # Close tag
                tag_content = match[2:-1].strip()
                tag_name = tag_content.split()[0].lower()
                if not valid_tag_name(tag_name):
                    raise XMLFormatError(f"Invalid or empty close tag: '{match}'")
                tokens.append(("CLOSE_TAG", tag_name))
            else:
                # Open tag
                inner = match[1:-1].strip()
                if not inner:
                    raise XMLFormatError(f"Empty open tag: '{match}'")
                parts = inner.split()
                tag_name = parts[0].lower()

                if tag_name.endswith("/"): # Handle self-closing tags minimally
                    tag_name = tag_name[:-1]

                if not valid_tag_name(tag_name):
                    raise XMLFormatError(f"Invalid or empty open tag: '{match}'")
                tokens.append(("OPEN_TAG", tag_name))
        else:
            # Text content
            tokens.append(("TEXT", match))

    logger.debug("Tokenization complete. Produced %d tokens.", len(tokens))
    return tokens


def valid_tag_name(name: str) -> bool:
    """
    Validates tag name: not empty, letters/digits/underscores only.
    Does not support namespaces or special chars per spec.
    """
    if not name:
        return False
    return bool(re.fullmatch(r'[A-Za-z0-9_]+', name))