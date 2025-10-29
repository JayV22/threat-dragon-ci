import shutil
import subprocess
import sys

CHECKS = [
    ("pytest", ["pytest", "-q"]),
    ("flake8", ["flake8"]),
]


def available(command):
    return shutil.which(command) is not None


def run_check(name, cmd):
    print(f"Running {name}: {' '.join(cmd)}")
    try:
        completed = subprocess.run(cmd, check=False)
        return completed.returncode
    except FileNotFoundError:
        print(f"{name} not found, skipping.")
        return 0


def main():
    missing = [name for name, cmd in CHECKS if not available(cmd[0])]
    if missing:
        print("Tools not found, will skip if necessary:", ", ".join(missing))

    failed = []
    for name, cmd in CHECKS:
        if not available(cmd[0]):
            print(f"Skipping {name} (not installed).")
            continue
        rc = run_check(name, cmd)
        if rc != 0:
            failed.append((name, rc))

    if failed:
        for name, rc in failed:
            print(f"{name} failed (exit code {rc})")
        sys.exit(1)

    print("All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()