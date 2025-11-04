#!/usr/bin/env python3
"""
Demonstration script for the refactored Fortran Analyzer.
Shows how the framework can be used with different types of Fortran codebases.
"""

import sys
import tempfile
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fortran_analyzer import (
    FortranAnalyzer,
    create_analyzer_for_project,
    quick_analyze,
    ConfigurationManager,
    create_default_config,
)


def create_sample_ctsm_structure(base_path: Path):
    """Create a sample CTSM-like project structure."""
    print("Creating sample CTSM project structure...")

    # Create directory structure
    biogeophys_dir = base_path / "src" / "biogeophys"
    biogeochem_dir = base_path / "src" / "biogeochem"
    main_dir = base_path / "src" / "main"

    for dir_path in [biogeophys_dir, biogeochem_dir, main_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create sample biogeophysics module
    biogeophys_content = """
module CanopyStateType
  use shr_kind_mod, only : r8 => shr_kind_r8
  use decompMod, only : bounds_type
  use clm_varpar, only : nlevsoi
  implicit none
  
  type, public :: canopystate_type
    real(r8), pointer :: lai_col(:)
    real(r8), pointer :: htop_col(:)
    real(r8), pointer :: hbot_col(:)
  end type canopystate_type

contains

  subroutine canopystate_init(this, bounds)
    class(canopystate_type), intent(inout) :: this
    type(bounds_type), intent(in) :: bounds
    
    allocate(this%lai_col(bounds%begc:bounds%endc))
    allocate(this%htop_col(bounds%begc:bounds%endc))
    allocate(this%hbot_col(bounds%begc:bounds%endc))
    
    this%lai_col(:) = 0.0_r8
    this%htop_col(:) = 0.0_r8
    this%hbot_col(:) = 0.0_r8
  end subroutine canopystate_init

  subroutine canopystate_update(this, bounds)
    class(canopystate_type), intent(inout) :: this
    type(bounds_type), intent(in) :: bounds
    integer :: c
    
    do c = bounds%begc, bounds%endc
      if (this%lai_col(c) > 0.0_r8) then
        this%htop_col(c) = 2.0_r8 * this%lai_col(c)
        this%hbot_col(c) = 0.1_r8 * this%htop_col(c)
      end if
    end do
  end subroutine canopystate_update

end module CanopyStateType
"""

    # Create sample biogeochemistry module
    biogeochem_content = """
module CNPhenologyMod
  use shr_kind_mod, only : r8 => shr_kind_r8
  use clm_varctl, only : iulog
  use CanopyStateType, only : canopystate_type
  implicit none

contains

  subroutine CNPhenology(bounds, num_soilp, filter_soilp, canopystate_inst)
    use decompMod, only : bounds_type
    type(bounds_type), intent(in) :: bounds
    integer, intent(in) :: num_soilp
    integer, intent(in) :: filter_soilp(:)
    type(canopystate_type), intent(inout) :: canopystate_inst
    
    integer :: p, fp
    real(r8) :: phenology_factor
    
    ! Update phenology for each patch
    do fp = 1, num_soilp
      p = filter_soilp(fp)
      
      ! Simple phenology calculation
      phenology_factor = 1.0_r8
      
      ! Update canopy state based on phenology
      call update_canopy_phenology(p, phenology_factor, canopystate_inst)
    end do
  end subroutine CNPhenology

  subroutine update_canopy_phenology(p, factor, canopystate_inst)
    integer, intent(in) :: p
    real(r8), intent(in) :: factor
    type(canopystate_type), intent(inout) :: canopystate_inst
    
    ! Update LAI based on phenology factor
    canopystate_inst%lai_col(p) = canopystate_inst%lai_col(p) * factor
  end subroutine update_canopy_phenology

end module CNPhenologyMod
"""

    # Create main module
    main_content = """
module clm_driver
  use CanopyStateType, only : canopystate_type
  use CNPhenologyMod, only : CNPhenology
  use decompMod, only : bounds_type
  implicit none

contains

  subroutine clm_drv(bounds, canopystate_inst)
    type(bounds_type), intent(in) :: bounds
    type(canopystate_type), intent(inout) :: canopystate_inst
    
    integer :: num_soilp
    integer, allocatable :: filter_soilp(:)
    
    ! Set up soil patch filter
    num_soilp = bounds%endc - bounds%begc + 1
    allocate(filter_soilp(num_soilp))
    
    ! Run phenology
    call CNPhenology(bounds, num_soilp, filter_soilp, canopystate_inst)
    
    deallocate(filter_soilp)
  end subroutine clm_drv

end module clm_driver
"""

    # Write files
    (biogeophys_dir / "CanopyStateType.F90").write_text(biogeophys_content)
    (biogeochem_dir / "CNPhenologyMod.F90").write_text(biogeochem_content)
    (main_dir / "clm_driver.F90").write_text(main_content)

    print(f"Created sample CTSM project at: {base_path}")


def create_sample_scientific_project(base_path: Path):
    """Create a sample scientific computing project."""
    print("Creating sample scientific computing project...")

    src_dir = base_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Linear algebra module
    linalg_content = """
module linear_algebra
  use iso_fortran_env, only: real64
  implicit none

contains

  subroutine matrix_multiply(A, B, C, n)
    integer, intent(in) :: n
    real(real64), intent(in) :: A(n,n), B(n,n)
    real(real64), intent(out) :: C(n,n)
    integer :: i, j, k
    
    do i = 1, n
      do j = 1, n
        C(i,j) = 0.0_real64
        do k = 1, n
          C(i,j) = C(i,j) + A(i,k) * B(k,j)
        end do
      end do
    end do
  end subroutine matrix_multiply

  function determinant_2x2(A) result(det)
    real(real64), intent(in) :: A(2,2)
    real(real64) :: det
    
    det = A(1,1) * A(2,2) - A(1,2) * A(2,1)
  end function determinant_2x2

end module linear_algebra
"""

    # Numerical methods module
    numerical_content = """
module numerical_methods
  use iso_fortran_env, only: real64
  use linear_algebra, only: matrix_multiply
  implicit none

contains

  subroutine solve_linear_system(A, b, x, n)
    integer, intent(in) :: n
    real(real64), intent(in) :: A(n,n), b(n)
    real(real64), intent(out) :: x(n)
    
    ! Simplified Gaussian elimination
    real(real64) :: A_work(n,n), b_work(n)
    integer :: i, j, k
    real(real64) :: factor
    
    A_work = A
    b_work = b
    
    ! Forward elimination
    do k = 1, n-1
      do i = k+1, n
        factor = A_work(i,k) / A_work(k,k)
        do j = k+1, n
          A_work(i,j) = A_work(i,j) - factor * A_work(k,j)
        end do
        b_work(i) = b_work(i) - factor * b_work(k)
      end do
    end do
    
    ! Back substitution
    do i = n, 1, -1
      x(i) = b_work(i)
      do j = i+1, n
        x(i) = x(i) - A_work(i,j) * x(j)
      end do
      x(i) = x(i) / A_work(i,i)
    end do
  end subroutine solve_linear_system

end module numerical_methods
"""

    # Write files
    (src_dir / "linear_algebra.f90").write_text(linalg_content)
    (src_dir / "numerical_methods.f90").write_text(numerical_content)

    print(f"Created sample scientific computing project at: {base_path}")


def demonstrate_configuration_templates():
    """Demonstrate available configuration templates."""
    print("\n" + "=" * 60)
    print("CONFIGURATION TEMPLATES DEMONSTRATION")
    print("=" * 60)

    manager = ConfigurationManager()

    print("Available templates:")
    for template in manager.list_templates():
        print(f"  - {template}")

    print("\nTemplate details:")
    for template in manager.list_templates():
        info = manager.get_template_info(template)
        print(f"\n{template}:")
        print(f"  Project type: {info.get('project_name', 'N/A')}")
        print(f"  Source dirs: {info.get('source_dirs', [])}")
        print(f"  Extensions: {info.get('fortran_extensions', [])}")
        if info.get("system_modules"):
            print(
                f"  System modules: {info['system_modules'][:3]}{'...' if len(info['system_modules']) > 3 else ''}"
            )


def demonstrate_ctsm_analysis():
    """Demonstrate analysis of CTSM-like project."""
    print("\n" + "=" * 60)
    print("CTSM PROJECT ANALYSIS DEMONSTRATION")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir)
        create_sample_ctsm_structure(project_path)

        # Create analyzer with CTSM template
        print("\nCreating analyzer with CTSM template...")
        analyzer = create_analyzer_for_project(
            str(project_path),
            template="ctsm",
            output_dir="ctsm_demo_output",
            generate_graphs=False,  # Disable for demo
        )

        print(f"Project: {analyzer.config.project_name}")
        print(f"Source dirs: {analyzer.config.source_dirs}")
        print(f"System modules: {len(analyzer.config.system_modules)} configured")

        # Run analysis
        print("\nRunning analysis...")
        results = analyzer.analyze(save_results=False)

        # Display results
        parsing = results["parsing"]
        print(f"\nParsing Results:")
        print(f"  Modules found: {len(parsing['modules'])}")
        print(f"  Total files: {parsing['statistics']['total_files']}")
        print(f"  Total lines: {parsing['statistics']['total_lines']}")
        print(f"  Subroutines: {parsing['statistics']['total_subroutines']}")
        print(f"  Functions: {parsing['statistics']['total_functions']}")
        print(f"  Types: {parsing['statistics']['total_types']}")

        # Show modules and their dependencies
        print(f"\nModules and Dependencies:")
        for module_name, module_info in parsing["modules"].items():
            uses = [use["module"] for use in module_info.uses]
            print(f"  {module_name}: uses {uses}")

        # Translation units
        translation = results["translation"]
        print(f"\nTranslation Analysis:")
        print(f"  Translation units: {translation['units']}")

        t_stats = translation["statistics"]
        if "units_by_effort" in t_stats:
            effort_stats = t_stats["units_by_effort"]
            print(f"  Low effort: {effort_stats.get('low', 0)}")
            print(f"  Medium effort: {effort_stats.get('medium', 0)}")
            print(f"  High effort: {effort_stats.get('high', 0)}")

        # Translation order
        order = analyzer.get_translation_order()
        print(f"\nRecommended translation order: {order}")

        # Recommendations
        recommendations = results["recommendations"]
        print(f"\nRecommendations:")
        for category, items in recommendations.items():
            if items:
                print(f"  {category.replace('_', ' ').title()}:")
                for item in items:
                    print(f"    - {item}")


