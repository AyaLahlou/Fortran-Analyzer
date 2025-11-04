#!/usr/bin/env python3
"""
Simple runner for the Fortran Analyzer to avoid import issues.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Fix all relative imports by replacing them
def fix_imports():
    """Temporarily fix import paths"""
    import importlib.util
    
    # Manual module loading to bypass relative import issues
    
    # Load config module
    config_spec = importlib.util.spec_from_file_location(
        "project_config", 
        src_dir / "config" / "project_config.py"
    )
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    
    # Load parser module  
    parser_spec = importlib.util.spec_from_file_location(
        "fortran_parser",
        src_dir / "parser" / "fortran_parser.py"
    )
    parser_module = importlib.util.module_from_spec(parser_spec)
    
    # Inject the config module to avoid import error
    sys.modules['config.project_config'] = config_module
    parser_spec.loader.exec_module(parser_module)
    
    # Load analysis modules
    call_graph_spec = importlib.util.spec_from_file_location(
        "call_graph_builder",
        src_dir / "analysis" / "call_graph_builder.py"
    )
    call_graph_module = importlib.util.module_from_spec(call_graph_spec)
    call_graph_spec.loader.exec_module(call_graph_module)
    
    decomposer_spec = importlib.util.spec_from_file_location(
        "translation_decomposer", 
        src_dir / "analysis" / "translation_decomposer.py"
    )
    decomposer_module = importlib.util.module_from_spec(decomposer_spec)
    decomposer_spec.loader.exec_module(decomposer_module)
    
    # Load visualization module
    viz_spec = importlib.util.spec_from_file_location(
        "visualizer",
        src_dir / "visualization" / "visualizer.py"
    )
    viz_module = importlib.util.module_from_spec(viz_spec)
    viz_spec.loader.exec_module(viz_module)
    
    return config_module, parser_module, call_graph_module, decomposer_module, viz_module

def run_analysis(project_path, template="ctsm", output_dir=None):
    """Run analysis with manually loaded modules"""
    
    config_mod, parser_mod, call_graph_mod, decomposer_mod, viz_mod = fix_imports()
    
    # Create configuration
    manager = config_mod.ConfigurationManager()
    
    print(f"Available templates: {manager.list_templates()}")
    
    # Create project config
    if template in manager.list_templates():
        config = manager.create_from_template(template, project_path)
    else:
        config = config_mod.create_default_config(project_path, template)
    
    if output_dir:
        config.output_dir = output_dir
        
    print(f"Created configuration for: {config.project_name}")
    print(f"Source directories: {config.source_dirs}")
    print(f"Fortran extensions: {config.fortran_extensions}")
    
    # Initialize components
    parser = parser_mod.FortranParser(config)
    call_graph_builder = call_graph_mod.CallGraphBuilder()
    decomposer = decomposer_mod.TranslationUnitDecomposer(config)
    
    if config.generate_graphs:
        visualizer = viz_mod.FortranVisualizer(config)
    else:
        visualizer = None
    
    print("\nStarting analysis...")
    
    # Run parsing
    print("1. Parsing Fortran files...")
    parsing_results = parser.parse_project()
    
    print(f"   Found {len(parsing_results['modules'])} modules")
    print(f"   Total files: {parsing_results['statistics']['total_files']}")
    print(f"   Total lines: {parsing_results['statistics']['total_lines']}")
    
    # Build dependency graph
    print("2. Building dependency graphs...")
    modules = parsing_results['modules']
    dependency_results = call_graph_builder.build_dependency_graph(modules)
    
    print(f"   Module dependencies: {dependency_results['module_graph_summary']['edges']}")
    
    # Decompose for translation
    print("3. Planning translation units...")
    translation_results = decomposer.decompose_project(modules)
    
    print(f"   Translation units: {translation_results['units']}")
    
    # Generate visualizations
    if visualizer:
        print("4. Generating visualizations...")
        try:
            viz_results = visualizer.create_all_visualizations(
                modules, dependency_results, translation_results
            )
            print(f"   Generated {len(viz_results)} visualizations")
        except Exception as e:
            print(f"   Visualization failed: {e}")
            viz_results = {}
    else:
        viz_results = {}
    
    # Compile results
    results = {
        'parsing': parsing_results,
        'dependencies': dependency_results, 
        'translation': translation_results,
        'visualizations': viz_results,
        'recommendations': {
            'start_with': translation_results.get('translation_order', [])[:3],
            'high_priority': [],
            'external_dependencies': dependency_results['analysis'].get('external_dependencies', [])
        }
    }
    
    # Save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        import json
        with open(output_path / "analysis_results.json", 'w') as f:
            # Convert any non-serializable objects to strings
            def serialize_obj(obj):
                if hasattr(obj, '__dict__'):
                    return str(obj)
                return obj
                
            json.dump(results, f, indent=2, default=serialize_obj)
        
        print(f"\nResults saved to: {output_path}")
        print(f"Analysis complete!")
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fortran Analyzer")
    parser.add_argument("project_path", help="Path to the Fortran project")
    parser.add_argument("--template", default="ctsm", help="Configuration template")
    parser.add_argument("--output-dir", help="Output directory for results")
    
    args = parser.parse_args()
    
    try:
        results = run_analysis(args.project_path, args.template, args.output_dir)
        print("\n✅ Analysis completed successfully!")
        
        # Print summary
        print("\n📊 Analysis Summary:")
        parsing = results['parsing']
        print(f"  • Modules: {len(parsing['modules'])}")
        print(f"  • Files: {parsing['statistics']['total_files']}")
        print(f"  • Lines of code: {parsing['statistics']['total_lines']}")
        print(f"  • Subroutines: {parsing['statistics']['total_subroutines']}")
        print(f"  • Functions: {parsing['statistics']['total_functions']}")
        
        deps = results['dependencies']
        print(f"  • Module dependencies: {deps['module_graph_summary']['edges']}")
        
        trans = results['translation']
        print(f"  • Translation units: {trans['units']}")
        
        if results['recommendations']['start_with']:
            print(f"  • Recommended start: {results['recommendations']['start_with']}")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)