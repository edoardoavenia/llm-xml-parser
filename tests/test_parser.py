import pytest
import json
import os

from src.llm_xml_parser.core.parser import parse
# If specific exceptions are needed, import them:
# from src.exceptions.errors import XMLParserError, XMLStructureError, XMLFormatError

def load_test_cases():
    """Loads all test cases from the JSON file."""
    input_file = os.path.join("tests", "test_inputs.json")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Test file not found: {input_file}")

    with open(input_file, encoding="utf-8") as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_test_cases())
def test_parser_cases(test_case):
    """
    Executes the test for each case read from test_inputs.json.
    Verifies that success/error/warnings/output/untagged
    correspond to what is specified.
    """
    xml_data = test_case["xml"]
    config = test_case["config"]
    expected_success = test_case["success"]
    expected_error = test_case["error"]
    expected_warnings = test_case["warnings"]
    expected_output = test_case["output"]
    expected_untagged = test_case["untagged"]

    # Let's try to parse
    try:
        result = parse(xml_data, config)

        # If the test expects a failure, but the parser does NOT raise an exception → test fails
        if not expected_success:
            pytest.fail(
                f"An error was expected, but the parser was successful. "
                f"Data obtained: {result._data}, warnings: {result.warnings}"
            )

        # If there was no error, we expect expected_error to be None
        assert expected_error is None, (
            f"Error '{expected_error}' was expected, but no error was raised."
        )

        # Verify warnings
        actual_warnings = result.warnings
        assert len(actual_warnings) == len(expected_warnings), (
            f"Different number of warnings. "
            f"Expected: {expected_warnings} - Obtained: {actual_warnings}"
        )
        for i, warning_msg in enumerate(expected_warnings):
            # If you only want to check that the expected string is included in the real one
            # you can do an "in" or an equality check
            assert warning_msg in actual_warnings[i], (
                f"Expected warning '{warning_msg}' does not match '{actual_warnings[i]}'"
            )

        # Verify the output dictionary
        actual_data = result._data
        assert actual_data == expected_output, (
            f"Output (tag fields) different from the expected one.\n"
            f"Expected: {expected_output}\nObtained: {actual_data}"
        )

        # Verify the untagged text
        actual_untagged = result.untagged
        assert actual_untagged == expected_untagged, (
            f"Untagged text different.\n"
            f"Expected: '{expected_untagged}'\nObtained: '{actual_untagged}'"
        )

    except Exception as e:
        # If the parser raises an exception but the test expects success → test fails
        if expected_success:
            pytest.fail(f"Success was expected, but an error was raised: {e}")
        else:
            # If the test expects an error, let's check that it corresponds
            assert expected_error is not None, (
                "No error message expected, but an exception was raised."
            )
            # Verify that the expected string is contained in the exception
            assert expected_error in str(e), (
                f"Expected error message '{expected_error}' not present in '{str(e)}'"
            )