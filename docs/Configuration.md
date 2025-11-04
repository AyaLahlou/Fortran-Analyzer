# Configuration Guide

This guide explains how to configure the Fortran Analyzer for different types of projects and use cases.

## Configuration Overview

The Fortran Analyzer uses YAML configuration files to define how your project should be analyzed. The configuration system is designed to be flexible and support a wide variety of Fortran projects.

## Basic Configuration Structure

```yaml
# Project identification
project_name: "My Fortran Project"
project_root: "/path/to/project"

# Source code organization
source_dirs:
  - "src"
  - "lib"

# File patterns
include_patterns:
  - "**/*.f90"
  - "**/*.F90"
exclude_patterns: []
exclude_dirs: []

# Fortran language settings
fortran_extensions: [".f90", ".F90"]
fortran_standard: "f2003"
case_sensitive: false

# Analysis parameters
max_translation_unit_lines: 150
min_chunk_lines: 50
preserve_interfaces: true
track_dependencies: true

# External dependencies
system_modules: []
external_libraries: []

# Output settings
output_dir: "analysis_output"
generate_graphs: true
generate_metrics: true
```

## Configuration Templates

### Available Templates

The analyzer provides several predefined templates:

1. **`ctsm`** - Community Terrestrial Systems Model
2. **`scientific_computing`** - General scientific computing projects
3. **`numerical_library`** - Mathematical and numerical libraries
4. **`climate_model`** - Climate and atmospheric models
5. **`generic`** - Generic Fortran projects

### Using Templates

#### Command Line
```bash
# Create config from template
fortran-analyzer config /path/to/project --template ctsm

# Analyze with template
fortran-analyzer analyze /path/to/project --template scientific_computing
```

#### Python API
```python
from fortran_analyzer.config.project_config import ConfigurationManager

# Create from template
manager = ConfigurationManager()
config = manager.create_config_from_template('ctsm', '/path/to/project')

# With overrides
config = manager.create_config_from_template(
    'generic', 
    '/path/to/project',
    overrides={'max_translation_unit_lines': 100}
)
```

## Detailed Configuration Options

### Project Identification

```yaml
project_name: "Community Terrestrial Systems Model"
project_root: "/home/user/ctsm"
```

- **`project_name`**: Human-readable name for reports and outputs
- **`project_root`**: Absolute path to the project root directory

### Source Code Organization

```yaml
source_dirs:
  - "src/biogeophys"
  - "src/biogeochem"
  - "src/main"
  - "src/utils"

include_dirs:
  - "include"
  - "modules"

exclude_dirs:
  - "src/external"
  - "tests"
  - "examples"
```

- **`source_dirs`**: Directories containing Fortran source code to analyze
- **`include_dirs`**: Additional directories for include files and modules
- **`exclude_dirs`**: Directories to skip during analysis

### File Pattern Matching

```yaml
# Include patterns (glob format)
include_patterns:
  - "**/*.F90"
  - "**/*.f90"
  - "src/**/*.f95"

# Exclude patterns
exclude_patterns:
  - "**/test_*"
  - "**/example_*"
  - "**/*_template*"

# File extensions to consider
fortran_extensions: [".f90", ".F90", ".f95", ".F95", ".f", ".F"]
```

### Fortran Language Settings

```yaml
fortran_standard: "f2003"  # f77, f90, f95, f2003, f2008
case_sensitive: false      # Whether identifiers are case-sensitive
```

Supported standards:
- **`f77`**: FORTRAN 77
- **`f90`**: Fortran 90
- **`f95`**: Fortran 95
- **`f2003`**: Fortran 2003 (default)
- **`f2008`**: Fortran 2008

### Translation Unit Settings

```yaml
max_translation_unit_lines: 150  # Maximum lines per unit
min_chunk_lines: 50              # Minimum size for code chunks
preserve_interfaces: true        # Keep interfaces intact
```

These settings control how large procedures are broken down:
- **`max_translation_unit_lines`**: Procedures larger than this are split
- **`min_chunk_lines`**: Minimum size for inner translation units
- **`preserve_interfaces`**: Whether to keep interface definitions together

### Dependency Analysis

```yaml
track_dependencies: true

# System/intrinsic modules
system_modules:
  - "iso_fortran_env"
  - "iso_c_binding" 
  - "ieee_arithmetic"

# External libraries
external_libraries:
  - "netcdf"
  - "mpi"
  - "lapack"
  - "blas"
```

- **`system_modules`**: Modules provided by the compiler/system
- **`external_libraries`**: Third-party libraries the project depends on

### Project-Specific Naming Conventions

```yaml
naming_conventions:
  module_suffix: "Mod"           # e.g., WaterStateTypeMod
  type_suffix: "_type"           # e.g., waterstate_type
  instance_suffix: "_inst"       # e.g., waterstate_inst
  public_prefix: ""              # Prefix for public entities
  private_prefix: ""             # Prefix for private entities
```

### Output and Visualization

```yaml
output_dir: "analysis_results"
generate_graphs: true
generate_metrics: true

visualization:
  node_color: "lightblue"
  edge_color: "gray"
  font_size: 10
  figure_size: [12, 8]
  show_labels: true
```

## Project-Specific Configurations

### CTSM Configuration

