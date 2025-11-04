# Fortran Analyzer

A generic framework for analyzing Fortran codebases, designed to help with code understanding, dependency analysis, and preparation for translation to other languages.

## Features

- **Generic Fortran Parsing**: Works with any Fortran codebase (F77, F90, F95, F2003, F2008)
- **Dependency Analysis**: Build module dependency graphs and identify circular dependencies
- **Translation Unit Decomposition**: Break large procedures into manageable chunks for easier porting
- **Call Graph Generation**: Visualize relationships between modules and procedures
- **Multiple Output Formats**: JSON, YAML, GraphML, and interactive HTML visualizations
- **Configurable Templates**: Pre-configured for common project types (CTSM, scientific computing, numerical libraries)
- **Command-Line Interface**: Easy-to-use CLI for batch processing
- **Extensible Architecture**: Easy to customize for specific project needs

## Installation

### Basic Installation

```bash
pip install fortran-analyzer
```

### Installation with Optional Dependencies

For advanced Fortran parsing (recommended):
```bash
pip install fortran-analyzer[fparser]
```

For interactive visualizations:
```bash
pip install fortran-analyzer[interactive]
```

For all features:
```bash
pip install fortran-analyzer[full]
```

### Development Installation

```bash
git clone https://github.com/yourusername/fortran-analyzer.git
cd fortran-analyzer
pip install -e .[dev]
```

## Quick Start

### Command Line Usage

#### Analyze a Fortran Project

```bash
# Auto-detect project type and analyze
fortran-analyzer analyze /path/to/fortran/project --template auto

# Use specific template
fortran-analyzer analyze /path/to/ctsm --template ctsm

# Analyze with custom output directory
fortran-analyzer analyze /path/to/project --output-dir ./analysis_results
```

#### Create Configuration File

```bash
# Create configuration for CTSM project
fortran-analyzer config /path/to/ctsm --template ctsm

# Create generic configuration
fortran-analyzer config /path/to/project --template generic --output my_config.yaml
```

#### Get Project Information

```bash
# Auto-detect project type and list files
fortran-analyzer info /path/to/project --detect --list-files
```

### Python API Usage

#### Simple Analysis

```python
from fortran_analyzer import quick_analyze

# Quick analysis with auto-detection
results = quick_analyze('/path/to/fortran/project')
print(f"Found {results['parsing']['statistics']['total_files']} files")
```

#### Detailed Analysis

```python
from fortran_analyzer import FortranAnalyzer
from fortran_analyzer.config.project_config import create_default_config

# Create configuration
config = create_default_config('/path/to/project', template='scientific_computing')

# Customize configuration
config.max_translation_unit_lines = 100
config.generate_graphs = True

# Create and run analyzer
analyzer = FortranAnalyzer(config)
results = analyzer.analyze()

# Get translation order
translation_order = analyzer.get_translation_order()
print(f"Recommended translation order: {translation_order}")
```

#### Custom Configuration

```python
from fortran_analyzer.config.project_config import FortranProjectConfig
from fortran_analyzer import FortranAnalyzer

# Create custom configuration
config = FortranProjectConfig(
    project_name="My Project",
    project_root="/path/to/project",
    source_dirs=["src", "lib"],
    fortran_extensions=[".f90", ".F90"],
    max_translation_unit_lines=80,
    external_libraries=["netcdf", "mpi"],
    system_modules=["iso_fortran_env", "mpi"]
)

analyzer = FortranAnalyzer(config)
results = analyzer.analyze()
```

## Configuration

### Configuration Templates

The analyzer comes with predefined templates for common project types:

- **`ctsm`**: Community Terrestrial Systems Model
- **`scientific_computing`**: General scientific computing projects
- **`numerical_library`**: Numerical libraries and mathematical software
- **`climate_model`**: Climate and atmospheric models
- **`generic`**: Generic Fortran projects

### Configuration Options

Key configuration parameters:

```yaml
# Project identification
project_name: "My Fortran Project"
project_root: "/path/to/project"

# Source code locations
source_dirs:
  - "src"
  - "lib"

# File patterns
include_patterns:
  - "**/*.f90"
  - "**/*.F90"
exclude_patterns:
  - "**/test_*"

# Fortran settings
fortran_extensions: [".f90", ".F90"]
fortran_standard: "f2003"

# Translation unit settings
max_translation_unit_lines: 150
min_chunk_lines: 50
preserve_interfaces: true

# Dependencies
system_modules:
  - "iso_fortran_env"
external_libraries:
  - "netcdf"
  - "mpi"

# Output settings
output_dir: "analysis_output"
generate_graphs: true
generate_metrics: true
```

