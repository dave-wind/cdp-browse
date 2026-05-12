#!/usr/bin/env python3
"""
cdp-browse 发布脚本

Usage:
    python release.py patch    # 0.2.1 -> 0.3.0
    python release.py minor    # 0.2.1 -> 0.3.0
    python release.py major    # 0.2.1 -> 1.0.0
    python release.py 1.2.3    # 指定版本号
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
PYPROJECT = ROOT / "pyproject.toml"
PYTHON = sys.executable


def run(cmd, check=True):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, check=check, cwd=ROOT)


def get_current_version():
    text = PYPROJECT.read_text()
    m = re.search(r'version\s*=\s*"([^"]+)"', text)
    if not m:
        print("ERROR: version not found in pyproject.toml")
        sys.exit(1)
    return m.group(1)


def set_version(new_version):
    text = PYPROJECT.read_text()
    text = re.sub(r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', text)
    PYPROJECT.write_text(text)


def bump_version(current, part):
    major, minor, patch = map(int, current.split("."))
    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0
    return f"{major}.{minor}.{patch}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]
    current = get_current_version()

    # 确定新版本号
    if re.match(r"^\d+\.\d+\.\d+$", arg):
        new_version = arg
    elif arg in ("patch", "minor", "major"):
        new_version = bump_version(current, arg)
    else:
        print(f"ERROR: invalid argument '{arg}'")
        print(__doc__)
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  Release: {current} -> {new_version}")
    print(f"{'='*50}\n")

    # 1. 修改版本号
    print(f"[1/6] Updating version to {new_version}")
    set_version(new_version)
    print(f"  Done: pyproject.toml\n")

    # 2. 清理旧构建
    print("[2/6] Cleaning old builds")
    for d in ["dist", "build"]:
        p = ROOT / d
        if p.exists():
            import shutil
            shutil.rmtree(p)
            print(f"  Removed {d}/")
    for egg in ROOT.glob("*.egg-info"):
        import shutil
        shutil.rmtree(egg)
        print(f"  Removed {egg.name}/")
    print()

    # 3. 构建
    print("[3/6] Building package")
    run(f"{PYTHON} -m build")
    print()

    # 4. 发布到 PyPI
    print("[4/6] Uploading to PyPI")
    run(f"{PYTHON} -m twine upload dist/*")
    print()

    # 5. 等待 PyPI 索引刷新 + uvx 验证
    print("[5/6] Verifying via uvx (waiting for PyPI index...)")
    import time
    time.sleep(25)
    run(f"uvx --from cdp-browse=={new_version} cdp-browse --help")
    print()

    # 6. Git commit
    print("[6/6] Git commit (not pushed)")
    run("git add -A")
    run(f'git commit -m "release: v{new_version}"', check=False)
    print()

    print(f"{'='*50}")
    print(f"  Released v{new_version}")
    print(f"  https://pypi.org/project/cdp-browse/{new_version}/")
    print(f"{'='*50}")
    print()
    print("  To push: git push")


if __name__ == "__main__":
    main()
