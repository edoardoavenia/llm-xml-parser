import re
from .logger import get_logger

logger = get_logger(__name__)

def preprocess_xml(xml_input: str) -> str:
    """
    Preprocesses the raw XML string by:
      1. Removing any XML comments.
      2. Wrapping the entire input with an artificial <root>...</root> tag.

    :param xml_input: The XML string that may lack a proper root tag.
    :return: A well-formed XML string with a <root> tag wrapping all content.
    """
    if not xml_input:
        # If empty, just wrap an empty root
        logger.debug("Received empty XML input. Returning <root></root>.")
        return "<root></root>"

    # 1) Remove XML comments using a simple regex (non-greedy).
    #    This regex will remove anything in the form <!-- ... -->
    #    It does NOT handle nested or tricky edge cases but suffices for typical usage.
    without_comments = re.sub(r"<!--.*?-->", "", xml_input, flags=re.DOTALL)

    # 2) Strip leading/trailing whitespace to keep things neat
    trimmed = without_comments.strip()

    # 3) Wrap everything inside a <root> tag
    processed = f"<root>{trimmed}</root>"

    logger.debug("Preprocessing completed. Added <root> wrapper.")
    return processed
