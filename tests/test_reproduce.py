"""Golden-output reproduction check: python reproduce.py check must exit 0."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_reproduce_check_alberta():
    res = subprocess.run([sys.executable, "reproduce.py", "check"],
                         cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, f"reproduce.py check failed:\n{res.stdout}\n{res.stderr}"


def test_reproduce_check_texas():
    res = subprocess.run([sys.executable, "reproduce.py", "check", "--texas"],
                         cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, f"texas check failed:\n{res.stdout}\n{res.stderr}"
