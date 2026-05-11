"""Aider adapter — terminal-first AI coding agent with deep git integration."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import backup_file, read_text_safe, restore_file, write_text_safe
from ..prompts import get_protocol_for_agent
from .base import AgentAdapter


def _detect_quality_tools(root: Path = Path(".")) -> dict[str, str]:
    """Auto-detect lint/test commands based on project files."""
    tools: dict[str, str] = {}

    # Python
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        if shutil.which("ruff"):
            tools["python_lint"] = "ruff check ."
        elif shutil.which("flake8"):
            tools["python_lint"] = "flake8"
        elif shutil.which("pylint"):
            tools["python_lint"] = "pylint"

        if ((root / "pytest.ini").exists() or (root / "pyproject.toml").exists()) and shutil.which("pytest"):
            tools["python_test"] = "pytest"

    # JavaScript / TypeScript
    if (root / "package.json").exists():
        pkg = root / "package.json"
        try:
            import json

            scripts = json.loads(pkg.read_text()).get("scripts", {})
            if "lint" in scripts:
                tools["js_lint"] = "npm run lint"
            elif "eslint" in scripts:
                tools["js_lint"] = "npm run eslint"
            if "test" in scripts:
                tools["js_test"] = "npm run test"
        except Exception:
            pass

    # Rust
    if (root / "Cargo.toml").exists():
        tools["rust_lint"] = "cargo clippy"
        tools["rust_test"] = "cargo test"

    # Go
    if (root / "go.mod").exists():
        tools["go_lint"] = "go vet ./..."
        tools["go_test"] = "go test ./..."

    # Java / Kotlin
    if (root / "pom.xml").exists():
        tools["java_test"] = "mvn test"
        if shutil.which("mvn"):
            tools["java_lint"] = "mvn spotbugs:check"
    elif (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        tools["java_test"] = "./gradlew test"
        if shutil.which("ktlint"):
            tools["kotlin_lint"] = "ktlint"

    # C / C++
    if (root / "CMakeLists.txt").exists():
        if shutil.which("cppcheck"):
            tools["cpp_lint"] = "cppcheck --enable=all ."
        if (root / "Makefile").exists():
            tools["cpp_test"] = "make test"
    elif (root / "Makefile").exists():
        tools["c_test"] = "make test"

    # C# (.NET)
    if any(root.glob("*.csproj")):
        tools["csharp_lint"] = "dotnet format --verify-no-changes"
        tools["csharp_test"] = "dotnet test"

    # Ruby
    if (root / "Gemfile").exists():
        if shutil.which("rubocop"):
            tools["ruby_lint"] = "rubocop"
        if shutil.which("rspec"):
            tools["ruby_test"] = "rspec"

    # PHP
    if (root / "composer.json").exists():
        if shutil.which("phpstan"):
            tools["php_lint"] = "phpstan analyse"
        if (root / "phpunit.xml").exists() or (root / "phpunit.xml.dist").exists():
            tools["php_test"] = "vendor/bin/phpunit"

    # Swift
    if (root / "Package.swift").exists():
        tools["swift_lint"] = "swiftlint"
        tools["swift_test"] = "swift test"

    # Dart / Flutter
    if (root / "pubspec.yaml").exists():
        tools["dart_lint"] = "dart analyze"
        tools["dart_test"] = "dart test"

    # Scala
    if (root / "build.sbt").exists() and shutil.which("sbt"):
        tools["scala_test"] = "sbt test"

    # TypeScript (Deno, Biome)
    if (root / "deno.json").exists() or (root / "deno.jsonc").exists():
        tools["deno_lint"] = "deno lint"
        tools["deno_test"] = "deno test"
    if (root / "biome.json").exists():
        tools["biome_lint"] = "biome check ."

    return tools


class AiderAdapter(AgentAdapter):
    name = "aider"
    display_name = "Aider"

    def detect(self) -> bool:
        return shutil.which("aider") is not None

    # ── paths ────────────────────────────────────────────────────
    def _conventions_path(self, scope: str) -> Path:
        if scope == "project":
            return Path("CONVENTIONS.md")
        return Path.home() / ".aider" / "CONVENTIONS.md"

    def _config_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".aider.conf.yml")
        return Path.home() / ".aider.conf.yml"

    def _ignore_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".aiderignore")
        return Path.home() / ".aiderignore"

    # ── backup ───────────────────────────────────────────────────
    def backup(self) -> list[Path]:
        paths = [
            self._conventions_path("user"),
            self._config_path("user"),
        ]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [
            self._conventions_path("user"),
            self._config_path("user"),
        ]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    # ── install MCP (Aider doesn't use MCP natively, but we register via conventions) ──
    def install_mcp(self, scope: str = "user") -> bool:
        return self.inject_rules(scope)

    # ── inject rules ─────────────────────────────────────────────
    def inject_rules(self, scope: str = "user") -> bool:
        root = Path(".") if scope == "project" else Path.home()

        # 1. CONVENTIONS.md
        conv_path = self._conventions_path(scope)
        protocol = get_protocol_for_agent(self.name)

        content = read_text_safe(conv_path)
        if protocol not in content:
            header = "# maru-deep-pro-search Research Protocol\n\n"
            write_text_safe(conv_path, content + "\n\n" + header + protocol + "\n")

        # 2. .aider.conf.yml — with auto-detected quality gates
        config_path = self._config_path(scope)
        raw = read_text_safe(config_path)
        lines = raw.splitlines() if raw else []

        # Ensure read: CONVENTIONS.md
        has_read = any("CONVENTIONS.md" in line for line in lines)
        if not has_read:
            lines.append('read: CONVENTIONS.md')

        # Ensure auto-lint
        has_auto_lint = any(line.strip().startswith("auto-lint:") for line in lines)
        if not has_auto_lint:
            lines.append("auto-lint: true")

        # Auto-detect and inject lint/test commands
        tools = _detect_quality_tools(root)
        lint_cmds: list[str] = []
        test_cmds: list[str] = []

        for key, cmd in tools.items():
            if "_lint" in key:
                lang = key.replace("_lint", "")
                lint_cmds.append(f'{lang}: {cmd}')
            if "_test" in key:
                lang = key.replace("_test", "")
                test_cmds.append(f'{lang}: {cmd}')

        # Only add if not already present
        existing = "\n".join(lines)
        for lc in lint_cmds:
            if lc not in existing:
                lines.append(f"lint-cmd: {lc}")
        for tc in test_cmds:
            if tc not in existing:
                lines.append(f"test-cmd: {tc}")

        # Ensure gitignore behavior
        has_gitignore = any("gitignore" in line for line in lines)
        if not has_gitignore:
            lines.append("gitignore: true")

        write_text_safe(config_path, "\n".join(lines) + "\n")

        # 3. .aiderignore — exclude harness artifacts
        ignore_path = self._ignore_path(scope)
        ignore_content = read_text_safe(ignore_path)
        maru_ignore = "# maru harness\n.maru/knowledge.db\n.maru/knowledge.db-journal\n.maru/*.bak\n"
        if ".maru/" not in ignore_content:
            write_text_safe(ignore_path, ignore_content + "\n" + maru_ignore)

        return True
