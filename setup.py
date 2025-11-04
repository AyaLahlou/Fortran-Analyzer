#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split("\n")
    requirements = [
        req.strip() for req in requirements if req.strip() and not req.startswith("#")
    ]

setup(
    name="fortran-analyzer",
    version="1.0.0",
    author="Fortran Analyzer Team",
    author_email="",
    description="A generic framework for analyzing Fortran codebases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fortran-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "types-PyYAML",
        ],
        "fparser": [
            "fparser>=0.2.0",
        ],
        "interactive": [
            "plotly>=5.0",
            "jupyter",
            "ipywidgets",
        ],
        "full": [
            "fparser>=0.2.0",
            "plotly>=5.0",
            "seaborn>=0.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "fortran-analyzer=fortran_analyzer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fortran-analyzer/issues",
        "Documentation": "https://github.com/yourusername/fortran-analyzer/wiki",
        "Source": "https://github.com/yourusername/fortran-analyzer",
    },
    keywords="fortran analysis parsing translation code-conversion",
)
