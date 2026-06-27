"""
Verification script to check imports and dependencies.
Run this to verify the project is set up correctly.
"""

import sys
import importlib
from pathlib import Path

def check_import(module_name: str, display_name: str = None) -> bool:
    """Check if a module can be imported."""
    display = display_name or module_name
    try:
        importlib.import_module(module_name)
        print(f"✓ {display}")
        return True
    except ImportError as e:
        print(f"✗ {display} - {e}")
        return False


def main():
    """Run verification checks."""
    print("=" * 60)
    print("FocusLens - Dependency Verification")
    print("=" * 60)
    print()

    # Check Python version
    print("📦 Python Version Check")
    print(f"Python: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✓ Python 3.8+")
    else:
        print("✗ Python 3.8+ required")
    print()

    # Check external dependencies
    print("📦 External Dependencies")
    external_deps = [
        ("streamlit", "Streamlit"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("google.generativeai", "Google Generative AI"),
        ("requests", "Requests"),
        ("pyttsx3", "pyttsx3"),
        ("plotly", "Plotly"),
        ("pandas", "Pandas"),
        ("dotenv", "python-dotenv"),
        ("PIL", "Pillow"),
    ]

    all_ok = True
    for module, display in external_deps:
        if not check_import(module, display):
            all_ok = False

    print()

    # Check internal modules
    print("📦 Internal Modules")
    internal_modules = [
        "config",
        "database.database",
        "models.session",
        "services.logger_service",
        "services.camera_service",
        "services.vision_service",
        "services.gemini_service",
        "services.voice_service",
        "services.session_service",
        "services.focus_service",
        "services.analytics_service",
        "ui.dashboard",
        "ui.cards",
        "ui.charts",
        "ui.camera_view",
        "utils.constants",
        "utils.helpers",
        "utils.prompts",
        "utils.styles",
    ]

    for module in internal_modules:
        if not check_import(module):
            all_ok = False

    print()
    print("=" * 60)

    if all_ok:
        print("✅ All checks passed! Ready to run FocusLens")
        print()
        print("Next steps:")
        print("1. Configure .env file with your API keys")
        print("2. Run: streamlit run app.py")
        return 0
    else:
        print("❌ Some checks failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
