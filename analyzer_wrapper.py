#!/usr/bin/env python3
"""
Working wrapper for the Fortran Analyzer to generate proper JSON files for jax-agents.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from fortran_analyzer import FortranAnalyzer, create_analyzer_for_project, quick_analyze
    print("✅ Successfully imported fortran_analyzer")
    
    def run_full_analysis(project_path, template="ctsm", output_dir=None):
        """Run full analysis using the main API."""
        
        print(f"Analyzing project: {project_path}")
        print(f"Template: {template}")
        print(f"Output directory: {output_dir}")
        
        # Use the main API
        analyzer = create_analyzer_for_project(
            project_path, 
            template=template,
            output_dir=output_dir if output_dir else "analysis_output"
        )
        
        print(f"Created analyzer for: {analyzer.config.project_name}")
        print(f"Source directories: {analyzer.config.source_dirs}")
        
        # Run the analysis
        results = analyzer.analyze(save_results=True)
        
        print("✅ Analysis completed!")
        return results
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Using fallback simple analyzer...")
    
    # Fallback to simple analyzer but try to generate compatible JSON
    sys.path.insert(0, str(Path(__file__).parent))
    from simple_analyzer import SimpleFortranAnalyzer
    
    def run_full_analysis(project_path, template="ctsm", output_dir=None):
        """Run analysis using simple analyzer with JSON conversion."""
        
        analyzer = SimpleFortranAnalyzer(project_path)
        results = analyzer.analyze_project()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save in the format expected by jax-agents
            with open(output_path / "fortran_analysis.json", "w") as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"📁 Results saved to: {output_path}")
        
        return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fortran Analyzer Wrapper")
    parser.add_argument("project_path", help="Path to the Fortran project")
    parser.add_argument("--template", default="ctsm", help="Configuration template")
    parser.add_argument("--output-dir", help="Output directory for results")

    args = parser.parse_args()

    try:
        results = run_full_analysis(args.project_path, args.template, args.output_dir)
        print("\n✅ Analysis completed successfully!")
        
        # Print summary
        if 'analysis_summary' in results:
            summary = results['analysis_summary']
            print(f"Files analyzed: {summary.get('files_analyzed', 0)}")
            print(f"Total modules: {summary.get('total_modules', 0)}")
        elif 'parsing' in results:
            parsing = results['parsing']
            stats = parsing.get('statistics', {})
            print(f"Files analyzed: {stats.get('total_files', 0)}")
            print(f"Total modules: {len(parsing.get('modules', {}))}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)