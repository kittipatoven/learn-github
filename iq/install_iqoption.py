"""
Installation Script - Install IQ Option API dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Install required packages for IQ Option API"""
    print("🚀 Installing IQ Option API dependencies...")
    
    required_packages = [
        "iqoptionapi>=7.1.0",
        "requests>=2.28.0",
        "aiohttp>=3.8.0"
    ]
    
    failed_packages = []
    
    for package in required_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "="*50)
    if failed_packages:
        print(f"❌ Installation failed for: {', '.join(failed_packages)}")
        print("Please install these packages manually:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return 1
    else:
        print("✅ All IQ Option API dependencies installed successfully!")
        print("\nYou can now run the application with:")
        print("  python main.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
