"""
Tests for the Fortran parser functionality.
"""

import pytest
import tempfile
from pathlib import Path

from fortran_analyzer.config.project_config import FortranProjectConfig
from fortran_analyzer.parser.fortran_parser import (
    FortranParser,
    FortranEntity,
    ModuleInfo,
)


# Sample Fortran code for testing
SAMPLE_MODULE_CODE = """
module test_module
  use iso_fortran_env, only: real64
  use another_module
  implicit none
  
  type :: test_type
    real(real64) :: value
    integer :: id
  end type test_type
  
  interface test_interface
    module procedure test_function
  end interface
  
contains

  subroutine test_subroutine(x, y)
    real(real64), intent(in) :: x
    real(real64), intent(out) :: y
    
    y = x * 2.0_real64
  end subroutine test_subroutine
  
  function test_function(a) result(b)
    real(real64), intent(in) :: a
    real(real64) :: b
    
    b = a + 1.0_real64
  end function test_function

end module test_module
"""

LARGE_SUBROUTINE_CODE = """
module large_module
  implicit none
contains

  subroutine large_subroutine(n, array)
    integer, intent(in) :: n
    real, intent(inout) :: array(n)
    integer :: i, j
    
    ! This is a large subroutine for testing decomposition
    do i = 1, n
      array(i) = 0.0
      do j = 1, 10
        array(i) = array(i) + real(i * j)
      end do
    end do
    
    ! More code to make it large
    do i = 1, n
      if (array(i) > 100.0) then
        array(i) = 100.0
      elseif (array(i) < 0.0) then
        array(i) = 0.0
      end if
    end do
    
    ! Even more code
    do i = 1, n-1
      if (array(i) > array(i+1)) then
        ! Swap elements
        real :: temp
        temp = array(i)
        array(i) = array(i+1)
        array(i+1) = temp
      end if
    end do
    
    ! Final processing
    do i = 1, n
      array(i) = sqrt(abs(array(i)))
    end do
    
  end subroutine large_subroutine

end module large_module
"""


class TestFortranParser:
    """Test FortranParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.src_dir = self.project_root / "src"
        self.src_dir.mkdir()

        # Create test configuration
        self.config = FortranProjectConfig(
            project_name="Test Project",
            project_root=str(self.project_root),
            source_dirs=["src"],
            fortran_extensions=[".f90", ".F90"],
        )

        self.parser = FortranParser(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test Fortran file."""
        file_path = self.src_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def test_find_fortran_files(self):
        """Test finding Fortran files."""
        # Create test files
        self.create_test_file("test1.f90", "! Test file 1")
        self.create_test_file("test2.F90", "! Test file 2")
        self.create_test_file("test3.txt", "! Not a Fortran file")

        # Find Fortran files
        fortran_files = self.parser.find_fortran_files()

        assert len(fortran_files) == 2
        filenames = [f.name for f in fortran_files]
        assert "test1.f90" in filenames
        assert "test2.F90" in filenames
        assert "test3.txt" not in filenames

    def test_parse_module_with_regex(self):
        """Test parsing a module with regex parser."""
        # Create test file
        test_file = self.create_test_file("test_module.f90", SAMPLE_MODULE_CODE)

        # Parse the file
        module_info = self.parser.parse_with_regex(test_file)

        assert module_info is not None
        assert module_info.name == "test_module"
        assert module_info.file_path == str(test_file)

        # Check uses
        assert len(module_info.uses) >= 2
        use_modules = [use["module"] for use in module_info.uses]
        assert "iso_fortran_env" in use_modules
        assert "another_module" in use_modules

        # Check subroutines and functions
        assert "test_subroutine" in module_info.subroutines
        assert "test_function" in module_info.functions

        # Check types
        assert "test_type" in module_info.types

        # Check entities
        assert len(module_info.entities) >= 3  # subroutine, function, type

    def test_parse_project(self):
        """Test parsing an entire project."""
        # Create multiple test files
        self.create_test_file("module1.f90", SAMPLE_MODULE_CODE)
        self.create_test_file(
            "module2.f90",
            """
module simple_module
  implicit none
contains
  subroutine simple_sub()
    print *, "Hello"
  end subroutine
end module
""",
        )

        # Parse the project
        results = self.parser.parse_project()

        assert "modules" in results
        assert "statistics" in results

        modules = results["modules"]
        assert len(modules) >= 2

        stats = results["statistics"]
        assert stats["total_files"] == 2
        assert stats["total_subroutines"] >= 2
        assert stats["total_functions"] >= 1

    def test_entity_line_detection(self):
        """Test detection of entity line numbers."""
        test_file = self.create_test_file("line_test.f90", SAMPLE_MODULE_CODE)

        # Parse and check line numbers
        module_info = self.parser.parse_with_regex(test_file)

        # Find subroutine entity
        subroutine_entity = None
        for entity in module_info.entities:
            if entity.name == "test_subroutine" and entity.entity_type == "subroutine":
                subroutine_entity = entity
                break

        assert subroutine_entity is not None
        assert subroutine_entity.line_start > 0
        assert subroutine_entity.line_end > subroutine_entity.line_start

    def test_exclude_patterns(self):
        """Test file exclusion patterns."""
        # Create files with different patterns
        self.create_test_file("module.f90", SAMPLE_MODULE_CODE)
        self.create_test_file("test_module.f90", "! Test file")
        self.create_test_file("example_module.f90", "! Example file")

        # Update config with exclude patterns
        self.config.exclude_patterns = ["**/test_*", "**/example_*"]
        parser = FortranParser(self.config)

        fortran_files = parser.find_fortran_files()
        filenames = [f.name for f in fortran_files]

        assert "module.f90" in filenames
        assert "test_module.f90" not in filenames
        assert "example_module.f90" not in filenames


