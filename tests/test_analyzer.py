"""
Tests for the main analyzer functionality.
"""

import pytest
import tempfile
from pathlib import Path
import json

from fortran_analyzer import FortranAnalyzer, create_analyzer_for_project, quick_analyze
from fortran_analyzer.config.project_config import FortranProjectConfig


# Sample project structure for testing
SAMPLE_PROJECT_FILES = {
    "src/main.f90": """
module main_module
  use utils_module
  implicit none
contains
  subroutine main_program()
    call utility_function()
  end subroutine
end module
""",
    "src/utils.f90": """
module utils_module
  implicit none
contains
  subroutine utility_function()
    print *, "Utility function called"
  end subroutine
end module
""",
    "src/physics.f90": """
module physics_module
  use iso_fortran_env, only: real64
  use utils_module
  implicit none
  
  type :: physics_state
    real(real64) :: temperature
    real(real64) :: pressure
  end type physics_state

contains

  subroutine compute_physics(state)
    type(physics_state), intent(inout) :: state
    
    ! Simple physics computation
    state%temperature = state%temperature + 1.0_real64
    state%pressure = state%pressure * 1.01_real64
    
    call utility_function()
  end subroutine compute_physics

  function get_temperature(state) result(temp)
    type(physics_state), intent(in) :: state
    real(real64) :: temp
    
    temp = state%temperature
  end function get_temperature

end module physics_module
""",
}


