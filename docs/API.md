# API Documentation

## Core Classes

### FortranAnalyzer

Main analyzer class that orchestrates the analysis workflow.

```python
class FortranAnalyzer:
    def __init__(self, config: FortranProjectConfig)
    def analyze(self, save_results: bool = True) -> Dict[str, Any]
    def get_results(self) -> Dict[str, Any]
    def get_translation_order(self) -> List[str]
    def get_summary_statistics(self) -> Dict[str, Any]
```

#### Methods

**`analyze(save_results=True)`**
- Performs complete analysis of the Fortran codebase
- Returns: Dictionary containing all analysis results
- Parameters:
  - `save_results`: Whether to save results to files

**`get_translation_order()`**
- Returns recommended order for translating modules
- Returns: List of module names in dependency order

**`get_summary_statistics()`**
- Returns high-level project statistics
- Returns: Dictionary with counts of files, lines, modules, etc.

### FortranProjectConfig

Configuration class that defines analysis parameters.

```python
@dataclass
class FortranProjectConfig:
    project_name: str
    project_root: str
    source_dirs: List[str]
    fortran_extensions: List[str] = ['.f90', '.F90']
    max_translation_unit_lines: int = 150
    # ... more fields
```

#### Key Fields

- **`project_name`**: Human-readable project name
- **`project_root`**: Absolute path to project root directory
- **`source_dirs`**: List of source directories to analyze
- **`fortran_extensions`**: File extensions to include
- **`max_translation_unit_lines`**: Maximum size for translation units
- **`system_modules`**: List of system modules to treat as external
- **`external_libraries`**: List of external library dependencies

#### Methods

**`from_yaml(yaml_path)`** (classmethod)
- Load configuration from YAML file
- Parameters: `yaml_path` - Path to YAML configuration file

**`validate()`**
- Validate configuration settings
- Returns: Boolean indicating if configuration is valid

### ConfigurationManager

Manages configuration templates and project type detection.

```python
class ConfigurationManager:
    @classmethod
    def create_config_from_template(cls, template_name: str, 
                                  project_root: str, 
                                  overrides: Optional[Dict] = None) -> FortranProjectConfig
    
    @classmethod
    def auto_detect_project_type(cls, project_root: str) -> str
    
    @classmethod
    def list_templates(cls) -> List[str]
```

#### Methods

**`create_config_from_template(template_name, project_root, overrides=None)`**
- Create configuration from predefined template
- Parameters:
  - `template_name`: Name of template ('ctsm', 'generic', etc.)
  - `project_root`: Path to project root
  - `overrides`: Dictionary of configuration overrides

**`auto_detect_project_type(project_root)`**
- Automatically detect project type from directory structure
- Returns: Template name that best matches the project

## Analysis Components

### FortranParser

Parses Fortran source files and extracts structural information.

```python
class FortranParser:
    def __init__(self, config: FortranProjectConfig)
    def parse_project(self) -> Dict
    def find_fortran_files(self) -> List[Path]
    def parse_file(self, file_path: Path) -> Optional[ModuleInfo]
```

### CallGraphBuilder

Builds dependency graphs and analyzes relationships.

```python
class CallGraphBuilder:
    def __init__(self, config: FortranProjectConfig)
    def build_module_dependency_graph(self, modules: Dict[str, ModuleInfo]) -> nx.DiGraph
    def build_entity_call_graph(self, modules: Dict[str, ModuleInfo]) -> nx.DiGraph
    def analyze_dependencies(self) -> Dict[str, Any]
    def get_translation_order(self) -> List[str]
```

### TranslationUnitDecomposer

Breaks down large modules into manageable translation units.

```python
class TranslationUnitDecomposer:
    def __init__(self, config: FortranProjectConfig)
    def decompose_modules(self, modules: Dict[str, ModuleInfo]) -> List[TranslationUnit]
    def get_statistics(self) -> Dict[str, Any]
```

### FortranVisualizer

Creates visualizations of analysis results.

```python
class FortranVisualizer:
    def __init__(self, config: FortranProjectConfig)
    def visualize_module_dependencies(self, call_graph_builder: CallGraphBuilder) -> Path
    def visualize_translation_units(self, translation_units: List[TranslationUnit]) -> Path
    def generate_all_visualizations(self, analysis_results: Dict[str, Any]) -> Dict[str, Path]
```

## Data Models

### ModuleInfo

Information about a Fortran module.

