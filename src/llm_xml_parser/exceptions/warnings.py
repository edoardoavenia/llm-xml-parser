"""
Contains the non-blocking warnings used by the XML parser:
    - XMLNestedWarning
    - XMLSingleItemWarning
"""

class XMLParserWarning(Warning):
    """
    Base warning for non-blocking parser issues.
    """
    pass


class XMLNestedWarning(XMLParserWarning):
    """
    Raised when there is nested XML in an unexpected context,
    or tags found within an unconfigured container.
    """
    pass


class XMLSingleItemWarning(XMLParserWarning):
    """
    Raised when a 'list' configuration contains only one item.
    """
    pass
