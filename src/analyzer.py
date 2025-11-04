"""
Main Fortran Analyzer framework.
Orchestrates the parsing, analysis, and visualization of Fortran codebases.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
import time

from config.project_config import FortranProjectConfig, ConfigurationManager
from parser.fortran_parser import FortranParser
from analysis.call_graph_builder import CallGraphBuilder
from analysis.translation_decomposer import TranslationUnitDecomposer
from visualization.visualizer import FortranVisualizer

logger = logging.getLogger(__name__)


class FortranAnalyzer:
    """Main analyzer class that orchestrates Fortran codebase analysis."""

    def __init__(self, config: FortranProjectConfig):
        self.config = config
        self.results: Dict[str, Any] = {}

        # Initialize components
        self.parser = FortranParser(config)
        self.call_graph_builder = CallGraphBuilder(config)
        self.decomposer = TranslationUnitDecomposer(config)
        self.visualizer = FortranVisualizer(config) if config.generate_graphs else None

        # Setup output directory
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized FortranAnalyzer for project: {config.project_name}")

    def analyze(self, save_results: bool = True) -> Dict[str, Any]:
        """Perform complete analysis of the Fortran codebase."""
        logger.info("Starting Fortran codebase analysis")
        start_time = time.time()

        try:
            # Validate configuration
            if not self.config.validate():
                raise ValueError("Invalid configuration")

            # Step 1: Parse the codebase
            logger.info("Step 1: Parsing Fortran source files")
            parsing_results = self.parser.parse_project()
            modules = parsing_results.get("modules", {})

            if not modules:
                logger.warning("No modules found in the codebase")
                return {}

            # Step 2: Build call graphs and dependency analysis
            logger.info("Step 2: Building call graphs and analyzing dependencies")
            module_graph = self.call_graph_builder.build_module_dependency_graph(
                modules
            )
            entity_graph = self.call_graph_builder.build_entity_call_graph(modules)

            dependency_analysis = self.call_graph_builder.analyze_dependencies()
            graph_metrics = self.call_graph_builder.calculate_metrics()

            # Step 3: Decompose into translation units
            logger.info("Step 3: Decomposing into translation units")
            translation_units = self.decomposer.decompose_modules(modules)
            translation_stats = self.decomposer.get_statistics()

            # Step 4: Generate visualizations
            visualization_files = {}
            if self.visualizer and self.config.generate_graphs:
                logger.info("Step 4: Generating visualizations")
                analysis_results = {
                    "call_graph_builder": self.call_graph_builder,
                    "translation_units": translation_units,
                    "statistics": parsing_results.get("statistics", {}),
                    "dependency_analysis": dependency_analysis,
                }
                visualization_files = self.visualizer.generate_all_visualizations(
                    analysis_results
                )

            # Compile results
            self.results = {
                "config": {
                    "project_name": self.config.project_name,
                    "project_root": self.config.project_root,
                    "analysis_timestamp": time.time(),
                    "analysis_duration": time.time() - start_time,
                },
                "parsing": parsing_results,
                "dependencies": {
                    "module_graph_summary": {
                        "nodes": module_graph.number_of_nodes() if module_graph else 0,
                        "edges": module_graph.number_of_edges() if module_graph else 0,
                    },
                    "entity_graph_summary": {
                        "nodes": entity_graph.number_of_nodes() if entity_graph else 0,
                        "edges": entity_graph.number_of_edges() if entity_graph else 0,
                    },
                    "analysis": dependency_analysis,
                    "metrics": graph_metrics,
                },
                "translation": {
                    "units": len(translation_units),
                    "statistics": translation_stats,
                    "translation_order": self.call_graph_builder.get_translation_order(),
                },
                "visualizations": visualization_files,
                "recommendations": self._generate_recommendations(
                    dependency_analysis, translation_stats, modules
                ),
            }

            # Save results
            if save_results:
                self._save_analysis_results()
                self._export_graphs()
                self._export_translation_units(translation_units)

            elapsed_time = time.time() - start_time
            logger.info(f"Analysis completed in {elapsed_time:.2f} seconds")

            return self.results

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def _generate_recommendations(
        self, dependency_analysis: Dict, translation_stats: Dict, modules: Dict
    ) -> Dict[str, Any]:
        """Generate recommendations based on analysis results."""
        recommendations: Dict[str, List[str]] = {
            "translation_strategy": [],
            "dependency_issues": [],
            "optimization_opportunities": [],
            "risks": [],
        }

        # Translation strategy recommendations
        if translation_stats.get("total_units", 0) > 50:
            recommendations["translation_strategy"].append(
                "Large project detected. Consider incremental translation approach."
            )

        high_effort_units = translation_stats.get("units_by_effort", {}).get("high", 0)
        total_units = translation_stats.get("total_units", 1)

        if high_effort_units / total_units > 0.3:
            recommendations["translation_strategy"].append(
                "High percentage of complex units. Plan for extended timeline."
            )

        # Dependency issue recommendations
        circular_deps = dependency_analysis.get("circular_dependencies", [])
        if circular_deps:
            recommendations["dependency_issues"].append(
                f"Found {len(circular_deps)} circular dependencies. These must be resolved before translation."
            )

        external_deps = dependency_analysis.get("external_dependencies", [])
        if external_deps:
            recommendations["dependency_issues"].append(
                f"Project depends on {len(external_deps)} external libraries. Verify availability in target language."
            )

        # Optimization opportunities
        orphaned_modules = dependency_analysis.get("orphaned_modules", [])
        if orphaned_modules:
            recommendations["optimization_opportunities"].append(
                f"Found {len(orphaned_modules)} orphaned modules. Consider removing unused code."
            )

        hub_modules = dependency_analysis.get("hub_modules", [])
        if hub_modules:
            recommendations["optimization_opportunities"].append(
                f"Modules {hub_modules[:3]} are heavily used. Prioritize their translation."
            )

        # Risk assessment
        avg_lines = translation_stats.get("average_lines_per_unit", 0)
        if avg_lines > self.config.max_translation_unit_lines * 0.8:
            recommendations["risks"].append(
                "High average lines per unit. Consider reducing translation unit size."
            )

        if not dependency_analysis.get("is_dag", True):
            recommendations["risks"].append(
                "Module dependency graph contains cycles. This complicates translation."
            )

        return recommendations

    def _save_analysis_results(self) -> None:
        """Save analysis results to files."""
        # Save main results as JSON
        results_file = self.output_dir / "analysis_results.json"

        # Create a serializable copy
        serializable_results = self._make_serializable(self.results)

        with open(results_file, "w") as f:
            json.dump(serializable_results, f, indent=2)

        logger.info(f"Analysis results saved to {results_file}")

        # Save summary report
        self._save_summary_report()

    def _save_summary_report(self) -> None:
        """Save a human-readable summary report."""
        report_file = self.output_dir / "analysis_summary.txt"

        with open(report_file, "w") as f:
            f.write(f"Fortran Codebase Analysis Report\n")
            f.write(f"{'=' * 40}\n\n")

            f.write(f"Project: {self.config.project_name}\n")
            f.write(
                f"Analysis Date: {time.ctime(self.results['config']['analysis_timestamp'])}\n"
            )
            f.write(
                f"Duration: {self.results['config']['analysis_duration']:.2f} seconds\n\n"
            )

            # Parsing summary
            parsing = self.results.get("parsing", {})
            stats = parsing.get("statistics", {})

            f.write("Parsing Summary:\n")
            f.write(f"  Total Files: {stats.get('total_files', 0)}\n")
            f.write(f"  Total Lines: {stats.get('total_lines', 0):,}\n")
            f.write(f"  Modules: {len(parsing.get('modules', {}))}\n")
            f.write(f"  Subroutines: {stats.get('total_subroutines', 0)}\n")
            f.write(f"  Functions: {stats.get('total_functions', 0)}\n")
            f.write(f"  Types: {stats.get('total_types', 0)}\n\n")

            # Translation summary
            translation = self.results.get("translation", {})

            f.write("Translation Analysis:\n")
            f.write(f"  Translation Units: {translation.get('units', 0)}\n")

            t_stats = translation.get("statistics", {})
            units_by_effort = t_stats.get("units_by_effort", {})
            f.write(f"  Low Effort Units: {units_by_effort.get('low', 0)}\n")
            f.write(f"  Medium Effort Units: {units_by_effort.get('medium', 0)}\n")
            f.write(f"  High Effort Units: {units_by_effort.get('high', 0)}\n\n")

            # Dependency summary
            dependencies = self.results.get("dependencies", {})
            analysis = dependencies.get("analysis", {})

            f.write("Dependency Analysis:\n")
            f.write(
                f"  Module Dependencies: {dependencies.get('module_graph_summary', {}).get('edges', 0)}\n"
            )
            f.write(
                f"  Circular Dependencies: {len(analysis.get('circular_dependencies', []))}\n"
            )
            f.write(
                f"  External Dependencies: {len(analysis.get('external_dependencies', []))}\n"
            )
            f.write(f"  Hub Modules: {len(analysis.get('hub_modules', []))}\n\n")

            # Recommendations
            recommendations = self.results.get("recommendations", {})

            if recommendations:
                f.write("Recommendations:\n")

                for category, items in recommendations.items():
                    if items:
                        f.write(f"  {category.replace('_', ' ').title()}:\n")
                        for item in items:
                            f.write(f"    - {item}\n")
                        f.write("\n")

        logger.info(f"Summary report saved to {report_file}")

    def _export_graphs(self) -> None:
        """Export graph data in various formats."""
        if not hasattr(self, "call_graph_builder"):
            return

        graphs_dir = self.output_dir / "graphs"
        graphs_dir.mkdir(exist_ok=True)

        try:
            exported_files = self.call_graph_builder.export_graphs(
                graphs_dir, formats=["graphml", "json"]
            )
            logger.info(f"Exported {len(exported_files)} graph files")
        except Exception as e:
            logger.error(f"Failed to export graphs: {e}")

    def _export_translation_units(self, translation_units: List) -> None:
        """Export translation units data."""
        if not translation_units:
            return

        units_file = self.output_dir / "translation_units.json"

        try:
            self.decomposer.export_units(units_file, format="json")
            logger.info(f"Translation units exported to {units_file}")
        except Exception as e:
            logger.error(f"Failed to export translation units: {e}")

    def _make_serializable(self, obj) -> Union[Dict, List, str, int, float, bool, None]:
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, "__dict__"):
            return self._make_serializable(obj.__dict__)
        else:
            try:
                json.dumps(obj)  # Test if serializable
                return obj
            except (TypeError, ValueError):
                return str(obj)

    def get_results(self) -> Dict[str, Any]:
        """Get analysis results."""
        return self.results

    def get_translation_order(self) -> List[str]:
        """Get recommended translation order."""
        return self.call_graph_builder.get_translation_order()

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.results:
            return {}

        return {
            "files": self.results.get("parsing", {})
            .get("statistics", {})
            .get("total_files", 0),
            "lines": self.results.get("parsing", {})
            .get("statistics", {})
            .get("total_lines", 0),
            "modules": len(self.results.get("parsing", {}).get("modules", {})),
            "translation_units": self.results.get("translation", {}).get("units", 0),
            "dependencies": self.results.get("dependencies", {})
            .get("module_graph_summary", {})
            .get("edges", 0),
            "circular_dependencies": len(
                self.results.get("dependencies", {})
                .get("analysis", {})
                .get("circular_dependencies", [])
            ),
            "external_dependencies": len(
                self.results.get("dependencies", {})
                .get("analysis", {})
                .get("external_dependencies", [])
            ),
        }


def create_analyzer_from_config_file(config_path: Union[str, Path]) -> FortranAnalyzer:
    """Create analyzer from configuration file."""
    from .config.project_config import load_config

    config = load_config(config_path)
    return FortranAnalyzer(config)


def create_analyzer_for_project(
    project_root: str, template: str = "auto", **config_overrides
) -> FortranAnalyzer:
    """Create analyzer for a project using template."""
    from .config.project_config import create_default_config

    config = create_default_config(project_root, template)

    # Apply any overrides
    for key, value in config_overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return FortranAnalyzer(config)


def quick_analyze(
    project_root: str, template: str = "auto", output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Perform a quick analysis of a Fortran project."""
    config_overrides = {}
    if output_dir:
        config_overrides["output_dir"] = output_dir

    analyzer = create_analyzer_for_project(project_root, template, **config_overrides)
    return analyzer.analyze()
