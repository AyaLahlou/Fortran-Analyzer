# Contributing to Fortran Analyzer

We welcome contributions to the Fortran Analyzer project! This document provides guidelines for contributing.

## Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/fortran-analyzer.git
   cd fortran-analyzer
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

## Contributing Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add type hints where appropriate
- Keep functions focused and modular

### Code Formatting

We use `black` for code formatting:
```bash
black src/ tests/
```

### Linting

We use `flake8` for linting:
```bash
flake8 src/ tests/
```

### Type Checking

We use `mypy` for type checking:
```bash
mypy src/
```

## Types of Contributions

### Bug Reports

When filing a bug report, please include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Relevant error messages

### Feature Requests

When proposing new features:
- Explain the use case
- Describe the proposed solution
- Consider backward compatibility
- Provide examples if possible

### Code Contributions

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Documentation Improvements

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update API documentation
- Add examples for new features

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/

# Run specific test file
pytest tests/test_parser.py

# Run tests matching pattern
pytest -k "test_parse"
```

### Writing Tests

- Add tests for all new functionality
- Use descriptive test names
- Include edge cases and error conditions
- Mock external dependencies when appropriate

Example test structure:
```python
def test_parser_handles_module_correctly():
    """Test that parser correctly identifies modules."""
    # Arrange
    fortran_code = """
    module test_module
        implicit none
    contains
        subroutine test_sub()
        end subroutine
    end module
    """
    
    # Act
    result = parse_fortran_content(fortran_code)
    
    # Assert
    assert len(result.modules) == 1
    assert result.modules[0].name == "test_module"
```

## Project Structure

```
fortran-analyzer/
├── src/                    # Source code
│   ├── config/            # Configuration management
│   ├── parser/            # Fortran parsing
│   ├── analysis/          # Code analysis
│   ├── visualization/     # Visualization tools
│   └── cli.py            # Command-line interface
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # Main documentation
```

## Areas for Contribution

### High Priority
- Support for additional Fortran standards (F2018, F2023)
- Performance optimization for large codebases
- Enhanced visualization options
- More project templates

### Medium Priority
- Integration with additional parsing tools
- Export to more graph formats
- Improved error handling and reporting
- Additional analysis metrics

### Low Priority
- GUI interface
- Plugin system
- Cloud deployment options
- Integration with IDEs

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors list

## Questions?

- Open an issue for questions about contributing
- Check existing issues and discussions
- Review the documentation in the `docs/` directory

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

Thank you for contributing to Fortran Analyzer! 🚀