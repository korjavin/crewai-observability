# Contributing to the AI-Powered Scheduling Assistant

First off, thank you for considering contributing! Your help is appreciated.

This document provides guidelines for contributing to this project.

## Development Setup

1.  **Fork & Clone:** Fork the repository on GitHub and clone your fork locally.
2.  **Install Dependencies:** This project uses Poetry for dependency management. To install all necessary dependencies, including development tools, run:
    ```bash
    make install
    ```
    This command sets up the virtual environment and installs all packages listed in `pyproject.toml`.

## Running Tests

To ensure the stability and quality of the codebase, we have a comprehensive test suite. Please run the tests before submitting a pull request to ensure that your changes do not break existing functionality.

You can use the following `make` commands to run the tests:

-   **Run all tests (unit and integration):**
    ```bash
    make test
    ```
-   **Run only unit tests:**
    ```bash
    make test-unit
    ```
-   **Run only integration tests:**
    ```bash
    make test-integration
    ```

## Code Quality

We use `black` for code formatting and `flake8` for linting.

-   **Format your code:**
    ```bash
    make fmt
    ```
-   **Check for linting errors:**
    ```bash
    make lint
    ```

All code quality checks must pass before a pull request can be merged.

## Submitting a Pull Request

1.  Create a new branch for your feature or bug fix.
2.  Make your changes.
3.  Ensure all tests and code quality checks pass.
4.  Push your changes to your fork and submit a pull request to the `main` branch of the original repository.
5.  The CI pipeline will automatically run all checks. Please ensure they all pass.

Thank you for your contribution!
