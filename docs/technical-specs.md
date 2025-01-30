# XML Parser for LLM Structured Output
Technical documentation for developers interested in contributing to the project.

## System Architecture

### Processing Pipeline
1. **Pre-processing** (`preprocessor.py`)
   - XML comment removal
   - Artificial root tag insertion
   - Input normalization

2. **Tokenization** (`lexer.py`)
   - Regex pattern: `(<[^>]*>|[^<]+)`
   - Token generation: OPEN_TAG, CLOSE_TAG, TEXT
   - Case-insensitive tag name normalization
   - XML attribute removal

3. **Parsing** (`parser.py`)
   - Stack-based algorithm for hierarchy analysis
   - Tree construction with `Node` objects
   - Raw content tracking to preserve internal XML
   - In-stream structural validation

4. **Validation** (`validator.py`)
   - Configuration compliance verification
   - Warning/error generation
   - Structure flattening into `ParseResult`

### Key Data Structures

#### Node
```python
class Node:
    __slots__ = ("name", "text", "children", "raw_inner")
    # name: normalized tag name
    # text: textual content (mainly used for root)
    # children: list of child nodes
    # raw_inner: raw internal XML content
```

#### ParseResult
```python
class ParseResult:
    def __init__(self):
        self._data = {}      # Tag -> content mapping
        self._untagged = ""  # Untagged text
        self._warnings = []  # Warning list
```

### Memory Management
- `__slots__` usage for node memory optimization
- Flat data structure for results
- No caching or memoization
- Standard Python garbage collection

### Performance Analysis

#### Time Complexity
1. **Pre-processing**: *O(n)*
   - Comment removal with regex: single pass *O(n)*
   - Root tag addition: *O(1)*

2. **Tokenization**: *O(n)*
   - `LEXER_PATTERN` regex: *O(n)* for `findall`
   - Token validation: *O(k)* per token, total *O(n)*

3. **Tree Construction**: *O(n)* typical, *O(n²)* worst-case
   - Token iteration: *O(n)*
   - **Note**: String concatenations with `+=` in `raw_inner`:
     ```python
     node.raw_inner += f"<{tag}>"
     node.raw_inner += content
     ```
     Can degrade to *O(n²)* worst-case due to Python string immutability

4. **Validation and Flattening**: *O(n)*
   - Tree traversal: *O(n)* in number of nodes
   - Concatenation operations limited by maximum depth

#### Space Complexity
1. **Token Storage**: *O(n)*
   - List of `(token_type, token_value)` tuples

2. **Tree Structure**: *O(n)*
   - One `Node` per tag
   - Low overhead thanks to `__slots__`

3. **String Accumulation**: *O(n)* with depth limit
   - `raw_inner` can duplicate content in upper levels
   - Limited to *O(n)* by 3-4 level constraint
   - Without depth limit: theoretical *O(n²)* risk

#### Practical Behavior
- **Typical Input** (few KB, max 4 levels):
  - Time: Near *O(n)*
  - Space: *O(n)* with constant overhead
- **Worst Case** (large input, deep nesting):
  - Time: Can degrade to *O(n²)* due to concatenations
  - Space: *O(n)* guaranteed by depth limit

## Future Developments

### Core Improvements
1. **Maximum Level Control**
   - Improve maximum depth filter logic
   - Rethink level validation approach

2. **XML Comment Handling**
   - Comment preservation during parsing
   - Specific warning introduction for comments
   - Comment integration in configured tag results

3. **Root Tag Evaluation**
   - Analysis of artificial root tag necessity
   - Evaluate alternatives for malformed LLM output handling

### Advanced Features

1. **Streaming Support**
   - Evaluate streaming support implementation for LLM output
   - Identify use cases where streaming is actually beneficial

2. **Automatic LLM Prompt Generation**
   - System to generate prompts describing required XML format
   - Templates based on parser configuration

### Testing and Maintenance
- Add tests for new edge cases
- Keep documentation updated