#!/usr/bin/env python3
"""Build a source-only, dependency-free ZIP from the maintained file allowlist."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


SOURCE_FILES = {
    '.gitignore',
    'LICENSE.md',
    'SKILL.md',
    'agents/openai.yaml',
    'assets/application-queue-template.json',
    'assets/candidate-profile-template.json',
    'references/batch-application.md',
    'references/browser-control.md',
    'references/browser-control.zh-CN.md',
    'references/calibration-and-efficiency.md',
    'references/fill-and-safety.md',
    'references/fill-and-safety.zh-CN.md',
    'references/intake-and-profile.md',
    'references/intake-and-profile.zh-CN.md',
    'references/platform-adapters.md',
    'scripts/browser-bridge/browser_bridge.js',
    'scripts/browser-bridge/native_cdp_launcher.js',
    'scripts/browser-bridge/package-lock.json',
    'scripts/browser-bridge/package.json',
    'scripts/browser-bridge/profile_resolver.js',
    'scripts/browser-bridge/tests/profile_resolver.test.js',
    'scripts/package_skill.py',
    'scripts/profile_guard.py',
    'scripts/tests/test_package_skill.py',
}


def should_include(path: Path, root: Path, output: Path) -> bool:
    relative = path.relative_to(root)
    if str(relative) not in SOURCE_FILES or path.resolve() == output.resolve():
        return False
    if any(part.is_symlink() for part in (path, *path.parents) if part != root.parent):
        return False
    return path.is_file()


def build_zip(root: Path, output: Path) -> int:
    root = root.resolve()
    output = output.resolve()
    if not (root / "SKILL.md").is_file():
        raise SystemExit(f"SKILL.md not found under {root}")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [path for path in sorted(root.rglob("*")) if should_include(path, root, output)]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, Path(root.name) / path.relative_to(root))
    return len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path.cwd() / "resume-autofill-agent.zip")
    args = parser.parse_args()
    count = build_zip(args.skill_dir, args.output)
    print(f"Created {args.output.resolve()} with {count} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