class TestFortranEntity:
    """Test FortranEntity data model."""

    def test_entity_creation(self):
        """Test creating FortranEntity."""
        entity = FortranEntity(
            name="test_subroutine",
            entity_type="subroutine",
            file_path="/path/to/file.f90",
            line_start=10,
            line_end=20,
            parent="test_module",
        )

        assert entity.name == "test_subroutine"
        assert entity.entity_type == "subroutine"
        assert entity.parent == "test_module"
        assert entity.attributes == {}

    def test_entity_with_attributes(self):
        """Test FortranEntity with attributes."""
        entity = FortranEntity(
            name="test_function",
            entity_type="function",
            file_path="/path/to/file.f90",
            line_start=30,
            line_end=40,
            attributes={"return_type": "real", "arguments": ["x", "y"]},
        )

        assert entity.attributes["return_type"] == "real"
        assert "x" in entity.attributes["arguments"]


class TestModuleInfo:
    """Test ModuleInfo data model."""

    def test_module_info_creation(self):
        """Test creating ModuleInfo."""
        entities = [
            FortranEntity("sub1", "subroutine", "/path/file.f90", 10, 20),
            FortranEntity("func1", "function", "/path/file.f90", 30, 40),
        ]

        module_info = ModuleInfo(
            name="test_module",
            file_path="/path/to/file.f90",
            uses=[{"module": "iso_fortran_env", "only": None}],
            subroutines=["sub1"],
            functions=["func1"],
            types=[],
            variables=[],
            interfaces=[],
            line_count=100,
            entities=entities,
        )

        assert module_info.name == "test_module"
        assert len(module_info.entities) == 2
        assert module_info.subroutines == ["sub1"]
        assert module_info.functions == ["func1"]


class TestParserEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.src_dir = self.project_root / "src"
        self.src_dir.mkdir()

        self.config = FortranProjectConfig(
            project_name="Test Project",
            project_root=str(self.project_root),
            source_dirs=["src"],
        )

        self.parser = FortranParser(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_empty_file(self):
        """Test parsing empty file."""
        empty_file = self.src_dir / "empty.f90"
        empty_file.write_text("")

        module_info = self.parser.parse_file(empty_file)
        assert module_info is not None
        assert module_info.name == "empty"  # Default to filename

    def test_malformed_fortran(self):
        """Test parsing malformed Fortran."""
        malformed_file = self.src_dir / "malformed.f90"
        malformed_file.write_text("This is not valid Fortran code!")

        # Should not crash, even with malformed input
        module_info = self.parser.parse_file(malformed_file)
        assert module_info is not None

    def test_no_fortran_files(self):
        """Test project with no Fortran files."""
        # Create non-Fortran files
        (self.src_dir / "readme.txt").write_text("README")
        (self.src_dir / "makefile").write_text("MAKEFILE")

        results = self.parser.parse_project()

        assert results["modules"] == {}
        assert results["statistics"]["total_files"] == 0

    def test_nonexistent_source_dir(self):
        """Test with non-existent source directory."""
        self.config.source_dirs = ["nonexistent"]
        parser = FortranParser(self.config)

        files = parser.find_fortran_files()
        assert len(files) == 0


def test_parser_statistics():
    """Test calculation of parsing statistics."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_root = Path(tmp_dir)
        src_dir = project_root / "src"
        src_dir.mkdir()

        # Create test files
        (src_dir / "mod1.f90").write_text(SAMPLE_MODULE_CODE)
        (src_dir / "mod2.f90").write_text(
            """
module mod2
contains
  subroutine sub2()
  end subroutine
  function func2() result(x)
    integer :: x
    x = 42
  end function
end module
"""
        )

        config = FortranProjectConfig(
            project_name="Stats Test",
            project_root=str(project_root),
            source_dirs=["src"],
        )

        parser = FortranParser(config)
        results = parser.parse_project()

        stats = results["statistics"]

        # Check that statistics are reasonable
        assert stats["total_files"] == 2
        assert stats["total_subroutines"] >= 2
        assert stats["total_functions"] >= 2
        assert stats["total_lines"] > 0
        assert stats["average_lines_per_file"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
