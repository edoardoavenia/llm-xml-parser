"""
Defines the ParseResult class, which stores the structured output
of the parser and allows dot-notation access to tags.
"""

class ParseResult:
    """
    Represents the result of parsing an XML string.

    Attributes:
      - untagged (str): Contains any text not enclosed by tags at root level.
      - warnings (list): Contains string descriptions of any non-blocking issues.
    """

    def __init__(self):
        # Use a private dictionary to store data keyed by tag name
        self._data = {}
        # Untagged text at the root level
        self._untagged = ""
        # List of warning messages
        self._warnings = []

    def add_warning(self, message: str):
        """
        Adds a warning message to the parse result.
        """
        self._warnings.append(message)

    @property
    def warnings(self) -> list:
        """
        Returns the list of warning messages.
        """
        return self._warnings

    @property
    def untagged(self) -> str:
        """
        Returns the untagged text at the root level.
        """
        return self._untagged

    @untagged.setter
    def untagged(self, value: str):
        """
        Sets the untagged text at the root level.
        """
        self._untagged = value

    def set_tag_value(self, tag_name: str, value):
        """
        Stores a parsed tag value under the given tag name.
        If the tag already exists, it will be overwritten unless
        the caller handles merging or appending separately.
        """
        self._data[tag_name] = value

    def get_tag_value(self, tag_name: str):
        """
        Retrieves a parsed tag value by tag name.
        """
        return self._data.get(tag_name, None)

    def __getattr__(self, name: str):
        """
        Allows dot-notation access for stored tags.
        Example: parse_result.thinking → returns self._data["thinking"] if it exists.
        """
        if name in self._data:
            return self._data[name]
        # If attribute not found in _data, raise AttributeError
        raise AttributeError(f"No attribute named '{name}' in ParseResult.")

    def __repr__(self):
        """
        Developer-friendly representation of the parse result.
        """
        return (
            f"<ParseResult untagged={repr(self._untagged)} "
            f"warnings={self._warnings} data={self._data}>"
        )
