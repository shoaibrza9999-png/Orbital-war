import sys
import subprocess

def run_pre_commit():
    print("Running pre-commit checks...")
    result = subprocess.run(["python3", "evaluate.py"], capture_output=True, text=True)
    if "P1 wins: 10, P2 wins: 0" in result.stdout and "P1 wins: 0, P2 wins: 10" in result.stdout:
        print("Pre-commit passed: Bot consistently wins.")
        sys.exit(0)
    else:
        print("Pre-commit failed:")
        print(result.stdout)
        sys.exit(1)

if __name__ == "__main__":
    run_pre_commit()
