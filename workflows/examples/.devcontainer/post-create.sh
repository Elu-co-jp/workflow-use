#!/bin/bash
set -e

echo "🚀 Setting up Workflow Use development environment..."

# Navigate to the workspace root
cd /workspace

# Check if we're in the examples directory structure
if [ -f "../../pyproject.toml" ]; then
    echo "📦 Found pyproject.toml in parent directory"
    cd ../..
elif [ -f "pyproject.toml" ]; then
    echo "📦 Found pyproject.toml in current directory"
else
    echo "⚠️  Could not find pyproject.toml"
fi

# Install Python with uv
echo "🐍 Installing Python with uv..."
uv python install 3.12

# Create virtual environment and install dependencies
echo "📚 Creating virtual environment and installing dependencies..."
uv venv
source .venv/bin/activate

# Install the project in development mode
if [ -f "pyproject.toml" ]; then
    echo "📦 Installing workflow-use package..."
    uv pip install -e .
    
    # Install additional development dependencies
    echo "🛠️  Installing development dependencies..."
    uv pip install \
        pytest \
        pytest-asyncio \
        pytest-cov \
        black \
        ruff \
        mypy \
        ipython
fi

# Install browser-use if not already installed
echo "🌐 Checking browser-use installation..."
if ! uv pip show browser-use > /dev/null 2>&1; then
    echo "📦 Installing browser-use..."
    uv pip install browser-use
fi

# Create a simple test script
echo "📝 Creating test script..."
cat > /workspace/test_setup.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify the development environment setup."""

import sys
import subprocess

def check_command(cmd, name):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {name} is installed")
            return True
        else:
            print(f"❌ {name} is not working properly")
            return False
    except Exception as e:
        print(f"❌ Error checking {name}: {e}")
        return False

def main():
    print("🔍 Checking development environment...\n")
    
    all_good = True
    
    # Check uv
    if check_command("uv --version", "uv"):
        print(f"   Version: {subprocess.check_output('uv --version', shell=True).decode().strip()}")
    else:
        all_good = False
    
    # Check Python
    if check_command("python --version", "Python"):
        print(f"   Version: {sys.version.split()[0]}")
    else:
        all_good = False
    
    # Check workflow-use
    try:
        import workflow_use
        print("✅ workflow-use is installed")
    except ImportError:
        print("❌ workflow-use is not installed")
        all_good = False
    
    # Check browser-use
    try:
        import browser_use
        print("✅ browser-use is installed")
    except ImportError:
        print("❌ browser-use is not installed")
        all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("✅ All checks passed! Your environment is ready.")
    else:
        print("⚠️  Some checks failed. Please review the output above.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x /workspace/test_setup.py

# Set up git
echo "🔧 Configuring git..."
git config --global --add safe.directory /workspace

# Create convenience aliases
echo "🎯 Setting up convenient aliases..."
cat >> ~/.zshrc << 'EOF'

# Workflow Use aliases
alias wf='cd /workspace'
alias uvactivate='source /workspace/.venv/bin/activate'
alias uvinstall='uv pip install -e /workspace'
alias runtest='cd /workspace && python test_setup.py'
alias runworkflow='cd /workspace/workflows/examples && python'

# Auto-activate virtual environment
if [ -f "/workspace/.venv/bin/activate" ]; then
    source /workspace/.venv/bin/activate
fi
EOF

echo "✅ Development environment setup complete!"
echo ""
echo "📚 Quick start commands:"
echo "   - runtest: Check your environment setup"
echo "   - wf: Navigate to workspace"
echo "   - uvactivate: Activate virtual environment"
echo "   - python csv_runner.py: Run the CSV workflow runner"
echo ""
echo "🎉 Happy coding!"