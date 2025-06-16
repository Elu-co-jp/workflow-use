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
