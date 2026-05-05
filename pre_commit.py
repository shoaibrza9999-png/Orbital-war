import sys
import subprocess

def run_pre_commit():
    print("Running pre-commit checks...")
    result = subprocess.run(["python3", "evaluate.py"], capture_output=True, text=True)

    tests_passed = True

    if "Results for my_bot.py (P1) vs base_bot.py (P2):\nP1 wins: 10, P2 wins: 0, Draws: 0" not in result.stdout:
        tests_passed = False
    if "Results for base_bot.py (P1) vs my_bot.py (P2):\nP1 wins: 0, P2 wins: 10, Draws: 0" not in result.stdout:
        tests_passed = False

    if tests_passed:
        print("Pre-commit passed: Bot consistently wins.")
        sys.exit(0)
    else:
        print("Pre-commit failed:")
        print(result.stdout)
        sys.exit(1)

if __name__ == "__main__":
    run_pre_commit()
