"""
Quick validation to ensure the framework works correctly.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Test imports
    from analyzer import (
        FortranAnalyzer,
        create_analyzer_for_project,
        create_default_config,
        quick_analyze,
    )
    from config.project_config import ConfigurationManager

    print("✓ All imports successful")

    # Test configuration manager
    manager = ConfigurationManager()
    templates = manager.list_templates()
    print(f"✓ Found {len(templates)} configuration templates: {templates}")

    # Test default config creation
    config = create_default_config("/tmp", template="generic")
    print(f"✓ Created default config for project: {config.project_name}")

    # Test analyzer creation
    analyzer = FortranAnalyzer(config)
    print(f"✓ Created analyzer instance")

    print("\n🎉 Framework validation successful!")
    print("The refactored Fortran Analyzer is ready for use.")

except Exception as e:
    print(f"❌ Validation failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
