# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-11-04

### Added
- Initial release of Fortran Analyzer
- Generic Fortran parsing support (F77-F2008)
- Module dependency analysis and visualization
- Translation unit decomposition for code modernization
- Call graph generation with NetworkX
- Multiple output formats (JSON, YAML, GraphML, HTML)
- Configurable project templates (CTSM, scientific computing, numerical libraries)
- Command-line interface with comprehensive options
- Python API for programmatic usage
- Interactive visualizations with Plotly
- Circular dependency detection
- External dependency analysis
- Project complexity metrics
- Translation priority recommendations
- Comprehensive test suite
- Detailed documentation and examples

### Features
- **Configuration System**: Template-based setup for different project types
- **Parser Engine**: Dual approach with fparser2 integration and regex fallback
- **Analysis Components**: Call graph builder, dependency analyzer, translation decomposer
- **Visualization Tools**: Static and interactive charts with multiple export formats
- **CLI Interface**: Easy-to-use command-line tools for batch processing
- **Python API**: Programmatic access for integration with other tools
- **Project Templates**: Pre-configured settings for common Fortran project types
- **Quality Metrics**: Code complexity analysis and translation recommendations

### Supported Project Types
- Community Land Model (CLM/CTSM)
- Scientific computing applications
- Numerical libraries
- Climate and atmospheric models
- Generic Fortran projects

### Dependencies
- Python 3.8+
- NetworkX for graph analysis
- Matplotlib for visualization
- PyYAML for configuration
- Optional: fparser2 for advanced parsing
- Optional: Plotly for interactive visualizations

[Unreleased]: https://github.com/yourusername/fortran-analyzer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/fortran-analyzer/releases/tag/v1.0.0