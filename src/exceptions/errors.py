
"""
Contains the main blocking exceptions used by the XML parser:
    - XMLStructureError
    - XMLFormatError
    - XMLConfigError
"""

class XMLParserError(Exception):
    """
    Base exception for XML parser errors that block execution.
    """
    pass


class XMLStructureError(XMLParserError):
    """
    Raised when an expected structure (like a single tag) is missing or duplicated,
    or a required list is empty, etc.
    """
    pass


class XMLFormatError(XMLParserError):
    """
    Raised when the XML input is malformed (e.g., unclosed tags, mismatched tags).
    """
    pass


class XMLConfigError(XMLParserError):
    """
    Raised when the parser configuration is invalid (e.g., too deep or ill-defined).
    """
    pass