def demonstrate_scientific_analysis():
    """Demonstrate analysis of scientific computing project."""
    print("\n" + "=" * 60)
    print("SCIENTIFIC COMPUTING PROJECT ANALYSIS")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir)
        create_sample_scientific_project(project_path)

        # Quick analysis
        print("\nRunning quick analysis...")
        results = quick_analyze(str(project_path), template="scientific_computing")

        # Display results
        parsing = results["parsing"]
        print(f"\nResults:")
        print(f"  Modules: {len(parsing['modules'])}")
        print(f"  Files: {parsing['statistics']['total_files']}")
        print(f"  Lines: {parsing['statistics']['total_lines']}")

        # Show dependency structure
        dependencies = results["dependencies"]
        print(f"\nDependency Analysis:")
        print(f"  Module dependencies: {dependencies['module_graph_summary']['edges']}")

        if dependencies["analysis"]["external_dependencies"]:
            print(
                f"  External deps: {dependencies['analysis']['external_dependencies']}"
            )


def demonstrate_custom_configuration():
    """Demonstrate custom configuration creation."""
    print("\n" + "=" * 60)
    print("CUSTOM CONFIGURATION DEMONSTRATION")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir)
        src_dir = project_path / "lib"
        src_dir.mkdir()

        # Create a simple module
        (src_dir / "custom.f90").write_text(
            """
module custom_module
  implicit none
contains
  subroutine custom_procedure()
    print *, "Custom procedure"
  end subroutine
end module
"""
        )

        # Create custom configuration
        from fortran_analyzer.config.project_config import FortranProjectConfig

        config = FortranProjectConfig(
            project_name="Custom Fortran Project",
            project_root=str(project_path),
            source_dirs=["lib"],  # Non-standard directory
            fortran_extensions=[".f90"],
            max_translation_unit_lines=60,  # Smaller units
            fortran_standard="f2008",
            external_libraries=["custom_lib"],
            generate_graphs=False,
        )

        print("Custom configuration created:")
        print(f"  Project: {config.project_name}")
        print(f"  Source dirs: {config.source_dirs}")
        print(f"  Max unit lines: {config.max_translation_unit_lines}")
        print(f"  Fortran standard: {config.fortran_standard}")

        # Analyze with custom config
        analyzer = FortranAnalyzer(config)
        results = analyzer.analyze(save_results=False)

        print(f"\nAnalysis with custom config:")
        print(f"  Found {len(results['parsing']['modules'])} modules")