```python
@dataclass
class ModuleInfo:
    name: str
    file_path: str
    uses: List[Dict[str, Union[str, List[str]]]]
    subroutines: List[str]
    functions: List[str]
    types: List[str]
    variables: List[str]
    interfaces: List[str]
    line_count: int
    entities: List[FortranEntity]
```

### FortranEntity

Represents a Fortran entity (subroutine, function, type, etc.).

```python
@dataclass
class FortranEntity:
    name: str
    entity_type: str  # 'module', 'subroutine', 'function', 'type', 'variable'
    file_path: str
    line_start: int
    line_end: int
    parent: Optional[str] = None
    attributes: Dict[str, Any] = None
```

### TranslationUnit

Represents a unit of code for translation.

```python
@dataclass
class TranslationUnit:
    id: str
    unit_type: str  # 'root', 'inner', 'interface', 'type_definition'
    entity_name: str
    entity_type: str
    module_name: str
    file_path: str
    line_start: int
    line_end: int
    line_count: int
    complexity_score: float = 0.0
    priority: int = 0
    estimated_effort: str = "medium"
```

## Utility Functions

### Quick Analysis Functions

```python
def quick_analyze(project_root: str, template: str = 'auto', 
                 output_dir: Optional[str] = None) -> Dict[str, Any]
```

Perform a quick analysis with minimal configuration.

```python
def create_analyzer_for_project(project_root: str, template: str = 'auto',
                               **config_overrides) -> FortranAnalyzer
```

Create analyzer instance with template and overrides.

### Configuration Functions

```python
def load_config(config_path: Union[str, Path]) -> FortranProjectConfig
```

Load configuration from YAML or JSON file.

```python
def create_default_config(project_root: str, template: str = 'generic') -> FortranProjectConfig
```

Create default configuration for a project.

## Error Handling

### Common Exceptions

- **`ValueError`**: Invalid configuration or parameters
- **`FileNotFoundError`**: Required files or directories not found
- **`ParseError`**: Fortran parsing failures (when using fparser2)

### Best Practices

1. Always validate configuration before analysis:
   ```python
   if not config.validate():
       raise ValueError("Invalid configuration")
   ```

2. Handle missing optional dependencies:
   ```python
   try:
       from fparser2 import ...
   except ImportError:
       # Fall back to regex parsing
   ```

3. Check for empty results:
   ```python
   results = analyzer.analyze()
   if not results['parsing']['modules']:
       logger.warning("No modules found")
   ```

## Performance Considerations

### Memory Usage

- Large projects may require substantial memory for dependency graphs
- Consider analyzing subdirectories separately for very large codebases
- Use `exclude_patterns` to skip unnecessary files

### Processing Time

- Parsing time scales roughly linearly with number of files
- Graph analysis time depends on dependency complexity
- Visualization generation can be time-consuming for large graphs

### Optimization Tips

1. **Selective Analysis**: Focus on specific source directories
2. **Disable Features**: Turn off graph generation for faster analysis
3. **Parallel Processing**: The framework is designed to be easily parallelizable

## Extension Points

### Custom Parsers

Extend `FortranParser` to handle project-specific constructs:

```python
class CustomParser(FortranParser):
    def parse_custom_directive(self, line):
        # Handle custom preprocessor directives
        pass
```

### Custom Analysis

Extend analysis components for specialized metrics:

```python
class CustomAnalyzer(CallGraphBuilder):
    def calculate_custom_metrics(self, graph):
        # Calculate domain-specific metrics
        pass
```

### Custom Visualizations

Add new visualization types:

```python
class CustomVisualizer(FortranVisualizer):
    def create_custom_plot(self, data):
        # Create specialized visualizations
        pass
```

## Integration Examples

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Analyze Fortran Code
  run: |
    fortran-analyzer analyze . --template auto --output-dir reports
    # Upload reports as artifacts
```

### Jupyter Notebook Integration

```python
# In Jupyter notebook
from fortran_analyzer import quick_analyze
import matplotlib.pyplot as plt

results = quick_analyze('/path/to/project')
# Create custom plots with results
```

### Script Integration

```python
#!/usr/bin/env python3
# Automated analysis script
import sys
from fortran_analyzer import create_analyzer_for_project

def main():
    if len(sys.argv) != 2:
        print("Usage: analyze.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    analyzer = create_analyzer_for_project(project_path, template='auto')
    results = analyzer.analyze()
    
    # Generate report
    stats = analyzer.get_summary_statistics()
    print(f"Analysis complete: {stats}")

if __name__ == '__main__':
    main()
```