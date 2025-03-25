# Contributing to the Handyman KPI System

Thank you for considering contributing to the Handyman KPI System! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment](#development-environment)
  - [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
  - [Branching Strategy](#branching-strategy)
  - [Commit Messages](#commit-messages)
  - [Pull Requests](#pull-requests)
- [Coding Standards](#coding-standards)
  - [Python Style Guide](#python-style-guide)
  - [JavaScript Style Guide](#javascript-style-guide)
  - [HTML/CSS Style Guide](#htmlcss-style-guide)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Tracking](#issue-tracking)
- [Review Process](#review-process)
- [Release Process](#release-process)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to adhere to these guidelines to ensure a positive and inclusive environment for everyone.

## Getting Started

### Development Environment

1. **Fork and Clone the Repository**

```bash
git clone https://github.com/your-username/handyman-kpi-system.git
cd handyman-kpi-system
```

2. **Set Up Development Environment**

#### Using Docker (Recommended)

```bash
# Create environment file from template
cp environments/.env.development .env

# Start the development containers
docker-compose -f docker-compose.dev.yml up -d

# Initialize the database
docker-compose -f docker-compose.dev.yml exec web python scripts/init_database.py

# Import sample data
docker-compose -f docker-compose.dev.yml exec web python scripts/import_excel_data.py --file "Craftman Developement Score Card.xlsx"

# Create admin user
docker-compose -f docker-compose.dev.yml exec web python scripts/create_admin.py
```

#### Traditional Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create environment file from template
cp environments/.env.development .env

# Initialize the database
python scripts/init_database.py

# Import sample data
python scripts/import_excel_data.py --file "Craftman Developement Score Card.xlsx"

# Create admin user
python scripts/create_admin.py

# Run the development server
python run.py
```

3. **Access the Application**

- Web interface: http://localhost:5000
- API documentation: http://localhost:5000/api/docs

### Project Structure

The project follows a modular structure:

```
handyman-kpi-system/
├── kpi-system/                # Main application code
│   ├── backend/               # Backend code
│   │   ├── app/               # Application package
│   │   │   ├── models/        # Database models
│   │   │   ├── routes/        # Route blueprints
│   │   │   ├── static/        # Static assets
│   │   │   ├── templates/     # HTML templates
│   │   │   ├── utils/         # Utility functions
│   │   │   └── __init__.py    # Application factory
│   │   └── run.py             # Development entry point
│   ├── config.py              # Configuration settings
│   ├── database/              # Database scripts
│   ├── docs/                  # Documentation
│   ├── frontend/              # Frontend code (if separate)
│   └── requirements.txt       # Dependencies
├── database/                  # Database migration files
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── ui/                    # UI tests
├── .env.example               # Environment variables template
├── docker-compose.yml         # Production Docker setup
├── docker-compose.dev.yml     # Development Docker setup
└── Dockerfile                 # Docker image definition
```

## Development Workflow

### Branching Strategy

We follow the GitFlow branching model:

- `main`: Production-ready code
- `develop`: Integration branch for feature development
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches
- `release/*`: Release preparation branches
- `hotfix/*`: Production hotfix branches

### Creating a New Feature

1. Create a new branch from `develop`:

```bash
git checkout develop
git pull
git checkout -b feature/your-feature-name
```

2. Implement your changes and commit them (see [Commit Messages](#commit-messages))

3. Push your branch:

```bash
git push -u origin feature/your-feature-name
```

4. Create a pull request to merge your changes into `develop`

### Fixing a Bug

1. Create a new branch from `develop` (or `main` for critical bugs):

```bash
git checkout develop
git pull
git checkout -b fix/your-bug-fix
```

2. Implement your fix and commit it

3. Push your branch:

```bash
git push -u origin fix/your-bug-fix
```

4. Create a pull request to merge your changes

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or fixing tests
- `chore`: Changes to the build process or auxiliary tools

Examples:
```
feat(evaluations): add skill comparison visualization
fix(auth): resolve password reset token expiration issue
docs(api): update endpoints documentation
test(models): add tests for employee model validation
```

### Pull Requests

Pull request titles should follow the same convention as commit messages.

Each pull request should:
- Reference related issues
- Include a clear description of changes
- Provide instructions for testing
- Pass all automated checks
- Be reviewed by at least one maintainer

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) formatter
- Maximum line length: 88 characters
- Use docstrings for all functions, classes, and modules
- Maintain a comprehensive test suite

Linting and formatting:
```bash
# Format code
black kpi-system/

# Run linters
flake8 kpi-system/
pylint kpi-system/
```

### JavaScript Style Guide

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ESLint with the project configuration
- Prefer ES6+ features
- Use JSDoc for documentation

Linting and formatting:
```bash
# Format code
npx prettier --write "kpi-system/backend/app/static/js/**/*.js"

# Run linters
npx eslint "kpi-system/backend/app/static/js/**/*.js"
```

### HTML/CSS Style Guide

- Follow [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html)
- Use semantic HTML5 elements
- Use Bootstrap 5 for consistent styling
- Maintain responsive design

## Testing

All changes must be accompanied by appropriate tests:

- New features: Unit and integration tests
- Bug fixes: Regression tests
- UI changes: UI tests for critical workflows

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test types
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/ui/

# Run with coverage
python -m pytest --cov=app
```

See [Testing Framework Documentation](testing/testing-framework.md) for details.

## Documentation

Documentation is a critical part of the project. Update documentation when you:
- Add or modify features
- Change APIs
- Update dependencies
- Refactor code structure

Documentation is organized into:
- User documentation (in `docs/user/`)
- Administrator documentation (in `docs/admin/`)
- Developer documentation (in `docs/developer/`)
- API reference (in `docs/developer/api/`)
- Code comments and docstrings

## Issue Tracking

We use GitHub Issues for tracking work:

- **Bug Reports**: Include steps to reproduce, expected vs. actual behavior, and environment details
- **Feature Requests**: Describe the feature, its benefits, and implementation suggestions
- **Documentation Improvements**: Identify what needs clarification or expansion

Use these labels:
- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed

## Review Process

All code must be reviewed before merging:

1. Automated checks must pass (tests, linting, etc.)
2. At least one core maintainer must approve
3. Code must meet standards for:
   - Functionality
   - Quality
   - Test coverage
   - Documentation

### Review Checklist

Reviewers look for:
- [ ] Code works as intended
- [ ] Follows coding standards
- [ ] Appropriate test coverage
- [ ] Documentation is updated
- [ ] No security issues
- [ ] No performance regressions

## Release Process

The release process follows these steps:

1. Create a release branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b release/v1.x.0
   ```

2. Prepare for release:
   - Update version numbers
   - Finalize documentation
   - Run final tests
   - Create migration scripts if needed

3. Merge to `main` and tag:
   ```bash
   git checkout main
   git merge --no-ff release/v1.x.0
   git tag -a v1.x.0 -m "Release v1.x.0"
   git push origin main --tags
   ```

4. Merge back to `develop`:
   ```bash
   git checkout develop
   git merge --no-ff release/v1.x.0
   git push origin develop
   ```

5. Clean up:
   ```bash
   git branch -d release/v1.x.0
   ```

## Getting Help

If you need help with contributing:
- Check the documentation
- Ask questions in GitHub Issues
- Contact the maintainers

Thank you for contributing to the Handyman KPI System!
