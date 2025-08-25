
# Task 2: Implement Google API Authentication

**Description:**

Implement the OAuth 2.0 flow for Google API authentication, as described in the `docs/SECURITY.md` file.

**Requirements:**

1.  Create a file named `src/crewai_observability/auth.py`.
2.  Implement the `get_google_credentials` function as specified in `docs/SECURITY.md`.
3.  The implementation should handle the OAuth 2.0 flow for desktop applications.
4.  The implementation should save the credentials to a `token.json` file for future use.

**Acceptance Criteria:**

*   The `get_google_credentials` function is implemented in `src/crewai_observability/auth.py`.
*   The function correctly handles the OAuth 2.0 flow and returns valid credentials.
*   The credentials are saved to `token.json` to avoid re-authentication.