## Output

### Generated Files

The analyzer generates several output files:

- **`analysis_results.json`**: Complete analysis results in JSON format
- **`analysis_summary.txt`**: Human-readable summary report
- **`translation_units.json`**: Translation unit decomposition
- **`graphs/`**: Directory containing dependency graphs in various formats
- **`visualizations/`**: Directory containing visualization images and HTML files

### Visualizations

Generated visualizations include:

1. **Module Dependency Graph**: Shows relationships between modules
2. **Translation Units Analysis**: Charts showing unit distribution and complexity
3. **Project Overview**: Summary statistics and metrics
4. **Translation Priority Chart**: Recommended translation order
5. **Interactive Dependency Graph**: Web-based interactive visualization

## Advanced Usage

### Extending the Framework

#### Custom Parser

```python
from fortran_analyzer.parser.fortran_parser import FortranParser

class CustomFortranParser(FortranParser):
    def parse_custom_construct(self, content):
        # Custom parsing logic
        pass
```

#### Custom Analysis

```python
from fortran_analyzer.analysis.call_graph_builder import CallGraphBuilder

class CustomCallGraphBuilder(CallGraphBuilder):
    def analyze_custom_relationships(self, modules):
        # Custom analysis logic
        pass
```

### Integration with Other Tools

#### Export for Other Tools

```python
# Export graphs for Gephi
analyzer.call_graph_builder.export_graphs(
    output_dir, formats=['gexf']
)

# Export for NetworkX processing
module_graph = analyzer.call_graph_builder.get_module_graph()
# Use NetworkX algorithms...
```

#### Continuous Integration

```bash
# Use in CI/CD pipeline
fortran-analyzer analyze $PROJECT_ROOT --template auto --output-dir ./reports
# Upload reports as artifacts
```

## Examples

### CTSM Analysis

```python
from fortran_analyzer import create_analyzer_for_project

# Analyze CTSM biogeophysics
analyzer = create_analyzer_for_project(
    '/path/to/ctsm',
    template='ctsm',
    source_dirs=['src/biogeophys'],  # Focus on specific component
    output_dir='ctsm_biogeophys_analysis'
)

results = analyzer.analyze()

# Get specific recommendations
recommendations = results['recommendations']
for category, items in recommendations.items():
    print(f"{category}: {items}")
```

### Climate Model Comparison

```python
# Compare two climate models
models = ['model_a', 'model_b']
results = {}

for model in models:
    analyzer = create_analyzer_for_project(
        f'/path/to/{model}',
        template='climate_model'
    )
    results[model] = analyzer.analyze()

# Compare statistics
for model in models:
    stats = results[model]['parsing']['statistics']
    print(f"{model}: {stats['total_lines']} lines, {stats['total_modules']} modules")
```

## Troubleshooting

### Common Issues

1. **Parser Errors**: If fparser2 is not available, the analyzer falls back to regex-based parsing
2. **Large Projects**: For very large projects, consider analyzing subdirectories separately
3. **Memory Usage**: Large dependency graphs may require substantial memory

### Performance Tips

- Use `exclude_patterns` to skip unnecessary files
- Focus analysis on specific source directories
- Disable graph generation for faster analysis: `generate_graphs: false`

### Getting Help

- Check the [documentation](https://github.com/yourusername/fortran-analyzer/wiki)
- Open an [issue](https://github.com/yourusername/fortran-analyzer/issues) on GitHub
- Look at the [examples](examples/) directory for usage patterns

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/yourusername/fortran-analyzer.git
cd fortran-analyzer
pip install -e .[dev]
pytest  # Run tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in research, please cite:

```bibtex
@software{fortran_analyzer,
  title={Fortran Analyzer: A Generic Framework for Fortran Code Analysis},
  author={Fortran Analyzer Team},
  year={2024},
  url={https://github.com/yourusername/fortran-analyzer}
}
```

## Acknowledgments

- Built with [NetworkX](https://networkx.org/) for graph analysis
- Optional integration with [fparser2](https://github.com/stfc/fparser) for advanced parsing
- Visualizations powered by [Matplotlib](https://matplotlib.org/) and [Plotly](https://plotly.com/)
- Inspired by the need to modernize legacy Fortran codebases