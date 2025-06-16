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

# Build browser extension for workflow recording
echo "🔧 Building browser extension..."
if [ -d "/workspace/extension" ]; then
    cd /workspace/extension
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing extension dependencies..."
        npm install > /dev/null 2>&1
    fi
    if [ ! -d ".output/chrome-mv3" ]; then
        echo "🔨 Building extension..."
        npm run build > /dev/null 2>&1
    fi
    cd /workspace
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

# VNC and browser viewing aliases
alias startvnc='supervisord -c ~/.config/supervisor/supervisord.conf'
alias stopvnc='supervisorctl -c ~/.config/supervisor/supervisord.conf shutdown'
alias vnc-status='supervisorctl -c ~/.config/supervisor/supervisord.conf status'
alias browser-view='echo "🌐 Open http://localhost:6080/vnc.html in your browser to see the desktop"'

# Auto-activate virtual environment
if [ -f "/workspace/.venv/bin/activate" ]; then
    source /workspace/.venv/bin/activate
fi
EOF

# Set up VNC server configuration
echo "🖥️  Setting up VNC server configuration..."
mkdir -p ~/.config/supervisor

# Create supervisor configuration
cat > ~/.config/supervisor/supervisord.conf << 'ENDCONFIG'
[supervisord]
nodaemon=false
user=vscode
pidfile=/tmp/supervisord.pid
logfile=/tmp/supervisord.log

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

[unix_http_server]
file=/tmp/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[program:xvfb]
command=/usr/bin/Xvfb :99 -screen 0 1280x1024x24
autorestart=true
user=vscode
priority=100
stdout_logfile=/tmp/xvfb.log
stderr_logfile=/tmp/xvfb.err

[program:x11vnc]
command=/usr/bin/x11vnc -display :99 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever
autorestart=true
user=vscode
priority=200
stdout_logfile=/tmp/x11vnc.log
stderr_logfile=/tmp/x11vnc.err

[program:fluxbox]
command=/usr/bin/fluxbox
autorestart=true
user=vscode
environment=DISPLAY=:99
priority=300
stdout_logfile=/tmp/fluxbox.log
stderr_logfile=/tmp/fluxbox.err

[program:novnc]
command=/usr/bin/websockify --web /usr/share/novnc/ 6080 localhost:5900
autorestart=true
user=vscode
priority=400
stdout_logfile=/tmp/novnc.log
stderr_logfile=/tmp/novnc.err
ENDCONFIG

# Update font cache for Japanese fonts
echo "🔤 Updating font cache for Japanese fonts..."
fc-cache -fv > /dev/null 2>&1

# Start VNC server automatically
echo "🖥️  Starting VNC server for browser viewing..."
supervisord -c ~/.config/supervisor/supervisord.conf > /dev/null 2>&1 &
sleep 3

echo "✅ Development environment setup complete!"
echo ""
echo "📚 Quick start commands:"
echo "   - runtest: Check your environment setup"
echo "   - wf: Navigate to workspace"
echo "   - uvactivate: Activate virtual environment"
echo "   - python csv_runner.py: Run the CSV workflow runner"
echo ""
echo "🖥️  Browser viewing:"
echo "   ✨ VNC server is running automatically!"
echo "   🌐 Open http://localhost:6080/vnc.html in your browser to see the desktop"
echo "   - vnc-status: Check VNC server status"
echo "   - stopvnc: Stop VNC server (if needed)"
echo "   - startvnc: Restart VNC server (if stopped)"
echo ""
echo "🎉 Happy coding!"