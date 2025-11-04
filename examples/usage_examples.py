"""
Example usage scripts for the Fortran Analyzer.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import the analyzer
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fortran_analyzer import FortranAnalyzer, create_analyzer_for_project, quick_analyze
from fortran_analyzer.config.project_config import ConfigurationManager


def example_ctsm_analysis():
    """Example: Analyze CTSM codebase."""
    print("Example: CTSM Analysis")
    print("=" * 50)
    
    # Path to CTSM (update this to your actual CTSM path)
    ctsm_path = "/path/to/ctsm"
    
    if not Path(ctsm_path).exists():
        print(f"CTSM path does not exist: {ctsm_path}")
        print("Please update the path in this example")
        return
    
    # Create analyzer with CTSM template
    analyzer = create_analyzer_for_project(
        ctsm_path,
        template='ctsm',
        output_dir='ctsm_analysis_results'
    )
    
    # Run analysis
    results = analyzer.analyze()
    
    # Print summary
    summary = analyzer.get_summary_statistics()
    print(f"Analysis complete!")
    print(f"  Files: {summary['files']}")
    print(f"  Lines: {summary['lines']:,}")
    print(f"  Modules: {summary['modules']}")
    print(f"  Translation units: {summary['translation_units']}")


def example_scientific_computing_analysis():
    """Example: Analyze a scientific computing project."""
    print("Example: Scientific Computing Analysis")
    print("=" * 50)
    
    # Use a hypothetical scientific computing project
    project_path = "/path/to/scientific/project"
    
    # Quick analysis with auto-detection
    try:
        results = quick_analyze(
            project_path,
            template='scientific_computing',
            output_dir='sci_analysis_results'
        )
        
        print("Quick analysis complete!")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        print("This is expected if the path doesn't exist")


def example_configuration_creation():
    """Example: Create configuration files."""
    print("Example: Configuration Creation")
    print("=" * 50)
    
    manager = ConfigurationManager()
    
    # List available templates
    print("Available templates:")
    for template in manager.list_templates():
        print(f"  - {template}")
    
    # Create config for a generic project
    config = manager.create_config_from_template(
        'generic',
        '/path/to/project',
        overrides={
            'project_name': 'My Fortran Project',
            'max_translation_unit_lines': 100
        }
    )
    
    # Save configuration
    config.to_yaml('my_project_config.yaml')
    print("Configuration saved to: my_project_config.yaml")


def example_custom_analysis():
    """Example: Custom analysis with specific settings."""
    print("Example: Custom Analysis")
    print("=" * 50)
    
    from fortran_analyzer.config.project_config import FortranProjectConfig
    
    # Create custom configuration
    config = FortranProjectConfig(
        project_name="Custom Project",
        project_root="/path/to/project",
        source_dirs=["src", "modules"],
        fortran_extensions=[".f90", ".F90"],
        max_translation_unit_lines=80,
        generate_graphs=True,
        external_libraries=["netcdf", "mpi"]
    )
    
    # Create analyzer with custom config
    analyzer = FortranAnalyzer(config)
    
    print(f"Created analyzer for: {config.project_name}")
    print(f"Source directories: {config.source_dirs}")
    print(f"Max unit lines: {config.max_translation_unit_lines}")


def example_project_info():
    """Example: Get project information without full analysis."""
    print("Example: Project Information")
    print("=" * 50)
    
    manager = ConfigurationManager()
    
    # Detect project type
    project_path = "."  # Current directory
    detected_type = manager.auto_detect_project_type(project_path)
    print(f"Detected project type: {detected_type}")
    
    # Get template info
    template_info = manager.get_template_info(detected_type)
    print("Template settings:")
    for key, value in template_info.items():
        print(f"  {key}: {value}")


def example_translation_workflow():
    """Example: Complete translation workflow."""
    print("Example: Translation Workflow")
    print("=" * 50)
    
    project_path = "/path/to/project"
    
    if not Path(project_path).exists():
        print(f"Project path does not exist: {project_path}")
        return
    
    # Step 1: Analyze project
    analyzer = create_analyzer_for_project(project_path, template='auto')
    results = analyzer.analyze()
    
    # Step 2: Get translation order
    translation_order = analyzer.get_translation_order()
    print(f"Recommended translation order ({len(translation_order)} modules):")
    for i, module in enumerate(translation_order[:10], 1):  # Show first 10
        print(f"  {i}. {module}")
    
    if len(translation_order) > 10:
        print(f"  ... and {len(translation_order) - 10} more")
    
    # Step 3: Get recommendations
    recommendations = results.get('recommendations', {})
    if recommendations:
        print("\nRecommendations:")
        for category, items in recommendations.items():
            if items:
                print(f"  {category.replace('_', ' ').title()}:")
                for item in items:
                    print(f"    - {item}")


if __name__ == "__main__":
    print("Fortran Analyzer Examples")
    print("=" * 50)
    
    examples = [
        ("Configuration Creation", example_configuration_creation),
        ("Project Information", example_project_info),
        ("Custom Analysis", example_custom_analysis),
        ("Scientific Computing Analysis", example_scientific_computing_analysis),
        ("Translation Workflow", example_translation_workflow),
        ("CTSM Analysis", example_ctsm_analysis),
    ]
    
    for name, func in examples:
        print(f"\n{name}")
        print("-" * len(name))
        try:
            func()
        except Exception as e:
            print(f"Example failed: {e}")
        print()
    
    print("Examples complete!")
    print("\nNote: Some examples may fail if the specified paths don't exist.")
    print("Update the paths in the examples to match your actual projects.")