```yaml
project_name: "Community Terrestrial Systems Model"
project_root: "/path/to/ctsm"

source_dirs:
  - "src/biogeophys"
  - "src/biogeochem"
  - "src/main"
  - "src/utils"

fortran_extensions: [".F90"]
fortran_standard: "f2003"

system_modules:
  - "shr_kind_mod"
  - "shr_const_mod"
  - "clm_varpar"
  - "clm_varctl"
  - "clm_varcon"
  - "decompMod"
  - "abortutils"

external_libraries:
  - "netcdf"
  - "esmf"
  - "mpi"

naming_conventions:
  module_suffix: "Mod"
  type_suffix: "_type"
  instance_suffix: "_inst"

max_translation_unit_lines: 150
```

### Scientific Computing Configuration

```yaml
project_name: "Scientific Computing Project"
project_root: "/path/to/project"

source_dirs:
  - "src"
  - "modules"

fortran_extensions: [".f90", ".F90", ".f95"]
fortran_standard: "f2008"

system_modules:
  - "iso_fortran_env"
  - "iso_c_binding"
  - "ieee_arithmetic"

external_libraries:
  - "lapack"
  - "blas"
  - "mpi"
  - "hdf5"

max_translation_unit_lines: 100
preserve_interfaces: true
```

### Numerical Library Configuration

```yaml
project_name: "Numerical Library"
project_root: "/path/to/library"

source_dirs:
  - "src"
  - "lib"

include_dirs:
  - "include"

fortran_extensions: [".f90", ".F90", ".f95"]
fortran_standard: "f2008"
case_sensitive: true

# Smaller units for library functions
max_translation_unit_lines: 80
min_chunk_lines: 20

external_libraries:
  - "lapack"
  - "blas"

naming_conventions:
  public_prefix: "lib_"
  private_prefix: "priv_"
```

## Advanced Configuration

### Custom File Filtering

```yaml
# Complex include/exclude patterns
include_patterns:
  - "src/core/**/*.f90"
  - "src/physics/**/*.F90"
  - "!src/physics/experimental/**"  # Exclude experimental code

exclude_patterns:
  - "**/obsolete/**"
  - "**/*_old.*"
  - "**/prototype_*"

# Custom validation
custom_validation:
  max_file_size: 10000  # Skip files larger than 10k lines
  required_modules: ["precision_mod"]  # Warn if not found
```

### Multi-Component Projects

For projects with multiple components:

```yaml
# Analyze components separately
components:
  physics:
    source_dirs: ["src/physics"]
    max_translation_unit_lines: 120
  
  dynamics:
    source_dirs: ["src/dynamics"] 
    max_translation_unit_lines: 100
  
  io:
    source_dirs: ["src/io"]
    max_translation_unit_lines: 80
```

### Environment-Specific Settings

```yaml
# Development vs production settings
environments:
  development:
    generate_graphs: true
    verbose_output: true
    
  production:
    generate_graphs: false
    optimize_for_speed: true
```

## Validation and Testing

### Configuration Validation

```python
from fortran_analyzer.config.project_config import FortranProjectConfig

config = FortranProjectConfig.from_yaml('my_config.yaml')

# Validate configuration
if config.validate():
    print("Configuration is valid")
else:
    print("Configuration has errors")
```

### Testing Configuration

```bash
# Test configuration without full analysis
fortran-analyzer info /path/to/project --config my_config.yaml

# Dry run
fortran-analyzer analyze /path/to/project --config my_config.yaml --dry-run
```

## Best Practices

### 1. Start with Templates

Always start with the closest template and customize:

```bash
# Create base config
fortran-analyzer config /path/to/project --template scientific_computing

# Edit the generated config file
vim fortran_analyzer_config.yaml
```

### 2. Incremental Configuration

Test configuration changes incrementally:

```python
# Test with small subset first
config.source_dirs = ["src/small_module"]
analyzer = FortranAnalyzer(config)
results = analyzer.analyze()
```

### 3. Use Version Control

Keep configuration files in version control:

```bash
git add fortran_analyzer_config.yaml
git commit -m "Add Fortran analyzer configuration"
```

### 4. Document Custom Settings

Add comments to explain project-specific choices:

```yaml
# Custom settings for legacy FORTRAN 77 compatibility
fortran_standard: "f77"
case_sensitive: false

# Large translation units due to legacy code structure
max_translation_unit_lines: 200  # TODO: Refactor to smaller units
```

### 5. Environment-Specific Configs

Use different configs for different purposes:

```
configs/
├── development.yaml      # Full analysis with graphs
├── ci.yaml              # Fast analysis for CI/CD
└── production.yaml      # Optimized for batch processing
```

## Troubleshooting Configuration

### Common Issues

1. **No files found**: Check `source_dirs` and `include_patterns`
2. **Parser errors**: Verify `fortran_standard` setting
3. **Missing dependencies**: Add to `system_modules` or `external_libraries`
4. **Large memory usage**: Reduce scope or disable graph generation

### Debug Configuration

```bash
# Show what files would be analyzed
fortran-analyzer info /path/to/project --list-files --config my_config.yaml

# Verbose analysis
fortran-analyzer analyze /path/to/project --config my_config.yaml --verbose
```

### Configuration Validation Script

```python
#!/usr/bin/env python3
"""Validate Fortran analyzer configuration."""

import sys
from pathlib import Path
from fortran_analyzer.config.project_config import load_config

def validate_config(config_path):
    try:
        config = load_config(config_path)
        
        if config.validate():
            print(f"✓ Configuration {config_path} is valid")
            return True
        else:
            print(f"✗ Configuration {config_path} has errors")
            return False
            
    except Exception as e:
        print(f"✗ Failed to load {config_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_config.py <config.yaml>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    if validate_config(config_path):
        sys.exit(0)
    else:
        sys.exit(1)
```