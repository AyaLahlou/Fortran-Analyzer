#!/usr/bin/env python3
"""
Simplified Fortran analyzer for CLM-ml_v1 project.
This is a standalone script that analyzes Fortran code structure.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import json

class SimpleFortranAnalyzer:
    """Simplified Fortran analyzer that works without complex imports."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.fortran_extensions = ['.f90', '.F90', '.f', '.F', '.f95', '.F95']
        
        # Common CLM/CTSM patterns
        self.source_dirs = [
            'clm_src_biogeophys',
            'clm_src_cpl', 
            'clm_src_main',
            'clm_src_utils',
            'cime_src_share_util',
            'multilayer_canopy',
            'offline_driver'
        ]
        
        self.modules = {}
        self.dependencies = defaultdict(set)
        self.files_analyzed = []
        
    def find_fortran_files(self) -> List[Path]:
        """Find all Fortran files in the project."""
        fortran_files = []
        
        for source_dir in self.source_dirs:
            dir_path = self.project_path / source_dir
            if dir_path.exists():
                for ext in self.fortran_extensions:
                    fortran_files.extend(dir_path.rglob(f"*{ext}"))
        
        return fortran_files
    
    def parse_fortran_file(self, file_path: Path) -> Dict:
        """Parse a single Fortran file for modules, subroutines, functions, and dependencies."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return {}
        
        # Remove comments and preprocessor directives
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            # Remove comments (starting with !)
            if '!' in line:
                line = line.split('!')[0]
            # Skip preprocessor directives
            if line.strip().startswith('#'):
                continue
            clean_lines.append(line)
        
        clean_content = '\n'.join(clean_lines)
        
        file_info = {
            'path': str(file_path),
            'modules': [],
            'subroutines': [],
            'functions': [],
            'uses': [],
            'types': [],
            'lines': len(lines)
        }
        
        # Find modules
        module_pattern = r'^\s*module\s+(\w+)'
        for match in re.finditer(module_pattern, clean_content, re.MULTILINE | re.IGNORECASE):
            module_name = match.group(1)
            if module_name.lower() not in ['procedure', 'subroutine', 'function']:
                file_info['modules'].append(module_name)
        
        # Find use statements
        use_pattern = r'^\s*use\s+(\w+)'
        for match in re.finditer(use_pattern, clean_content, re.MULTILINE | re.IGNORECASE):
            used_module = match.group(1)
            file_info['uses'].append(used_module)
        
        # Find subroutines
        subroutine_pattern = r'^\s*subroutine\s+(\w+)'
        for match in re.finditer(subroutine_pattern, clean_content, re.MULTILINE | re.IGNORECASE):
            file_info['subroutines'].append(match.group(1))
        
        # Find functions
        function_pattern = r'^\s*(?:.*\s+)?function\s+(\w+)'
        for match in re.finditer(function_pattern, clean_content, re.MULTILINE | re.IGNORECASE):
            file_info['functions'].append(match.group(1))
        
        # Find derived types
        type_pattern = r'^\s*type\s*::\s*(\w+)|^\s*type\s+(\w+)'
        for match in re.finditer(type_pattern, clean_content, re.MULTILINE | re.IGNORECASE):
            type_name = match.group(1) or match.group(2)
            if type_name and type_name.lower() not in ['public', 'private', 'parameter']:
                file_info['types'].append(type_name)
        
        return file_info
    
    def analyze_project(self) -> Dict:
        """Analyze the entire project."""
        print(f"Analyzing Fortran project: {self.project_path}")
        
        # Find all Fortran files
        fortran_files = self.find_fortran_files()
        print(f"Found {len(fortran_files)} Fortran files")
        
        total_lines = 0
        total_modules = 0
        total_subroutines = 0
        total_functions = 0
        total_types = 0
        
        module_to_file = {}
        all_uses = set()
        
        # Analyze each file
        for file_path in fortran_files:
            print(f"  Analyzing: {file_path.relative_to(self.project_path)}")
            file_info = self.parse_fortran_file(file_path)
            
            if file_info:
                self.files_analyzed.append(file_info)
                total_lines += file_info['lines']
                total_modules += len(file_info['modules'])
                total_subroutines += len(file_info['subroutines'])
                total_functions += len(file_info['functions'])
                total_types += len(file_info['types'])
                
                # Map modules to files
                for module in file_info['modules']:
                    module_to_file[module] = str(file_path)
                    self.modules[module] = file_info
                
                # Track dependencies
                for module in file_info['modules']:
                    for used_module in file_info['uses']:
                        self.dependencies[module].add(used_module)
                        all_uses.add(used_module)
        
        # Find external dependencies (used but not defined)
        defined_modules = set(self.modules.keys())
        external_deps = all_uses - defined_modules
        
        # Count module usage
        module_usage = Counter()
        for file_info in self.files_analyzed:
            for used_module in file_info['uses']:
                module_usage[used_module] += 1
        
        # Find circular dependencies
        circular_deps = self.find_circular_dependencies()
        
        results = {
            'project_path': str(self.project_path),
            'analysis_summary': {
                'total_files': len(fortran_files),
                'files_analyzed': len(self.files_analyzed),
                'total_lines': total_lines,
                'total_modules': total_modules,
                'total_subroutines': total_subroutines,
                'total_functions': total_functions,
                'total_types': total_types,
                'external_dependencies': len(external_deps)
            },
            'modules': {name: {
                'file': module_to_file.get(name, 'unknown'),
                'uses': list(self.dependencies.get(name, [])),
                'subroutines': info.get('subroutines', []),
                'functions': info.get('functions', []),
                'types': info.get('types', [])
            } for name, info in self.modules.items()},
            'dependencies': {
                'internal': {k: list(v & defined_modules) for k, v in self.dependencies.items()},
                'external': sorted(external_deps),
                'circular': circular_deps
            },
            'statistics': {
                'most_used_modules': dict(module_usage.most_common(10)),
                'modules_by_directory': self.get_modules_by_directory(),
                'complexity_metrics': self.calculate_complexity_metrics()
            },
            'translation_recommendations': self.get_translation_recommendations()
        }
        
        return results
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor in self.modules:  # Only consider internal modules
                    dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for module in self.modules:
            if module not in visited:
                dfs(module, [])
        
        return cycles
    
    def get_modules_by_directory(self) -> Dict[str, List[str]]:
        """Group modules by source directory."""
        modules_by_dir = defaultdict(list)
        
        for module_name, module_info in self.modules.items():
            file_path = Path(module_info['path'])
            # Find the source directory
            for part in file_path.parts:
                if part in self.source_dirs:
                    modules_by_dir[part].append(module_name)
                    break
        
        return dict(modules_by_dir)
    
    def calculate_complexity_metrics(self) -> Dict:
        """Calculate complexity metrics for the project."""
        total_procedures = 0
        module_sizes = []
        
        for module_info in self.modules.values():
            procedures = len(module_info.get('subroutines', [])) + len(module_info.get('functions', []))
            total_procedures += procedures
            module_sizes.append(procedures)
        
        return {
            'average_procedures_per_module': total_procedures / len(self.modules) if self.modules else 0,
            'max_procedures_in_module': max(module_sizes) if module_sizes else 0,
            'modules_with_many_procedures': len([s for s in module_sizes if s > 10])
        }
    
    def get_translation_recommendations(self) -> Dict:
        """Generate recommendations for JAX translation."""
        # Find leaf modules (no dependencies)
        leaf_modules = []
        for module in self.modules:
            internal_deps = [dep for dep in self.dependencies.get(module, []) if dep in self.modules]
            if not internal_deps:
                leaf_modules.append(module)
        
        # Find utility modules (used by many others)
        module_usage = Counter()
        for deps in self.dependencies.values():
            for dep in deps:
                if dep in self.modules:
                    module_usage[dep] += 1
        
        utility_modules = [mod for mod, count in module_usage.most_common(5)]
        
        # Find large modules that might need decomposition
        large_modules = []
        for module_name, module_info in self.modules.items():
            procedures = len(module_info.get('subroutines', [])) + len(module_info.get('functions', []))
            if procedures > 15:  # Arbitrary threshold
                large_modules.append((module_name, procedures))
        
        return {
            'start_with_leaf_modules': leaf_modules[:5],
            'high_priority_utilities': utility_modules,
            'consider_decomposing': [mod for mod, count in large_modules],
            'translation_order_suggestion': leaf_modules + utility_modules
        }

def main():
    """Main function to run the analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Fortran Project Analyzer")
    parser.add_argument("project_path", help="Path to the Fortran project")
    parser.add_argument("--output-dir", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Create analyzer and run analysis
    analyzer = SimpleFortranAnalyzer(args.project_path)
    results = analyzer.analyze_project()
    
    # Print summary
    print("\n" + "="*60)
    print("FORTRAN ANALYSIS RESULTS")
    print("="*60)
    
    summary = results['analysis_summary']
    print(f"Project: {results['project_path']}")
    print(f"Files analyzed: {summary['files_analyzed']}/{summary['total_files']}")
    print(f"Total lines of code: {summary['total_lines']:,}")
    print(f"Modules: {summary['total_modules']}")
    print(f"Subroutines: {summary['total_subroutines']}")
    print(f"Functions: {summary['total_functions']}")
    print(f"Derived types: {summary['total_types']}")
    print(f"External dependencies: {summary['external_dependencies']}")
    
    # Show module breakdown by directory
    print(f"\nModules by directory:")
    modules_by_dir = results['statistics']['modules_by_directory']
    for directory, modules in modules_by_dir.items():
        print(f"  {directory}: {len(modules)} modules")
    
    # Show most used modules
    print(f"\nMost used modules:")
    most_used = results['statistics']['most_used_modules']
    for module, count in list(most_used.items())[:5]:
        print(f"  {module}: used {count} times")
    
    # Show circular dependencies
    circular = results['dependencies']['circular']
    if circular:
        print(f"\n⚠️  Found {len(circular)} circular dependencies:")
        for cycle in circular[:3]:  # Show first 3
            print(f"  {' -> '.join(cycle)}")
    else:
        print(f"\n✅ No circular dependencies found")
    
    # Show recommendations
    recommendations = results['translation_recommendations']
    print(f"\nTranslation recommendations:")
    print(f"  Start with leaf modules: {recommendations['start_with_leaf_modules'][:3]}")
    print(f"  High-priority utilities: {recommendations['high_priority_utilities'][:3]}")
    if recommendations['consider_decomposing']:
        print(f"  Consider decomposing: {recommendations['consider_decomposing'][:3]}")
    
    # Save results
    if args.output_dir:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / "fortran_analysis.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create a summary report
        with open(output_path / "analysis_summary.txt", 'w') as f:
            f.write("FORTRAN ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Project: {results['project_path']}\n")
            f.write(f"Analysis Date: {__import__('datetime').datetime.now()}\n\n")
            
            f.write("STATISTICS:\n")
            for key, value in summary.items():
                f.write(f"  {key.replace('_', ' ').title()}: {value:,}\n")
            
            f.write(f"\nMODULES BY DIRECTORY:\n")
            for directory, modules in modules_by_dir.items():
                f.write(f"  {directory}: {len(modules)} modules\n")
                for module in modules[:5]:  # List first 5
                    f.write(f"    - {module}\n")
                if len(modules) > 5:
                    f.write(f"    ... and {len(modules)-5} more\n")
            
            f.write(f"\nRECOMMENDATIONS:\n")
            f.write(f"  Start with: {', '.join(recommendations['start_with_leaf_modules'][:5])}\n")
            f.write(f"  Utilities: {', '.join(recommendations['high_priority_utilities'][:5])}\n")
        
        print(f"\n📁 Results saved to: {output_path}")
        print(f"   - fortran_analysis.json (detailed results)")
        print(f"   - analysis_summary.txt (human-readable summary)")
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()