from pathlib import Path
import subprocess
import sys


def main():
    ui_path = Path(__file__).with_name("ui.py")
    cmd = [sys.executable, "-m", "streamlit", "run", str(ui_path)]
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