def demonstrate_comparison():
    """Demonstrate comparing different project configurations."""
    print("\n" + "=" * 60)
    print("PROJECT COMPARISON DEMONSTRATION")
    print("=" * 60)

    templates = ["generic", "scientific_computing", "numerical_library"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir)
        create_sample_scientific_project(project_path)

        print("Analyzing same project with different templates:\n")

        for template in templates:
            print(f"Template: {template}")

            config = create_default_config(str(project_path), template)
            print(f"  Max unit lines: {config.max_translation_unit_lines}")
            print(f"  System modules: {len(config.system_modules)}")
            print(f"  External libs: {len(config.external_libraries)}")

            # Quick analysis
            try:
                results = quick_analyze(str(project_path), template=template)
                t_stats = results["translation"]["statistics"]
                print(f"  Translation units: {t_stats.get('total_units', 0)}")
            except Exception as e:
                print(f"  Analysis failed: {e}")

            print()


def main():
    """Main demonstration function."""
    print("FORTRAN ANALYZER - REFACTORED FRAMEWORK DEMONSTRATION")
    print("=" * 70)
    print("This demonstrates the refactored Fortran Analyzer that works")
    print("with any Fortran codebase, not just CLM/CTSM.")
    print("=" * 70)

    try:
        # Demonstrate configuration templates
        demonstrate_configuration_templates()

        # Demonstrate CTSM analysis
        demonstrate_ctsm_analysis()

        # Demonstrate scientific computing analysis
        demonstrate_scientific_analysis()

        # Demonstrate custom configuration
        demonstrate_custom_configuration()

        # Demonstrate comparison
        demonstrate_comparison()

        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("Key improvements in the refactored framework:")
        print("  ✓ Generic Fortran parser (works with any codebase)")
        print("  ✓ Configurable templates for different project types")
        print("  ✓ Flexible translation unit decomposition")
        print("  ✓ Comprehensive dependency analysis")
        print("  ✓ Multiple output formats and visualizations")
        print("  ✓ Command-line interface and Python API")
        print("  ✓ Extensive documentation and examples")
        print("  ✓ Unit tests for validation")

        print("\nTo use with your own projects:")
        print("  1. Choose appropriate template or create custom config")
        print("  2. Run: fortran-analyzer analyze /path/to/project")
        print("  3. Review generated analysis results and visualizations")

    except KeyboardInterrupt:
        print("\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\nDemonstration failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
