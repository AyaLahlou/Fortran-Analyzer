"""
Tests for the Fortran Analyzer configuration system.
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from fortran_analyzer.config.project_config import (
    FortranProjectConfig,
    ConfigurationManager,
    create_default_config,
)


class TestFortranProjectConfig:
    """Test FortranProjectConfig class."""

    def test_basic_config_creation(self):
        """Test basic configuration creation."""
        config = FortranProjectConfig(
            project_name="Test Project", project_root="/tmp/test"
        )

        assert config.project_name == "Test Project"
        assert config.project_root == str(Path("/tmp/test").resolve())
        assert config.fortran_extensions == [".f90", ".F90", ".f", ".F", ".f95", ".F95"]
        assert config.max_translation_unit_lines == 150

    def test_config_validation_valid(self):
        """Test validation with valid configuration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            src_dir = tmp_path / "src"
            src_dir.mkdir()

            config = FortranProjectConfig(
                project_name="Valid Project",
                project_root=str(tmp_path),
                source_dirs=["src"],
            )

            assert config.validate() == True

    def test_config_validation_invalid_root(self):
        """Test validation with invalid project root."""
        config = FortranProjectConfig(
            project_name="Invalid Project", project_root="/nonexistent/path"
        )

        assert config.validate() == False

    def test_config_yaml_roundtrip(self):
        """Test saving to and loading from YAML."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            config_file = tmp_path / "config.yaml"

            # Create config
            original_config = FortranProjectConfig(
                project_name="YAML Test",
                project_root=str(tmp_path),
                source_dirs=["src", "lib"],
                max_translation_unit_lines=100,
            )

            # Save to YAML
            original_config.to_yaml(config_file)

            # Load from YAML
            loaded_config = FortranProjectConfig.from_yaml(config_file)

            # Compare
            assert loaded_config.project_name == original_config.project_name
            assert (
                loaded_config.max_translation_unit_lines
                == original_config.max_translation_unit_lines
            )
            assert loaded_config.source_dirs == original_config.source_dirs


class TestConfigurationManager:
    """Test ConfigurationManager class."""

    def test_list_templates(self):
        """Test listing available templates."""
        manager = ConfigurationManager()
        templates = manager.list_templates()

        assert "generic" in templates
        assert "ctsm" in templates
        assert "scientific_computing" in templates
        assert len(templates) >= 3

    def test_create_from_template(self):
        """Test creating configuration from template."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = ConfigurationManager()

            config = manager.create_config_from_template(
                "generic", tmp_dir, overrides={"project_name": "Override Test"}
            )

            assert config.project_name == "Override Test"
            assert config.project_root == str(Path(tmp_dir).resolve())
            assert any(Path(d).name == "src" for d in config.source_dirs)

    def test_auto_detect_generic(self):
        """Test auto-detection for generic project."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create basic structure
            src_dir = Path(tmp_dir) / "src"
            src_dir.mkdir()

            manager = ConfigurationManager()
            detected = manager.auto_detect_project_type(tmp_dir)

            assert detected == "generic"

    def test_auto_detect_ctsm(self):
        """Test auto-detection for CTSM project."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create CTSM-like structure
            biogeophys_dir = Path(tmp_dir) / "src" / "biogeophys"
            biogeophys_dir.mkdir(parents=True)

            manager = ConfigurationManager()
            detected = manager.auto_detect_project_type(tmp_dir)

            assert detected == "ctsm"


class TestConfigUtilities:
    """Test configuration utility functions."""

    def test_create_default_config(self):
        """Test creating default configuration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = create_default_config(tmp_dir, "generic")

            assert config.project_name == "Generic Fortran Project"
            assert config.project_root == str(Path(tmp_dir).resolve())
            assert config.fortran_standard == "f2003"

    def test_create_default_config_auto(self):
        """Test creating default configuration with auto-detection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create src directory for generic detection
            src_dir = Path(tmp_dir) / "src"
            src_dir.mkdir()

            config = create_default_config(tmp_dir, "auto")

            assert config.project_name == "Generic Fortran Project"
            assert config.project_root == str(Path(tmp_dir).resolve())


class TestConfigurationEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_template(self):
        """Test handling of invalid template name."""
        manager = ConfigurationManager()

        with pytest.raises(ValueError):
            manager.create_config_from_template("nonexistent_template", "/tmp")

    def test_config_with_empty_source_dirs(self):
        """Test configuration with no source directories."""
        config = FortranProjectConfig(
            project_name="Empty Config", project_root="/tmp", source_dirs=[]
        )

        assert config.validate() == False

    def test_config_with_invalid_fortran_standard(self):
        """Test configuration with invalid Fortran standard."""
        config = FortranProjectConfig(
            project_name="Invalid Standard",
            project_root="/tmp",
            fortran_standard="invalid_standard",
        )

        assert config.validate() == False

    def test_config_with_invalid_line_limits(self):
        """Test configuration with invalid line limits."""
        config = FortranProjectConfig(
            project_name="Invalid Lines",
            project_root="/tmp",
            max_translation_unit_lines=10,
            min_chunk_lines=20,  # min > max
        )

        assert config.validate() == False


def test_yaml_config_example():
    """Test loading example YAML configuration."""
    yaml_content = """
project_name: "Test YAML Project"
project_root: "/tmp/test"
source_dirs:
  - "src"
  - "lib"
fortran_extensions: [".f90", ".F90"]
max_translation_unit_lines: 120
system_modules:
  - "iso_fortran_env"
external_libraries:
  - "netcdf"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_file = f.name

    try:
        config = FortranProjectConfig.from_yaml(yaml_file)

        assert config.project_name == "Test YAML Project"
        assert config.max_translation_unit_lines == 120
        assert any(Path(d).name == "src" for d in config.source_dirs)
        assert any(Path(d).name == "lib" for d in config.source_dirs)
        assert "iso_fortran_env" in config.system_modules
        assert "netcdf" in config.external_libraries

    finally:
        Path(yaml_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
