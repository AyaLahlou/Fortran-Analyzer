#!/bin/bash

# Fortran Analyzer - GitHub Repository Setup Script
# This script helps prepare the repository for publishing to GitHub

set -e

echo "🚀 Fortran Analyzer - GitHub Repository Setup"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo "❌ Error: Please run this script from the fortran-analyzer root directory"
    exit 1
fi

echo "✅ Found fortran-analyzer project structure"

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files to git
echo "📁 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Committing initial files..."
    git commit -m "Initial commit: Fortran Analyzer v1.0.0

Features:
- Generic Fortran parsing (F77-F2008)
- Module dependency analysis
- Translation unit decomposition
- Call graph generation
- Multiple output formats
- CLI and Python API
- Project templates
- Comprehensive documentation"
    echo "✅ Initial commit created"
fi

# Set up main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "🌿 Setting up main branch..."
    git branch -M main
    echo "✅ Switched to main branch"
fi

echo ""
echo "🎯 Next Steps for GitHub Publication:"
echo "====================================="
echo ""
echo "1. Create GitHub Repository:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: fortran-analyzer"
echo "   - Description: A generic framework for analyzing Fortran codebases"
echo "   - Make it public"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Add GitHub Remote:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/fortran-analyzer.git"
echo ""
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. Set up GitHub Features:"
echo "   - Enable Issues and Discussions"
echo "   - Set up branch protection rules"
echo "   - Configure GitHub Pages (optional)"
echo "   - Add repository topics: fortran, code-analysis, parsing, translation"
echo ""
echo "5. Configure Secrets (for PyPI publishing):"
echo "   - Go to Settings > Secrets and variables > Actions"
echo "   - Add PYPI_API_TOKEN secret for automated publishing"
echo ""
echo "6. Verify CI/CD:"
echo "   - GitHub Actions should run automatically on push"
echo "   - Check the Actions tab after pushing"
echo ""

# Show repository statistics
echo "📊 Repository Statistics:"
echo "========================"
echo "Files: $(find . -type f | grep -v .git | wc -l)"
echo "Source code files: $(find src -name "*.py" | wc -l)"
echo "Test files: $(find tests -name "*.py" | wc -l)"
echo "Documentation files: $(find docs -name "*.md" | wc -l)"
echo "Total lines of code: $(find src -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')"
echo ""

# Validate key files exist
echo "🔍 Validating repository structure..."
required_files=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    "CHANGELOG.md"
    "SECURITY.md"
    "setup.py"
    "requirements.txt"
    ".gitignore"
    ".github/workflows/ci.yml"
    ".github/workflows/publish.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
    fi
done

echo ""
echo "🎉 Repository is ready for GitHub publication!"
echo ""
echo "Quick command summary:"
echo "====================="
echo "# After creating the GitHub repository:"
echo "git remote add origin https://github.com/YOUR_USERNAME/fortran-analyzer.git"
echo "git push -u origin main"
echo ""
echo "🌟 Don't forget to:"
echo "- Update the GitHub URL in setup.py and README.md"
echo "- Add repository topics and description"
echo "- Set up branch protection"
echo "- Configure release automation"