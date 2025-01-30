# XML Parser for Structured LLM Output

## General Description
This parser implements a stack-based algorithm to analyze XML hierarchies, tracking parent-child relationships and structure depth. It offers flexible configurations for extracting specific tags (both single and lists) at defined depths, with a rigorous validation system. The implementation is optimized for small XML files (typically a few KB) with simple hierarchical structures (maximum 3-4 levels of depth).

### Core Features
The parser handles:
- **Critical Errors**: missing tags, unauthorized duplicates, empty lists
- **Non-Blocking Warnings**: nested tags in unexpected structures, mixed XML/text content
- **Untagged Text Handling**: preserves text not enclosed in XML tags
- **Case-Insensitive Tag Search**:  tag names are matched regardless of case.
- **Original Text Capitalization**: output text retains the exact capitalization from the input.

### Key Technical Features
- Exclusive use of Python standard libraries (no external dependencies)
- Case-insensitive only for tag names during search
- Preservation of original text, including capitalization and formatting
- Integrated logging system for warnings and errors

## Use Cases and Behaviors

**Important Note:** The `ParseResult` structure is **flat**. All configured tags, including those defined as "children" in the configuration, are accessible as first-level attributes of the `result` object. There is no nested hierarchical structure.

### ✅ Correctly Handled Cases
Elements extracted without warnings or errors.

#### 1. Single Element at Depth 0
**XML**:
```xml
<thinking>This is a test</thinking>
```
**Config**: `{'thinking': 'single'}`
**Output**:
```python
result.thinking → "This is a test"
```

#### 2. List with 2+ Elements
**XML**:
```xml
<step>A</step>
<step>B</step>
<step>C</step>
```
**Config**: `{'step': 'list'}`
**Output**:
```python
result.step → ["A", "B", "C"]
```

#### 3. Explicitly Configured Hierarchy
**XML**:
```xml
<exercise>
    <question>What is 2+2?</question>
    <answer>The answer is 4</answer>
</exercise>
```
**Config**:
```python
config = {
    'exercise': {
        'type': 'single',
        'children': {
            'question': 'single',
            'answer': 'single'
        }
    }
}
```
**Output**:
```python
result.exercise → "<question>What is 2+2?</question><answer>The answer is 4</answer>" 
result.question → "What is 2+2?" 
result.answer → "The answer is 4"
```

#### 4. Correct Untagged Text Extraction
**LLM Input**:
```xml
<thinking>Analysis</thinking>
Answer: 42
```
**After Pre-Processing**:
```xml
<root>
    <thinking>Analysis</thinking>
    Answer: 42
</root>
```
*Note: Preprocessing always adds an artificial root tag, since LLM output often does not include a valid root tag. The root tag is shown here only to illustrate the handling of unlabeled text.*

**Output**:
```python
result.thinking → "Analysis"
result.untagged → "Answer: 42"
```

### ⚠️ Warnings (Extraction with Notification)
Elements extracted with warnings in logs and accessible via `ParseResult.warnings`

#### 1. Nested Tags in Single Element
**XML**:
```xml
<thinking>Use <formula>E=mc²</formula></thinking>
```
**Config**: `{'thinking': 'single'}`
**Output**:
```python
result.thinking → "Use <formula>E=mc²</formula>"
# Log and warnings: "Unconfigured tag <formula> found inside 'thinking'"
```

#### 2. Unconfigured Tag in List
**XML**:
```xml
<step>
    A<detail>some info</detail>
</step>
<step>B</step>
```
**Config**: `{'step': 'list'}`
**Output**:
```python
result.step → ["A<detail>some info</detail>", "B"]
# Log and warnings: "Unconfigured tag <detail> found inside 'step'"
```

#### 3. List with 1 Element
**XML**:
```xml
<step>Single step</step>
```
**Config**: `{'step': 'list'}`
**Output**:
```python
result.step → ["Single step"]
# Log and warnings: "List <step> contains only 1 element."
```

### ❌ Blocking Errors
Interrupt execution by raising specific exceptions.

#### 1. Missing Single Element
**XML**: `<answer>42</answer>`
**Config**: `{'thinking': 'single'}`
**Error**:
```python
XMLStructureError: Tag <thinking> not found (single required).
```

#### 2. Too Many Single Elements
**XML**:
```xml
<answer>42</answer>
<answer>43</answer>
```
**Config**: `{'answer': 'single'}`
**Error**:
```python
XMLStructureError: Multiple <answer> found, but 'single' is required.
```

#### 3. Empty List
**XML**: `<answer>stuff</answer>`
**Config**: `{'steps': 'list'}`
**Error**:
```python
XMLStructureError: List <steps> is empty (1+ elements required).
```

#### 4. Malformed XML
**XML**:
```xml
<thinking>Test<thinking>
```
or
```xml
<a><b></a></b>
```
**Error**:
```python
XMLFormatError: Unclosed tags remain. Malformed XML structure.
```
or
```python
XMLFormatError: Mismatched tags: opened <b>, but closed </a>
```

## Unhandled Cases
The parser is designed to be minimalist and efficiently handle simple XML output from LLMs. The following cases are not supported:

1. **Namespaces**
   - ❌ Invalid: `<ns:thinking>Test</ns:thinking>`

2. **Tags with Special Characters**
   - ✅ Valid: `<distro_linux>Test</distro_linux>` (underscore supported)
   - ❌ Invalid: `<foo-bar>Test</foo-bar>`
   - ❌ Invalid: `<foo bar>Test</foo bar>`

3. **CDATA and Complex Content**
   - CDATA sections not interpreted
   - XML entities not processed
   - ❌ Not handled: `<thinking><![CDATA[<test>]]></thinking>`

4. **XML Attributes**
   - Tag attributes ignored
   - ❌ Not handled: `<tag attr="val">Test</tag>`

## Implementation Details

### Execution Modes
1. **Normal Mode** (Default, `strict_mode=False`)
   - Warnings logged but non-blocking
   - Only errors generate exceptions
   - Output preserved even with warnings

2. **Strict Mode** (`strict_mode=True`)
   - All warnings become blocking errors
   - Maximum validation rigor

### Input Handling
- **Size**: Optimized for small XML files (10-20 KB)
- **Depth**: Efficient support up to 3-4 levels
- **Case Sensitivity**:
  - Tags: case-insensitive during search
  - Content: preserved exactly as in input

### Pre-Processing
- Automatic removal of XML comments
- Automatic root tag addition
- Basic input normalization

## Technical Requirements
- **Python**: Version 3.7 or higher
- **Dependencies**: Python standard library only
- **Encoding**: UTF-8 for input/output