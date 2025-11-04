# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Fortran Analyzer, please follow these steps:

### Private Disclosure

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. Send an email to the maintainers with details about the vulnerability
3. Include steps to reproduce the issue if possible
4. Provide any relevant technical details

### What to Include

Please include the following information in your report:

- **Description**: Brief description of the vulnerability
- **Impact**: Potential impact and affected components
- **Reproduction Steps**: Step-by-step instructions to reproduce
- **Environment**: Python version, OS, and package versions
- **Proof of Concept**: If available, minimal code demonstrating the issue

### Response Timeline

- **Initial Response**: Within 48 hours of receiving the report
- **Confirmation**: Within 1 week of initial response
- **Fix Timeline**: Security fixes will be prioritized and released as soon as possible
- **Disclosure**: Public disclosure will be coordinated after a fix is available

### Security Considerations

When using Fortran Analyzer, please be aware of:

#### Input Validation
- The tool processes Fortran source code files
- Malicious Fortran code could potentially cause issues during parsing
- Always use trusted source code inputs

#### File System Access
- The analyzer reads files from specified directories
- Ensure appropriate file system permissions
- Be cautious when analyzing code from untrusted sources

#### Dependency Security
- Keep dependencies up to date
- Regularly check for security updates in:
  - NetworkX
  - Matplotlib
  - PyYAML
  - Optional dependencies (fparser2, Plotly)

#### Output Security
- Generated output files may contain sensitive project information
- Review output before sharing or publishing
- Be cautious with generated visualizations and reports

## Best Practices

### For Users
1. **Keep Updated**: Always use the latest version of Fortran Analyzer
2. **Trusted Sources**: Only analyze code from trusted sources
3. **Review Output**: Check generated files before sharing
4. **Secure Environment**: Run analysis in secure, isolated environments for untrusted code

### For Contributors
1. **Code Review**: All code changes undergo security review
2. **Dependencies**: Carefully evaluate new dependencies
3. **Testing**: Include security considerations in testing
4. **Documentation**: Document security implications of new features

## Security Features

### Current Security Measures
- No execution of analyzed Fortran code
- Read-only access to source files
- Sandboxed parsing operations
- No network communication required
- Local file system access only

### Planned Security Enhancements
- Input validation improvements
- Enhanced error handling for malformed inputs
- Optional sandboxing for untrusted code analysis
- Security audit logging

## Contact

For security-related questions or concerns:
- Create a private security advisory on GitHub
- Contact the maintainers directly for sensitive issues
- Check existing security advisories for known issues

Thank you for helping keep Fortran Analyzer secure!