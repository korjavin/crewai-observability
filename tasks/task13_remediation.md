
# Task 13 Remediation: Mocking Google API Calls

**Description:**

This task provides guidance on how to correctly mock the Google API calls in the unit tests for the custom tools. The key is to patch the `googleapiclient.discovery.build` function to prevent the real library code from running.

**Guidance:**

1.  **Patch the `build` function:** In your test file (`tests/unit/test_google_tools.py`), use `unittest.mock.patch` to patch `googleapiclient.discovery.build`. The patch should target the `build` function where it is imported and used, which is in `src.crewai_observability.tools.google_tools`.

    ```python
    from unittest.mock import patch, MagicMock

    @patch('src.crewai_observability.tools.google_tools.build')
    def test_gmail_reader_tool(self, mock_build):
        # ...
    ```

2.  **Configure the mock object:** The `mock_build` argument in your test function is a `MagicMock` object. You need to configure it to simulate the behavior of the Google API. This involves mocking the chain of method calls that the tool makes.

    ```python
    # Create a mock service object
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Mock the chain of calls for the GmailReaderTool
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.list.return_value.execute.return_value = {'messages': [{'id': '123'}]}
    mock_messages.get.return_value.execute.return_value = {
        'payload': {
            'headers': [{'name': 'Subject', 'value': 'Test Subject'}],
            'parts': [{'mimeType': 'text/plain', 'body': {'data': 'VGVzdCBib2R5'}}] # 'Test body' base64 encoded
        }
    }
    ```

3.  **Use `autospec=True`:** When creating mocks, it is a good practice to use `autospec=True`. This will ensure that the mock object has the same interface as the real object, which can help to catch errors in your tests.

    ```python
    @patch('src.crewai_observability.tools.google_tools.build', autospec=True)
    ```

By following this guidance, you should be able to correctly mock the Google API calls and resolve the `UniverseMismatchError`.