class TestFortranAnalyzer:
    """Test main FortranAnalyzer functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create project structure
        for file_path, content in SAMPLE_PROJECT_FILES.items():
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        # Create configuration
        self.config = FortranProjectConfig(
            project_name="Test Project",
            project_root=str(self.project_root),
            source_dirs=["src"],
            output_dir="test_output",
            generate_graphs=False,  # Disable for faster testing
            generate_metrics=True,
        )

        self.analyzer = FortranAnalyzer(self.config)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.config.project_name == "Test Project"
        assert self.analyzer.parser is not None
        assert self.analyzer.call_graph_builder is not None
        assert self.analyzer.decomposer is not None

    def test_basic_analysis(self):
        """Test basic analysis functionality."""
        results = self.analyzer.analyze(save_results=False)

        # Check basic structure
        assert "config" in results
        assert "parsing" in results
        assert "dependencies" in results
        assert "translation" in results

        # Check parsing results
        parsing = results["parsing"]
        assert "modules" in parsing
        assert "statistics" in parsing

        modules = parsing["modules"]
        assert len(modules) == 3  # main, utils, physics

        # Check module names
        module_names = list(modules.keys())
        assert "main_module" in module_names
        assert "utils_module" in module_names
        assert "physics_module" in module_names

        # Check statistics
        stats = parsing["statistics"]
        assert stats["total_files"] == 3
        assert stats["total_subroutines"] >= 2
        assert stats["total_functions"] >= 1

    def test_dependency_analysis(self):
        """Test dependency analysis."""
        results = self.analyzer.analyze(save_results=False)

        dependencies = results["dependencies"]
        assert "module_graph_summary" in dependencies
        assert "analysis" in dependencies

        # Check that dependencies were detected
        graph_summary = dependencies["module_graph_summary"]
        assert graph_summary["nodes"] >= 3
        assert graph_summary["edges"] >= 2  # main->utils, physics->utils

        # Check dependency analysis
        analysis = dependencies["analysis"]
        assert "external_dependencies" in analysis
        assert "hub_modules" in analysis

    def test_translation_units(self):
        """Test translation unit decomposition."""
        results = self.analyzer.analyze(save_results=False)

        translation = results["translation"]
        assert "units" in translation
        assert "statistics" in translation

        # Should have created translation units
        assert translation["units"] > 0

        # Check statistics
        t_stats = translation["statistics"]
        assert "total_units" in t_stats
        assert "units_by_type" in t_stats

    def test_get_summary_statistics(self):
        """Test summary statistics generation."""
        self.analyzer.analyze(save_results=False)

        summary = self.analyzer.get_summary_statistics()

        assert "files" in summary
        assert "lines" in summary
        assert "modules" in summary
        assert "translation_units" in summary

        assert summary["files"] == 3
        assert summary["modules"] == 3
        assert summary["lines"] > 0

    def test_get_translation_order(self):
        """Test translation order generation."""
        self.analyzer.analyze(save_results=False)

        order = self.analyzer.get_translation_order()

        assert isinstance(order, list)
        assert len(order) > 0

        # utils_module should come before modules that depend on it
        utils_index = order.index("utils_module")
        main_index = order.index("main_module")
        physics_index = order.index("physics_module")

        assert utils_index < main_index
        assert utils_index < physics_index

    def test_recommendations(self):
        """Test recommendation generation."""
        results = self.analyzer.analyze(save_results=False)

        recommendations = results["recommendations"]

        assert isinstance(recommendations, dict)
        assert "translation_strategy" in recommendations
        assert "dependency_issues" in recommendations
        assert "optimization_opportunities" in recommendations
        assert "risks" in recommendations


class TestAnalyzerFactory:
    """Test analyzer factory functions."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create minimal project
        src_dir = self.project_root / "src"
        src_dir.mkdir()
        (src_dir / "test.f90").write_text(
            """
module test_module
contains
  subroutine test_sub()
  end subroutine
end module
"""
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_create_analyzer_for_project(self):
        """Test creating analyzer for project."""
        analyzer = create_analyzer_for_project(
            str(self.project_root), template="generic", project_name="Factory Test"
        )

        assert analyzer.config.project_name == "Factory Test"
        assert analyzer.config.project_root == str(self.project_root)

    def test_quick_analyze(self):
        """Test quick analysis function."""
        results = quick_analyze(str(self.project_root), template="generic")

        assert "parsing" in results
        assert "dependencies" in results
        assert "translation" in results

        # Should find the test module
        modules = results["parsing"]["modules"]
        assert "test_module" in modules


class TestAnalyzerEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_project(self):
        """Test analysis of empty project."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create empty source directory
            src_dir = Path(tmp_dir) / "src"
            src_dir.mkdir()

            config = FortranProjectConfig(
                project_name="Empty Project",
                project_root=tmp_dir,
                source_dirs=["src"],
                generate_graphs=False,
            )

            analyzer = FortranAnalyzer(config)
            results = analyzer.analyze(save_results=False)

            # Should handle empty project gracefully
            assert results["parsing"]["modules"] == {}
            assert results["parsing"]["statistics"]["total_files"] == 0

    def test_invalid_configuration(self):
        """Test analysis with invalid configuration."""
        config = FortranProjectConfig(
            project_name="Invalid Project",
            project_root="/nonexistent/path",
            source_dirs=["src"],
        )

        with pytest.raises(ValueError):
            analyzer = FortranAnalyzer(config)

    def test_single_file_project(self):
        """Test analysis of single file project."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create single file
            src_dir = Path(tmp_dir) / "src"
            src_dir.mkdir()

            (src_dir / "single.f90").write_text(
                """
module single_module
  implicit none
contains
  subroutine single_sub()
    print *, "Single subroutine"
  end subroutine
end module
"""
            )

            analyzer = create_analyzer_for_project(
                tmp_dir, template="generic", generate_graphs=False
            )

            results = analyzer.analyze(save_results=False)

            assert len(results["parsing"]["modules"]) == 1
            assert "single_module" in results["parsing"]["modules"]


class TestAnalyzerIntegration:
    """Integration tests for the analyzer."""

    def test_full_workflow(self):
        """Test complete analysis workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # Create comprehensive test project
            for file_path, content in SAMPLE_PROJECT_FILES.items():
                full_path = project_root / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

            # Run complete analysis
            analyzer = create_analyzer_for_project(
                str(project_root),
                template="scientific_computing",
                output_dir="full_test_output",
                generate_graphs=False,  # Skip for faster testing
            )

            results = analyzer.analyze(save_results=True)

            # Verify all components worked
            assert "parsing" in results
            assert "dependencies" in results
            assert "translation" in results
            assert "recommendations" in results

            # Check that files were saved
            output_dir = project_root / "full_test_output"
            assert output_dir.exists()

            # Check for expected output files
            expected_files = [
                "analysis_results.json",
                "analysis_summary.txt",
                "translation_units.json",
            ]

            for filename in expected_files:
                file_path = output_dir / filename
                assert file_path.exists(), f"Expected file {filename} not found"
                assert file_path.stat().st_size > 0, f"File {filename} is empty"

    def test_analysis_results_serialization(self):
        """Test that analysis results can be properly serialized."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # Create simple test project
            src_dir = project_root / "src"
            src_dir.mkdir()
            (src_dir / "test.f90").write_text(SAMPLE_PROJECT_FILES["src/utils.f90"])

            analyzer = create_analyzer_for_project(
                str(project_root), template="generic", generate_graphs=False
            )

            results = analyzer.analyze(save_results=True)

            # Check that JSON file was created and is valid
            json_file = (
                project_root / analyzer.config.output_dir / "analysis_results.json"
            )
            assert json_file.exists()

            # Load and verify JSON
            with open(json_file, "r") as f:
                loaded_results = json.load(f)

            assert "config" in loaded_results
            assert "parsing" in loaded_results
            assert loaded_results["config"]["project_name"] == "Generic Fortran Project"


if __name__ == "__main__":
    pytest.main([__file__])
