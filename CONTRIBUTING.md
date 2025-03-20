# Contributing to Handyman KPI System

Thank you for considering contributing to the Handyman KPI System! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue in the repository with the following information:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment details (OS, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- A clear, descriptive title
- Detailed description of the proposed enhancement
- Any relevant examples or mockups
- Explanation of why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request

## Development Process

### Setting Up Development Environment

1. Clone the repository
   ```
   git clone https://github.com/skunkbandit/handyman-kpi-system.git
   cd handyman-kpi-system
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database
   ```
   python scripts/init_database.py
   ```

5. Run the application
   ```
   python backend/run.py
   ```

### Code Style

- Follow PEP 8 guidelines for Python code
- Use 4 spaces for indentation (no tabs)
- Use meaningful variable and function names
- Document code with docstrings

### Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a pull request
- Aim for high code coverage

Run tests with:
```
python tests/run_tests.py
```

## Branching Strategy

- `main` branch is the stable release branch
- Create feature branches from `main` using the format: `feature/description`
- Create bugfix branches using the format: `bugfix/issue-number`

## Commit Guidelines

- Use clear, descriptive commit messages
- Reference issue numbers in commit messages when applicable
- Keep commits focused on single changes

## Code Review Process

- All submissions require review
- Changes may be requested before a pull request is merged
- Reviewers will check for quality, test coverage, and adherence to guidelines

## Documentation

- Update documentation for any changed features
- Add inline comments for complex sections of code
- Keep the README.md updated with any significant changes

Thank you for contributing to the Handyman KPI System!
