"""
Plugin Validator - Validates and fixes plugin configuration files.

Handles hooks.json schema validation and .mcp.json syntax validation.
"""

import json
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ValidationType(str, Enum):
    HOOKS = "hooks"
    MCP = "mcp"


class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    FIXED = "fixed"


@dataclass(frozen=True)
class ValidationResult:
    plugin_name: str
    plugin_version: str
    validation_type: ValidationType
    status: ValidationStatus
    file_path: str
    errors: list[str]
    fixed_content: Optional[str] = None


class HooksJsonValidator:
    """Validates hooks.json files against expected schema."""

    # Expected schema: {"hooks": {}}
    EXPECTED_SCHEMA = {"hooks": {}}

    def validate(self, content: str, file_path: str) -> tuple[bool, list[str]]:
        """
        Validate hooks.json content.

        Returns (is_valid, list_of_errors)
        """
        errors = []

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}"]

        # Check root is an object
        if not isinstance(parsed, dict):
            return False, [f"Root must be an object, got {type(parsed).__name__}"]

        # Check for 'hooks' key
        if "hooks" not in parsed:
            errors.append("Missing required 'hooks' key")

        # Check hooks value is an object
        elif not isinstance(parsed["hooks"], dict):
            errors.append(f"'hooks' must be an object, got {type(parsed['hooks']).__name__}")

        # Check for bare array (the common bug)
        if isinstance(parsed, list):
            errors.append("Root is an array [] instead of object with 'hooks' key")

        return len(errors) == 0, errors

    def fix(self, content: str) -> str:
        """Fix invalid hooks.json by returning correct schema."""
        try:
            parsed = json.loads(content)
            # If it's a bare array, replace with correct schema
            if isinstance(parsed, list):
                return json.dumps(self.EXPECTED_SCHEMA, indent=2)
            # If it's an object but missing hooks or hooks is not dict
            if isinstance(parsed, dict):
                if "hooks" not in parsed or not isinstance(parsed.get("hooks"), dict):
                    return json.dumps(self.EXPECTED_SCHEMA, indent=2)
            return content
        except json.JSONDecodeError:
            # Completely invalid JSON, return default
            return json.dumps(self.EXPECTED_SCHEMA, indent=2)


class McpJsonValidator:
    """Validates .mcp.json files for syntax correctness."""

    def validate(self, content: str, file_path: str) -> tuple[bool, list[str]]:
        """
        Validate .mcp.json content for syntax errors.

        Returns (is_valid, list_of_errors)
        """
        errors = []

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}"]

        # Check root is an object
        if not isinstance(parsed, dict):
            errors.append(f"Root must be an object, got {type(parsed).__name__}")

        # Check each connector has required fields
        for key, value in parsed.items():
            if not isinstance(value, dict):
                errors.append(f"Connector '{key}' must be an object")
                continue
            if "url" not in value:
                errors.append(f"Connector '{key}' missing required 'url' field")

        return len(errors) == 0, errors

    def fix(self, content: str) -> Optional[str]:
        """
        Attempt to fix common .mcp.json syntax errors.

        Handles missing commas and unclosed braces.
        Returns fixed content or None if unfixable.
        """
        try:
            # First try parsing as-is
            json.loads(content)
            return content  # Already valid
        except json.JSONDecodeError as e:
            # Try to fix common issues
            fixed = self._attempt_fix(content, e)
            if fixed:
                try:
                    json.loads(fixed)
                    return fixed
                except json.JSONDecodeError:
                    pass
            return None

    def _attempt_fix(self, content: str, error: json.JSONDecodeError) -> Optional[str]:
        """Attempt to fix JSON based on error type."""
        lines = content.splitlines()

        # Missing comma between objects
        if "Expecting ',' delimiter" in error.msg:
            # The error is on the line where the next key starts, but comma needs to go on previous line
            line_idx = error.lineno - 2  # Previous line
            if 0 <= line_idx < len(lines):
                line = lines[line_idx].rstrip()
                # If line ends with } and next non-empty line starts with "key":
                for i in range(line_idx + 1, len(lines)):
                    next_line = lines[i].strip()
                    if next_line and not next_line.startswith("//"):
                        if next_line.startswith('"') and ':' in next_line:
                            # Add comma to previous line
                            lines[line_idx] = line + ","
                            return "\n".join(lines)
                        break

        # Unclosed brace - missing } at end
        if "Expecting '}'" in error.msg or "Expecting value" in error.msg:
            # Count braces
            open_braces = content.count("{")
            close_braces = content.count("}")
            if open_braces > close_braces:
                # Add missing closing braces
                return content + "}" * (open_braces - close_braces)

        return None


class PluginValidator:
    """Main plugin validator coordinating hooks and MCP validation."""

    def __init__(self):
        self.hooks_validator = HooksJsonValidator()
        self.mcp_validator = McpJsonValidator()

    def validate_plugin_directory(self, plugin_dir: Path) -> list[ValidationResult]:
        """Validate all config files in a plugin directory."""
        results = []

        # Check hooks.json
        hooks_path = plugin_dir / "hooks" / "hooks.json"
        if hooks_path.exists():
            content = hooks_path.read_text()
            is_valid, errors = self.hooks_validator.validate(content, str(hooks_path))
            status = ValidationStatus.PASSED if is_valid else ValidationStatus.FAILED
            fixed_content = None
            if not is_valid:
                fixed_content = self.hooks_validator.fix(content)
            results.append(ValidationResult(
                plugin_name=plugin_dir.name,
                plugin_version="unknown",  # Would be read from plugin manifest
                validation_type=ValidationType.HOOKS,
                status=status,
                file_path=str(hooks_path),
                errors=errors,
                fixed_content=fixed_content,
            ))

        # Check .mcp.json
        mcp_path = plugin_dir / ".mcp.json"
        if mcp_path.exists():
            content = mcp_path.read_text()
            is_valid, errors = self.mcp_validator.validate(content, str(mcp_path))
            status = ValidationStatus.PASSED if is_valid else ValidationStatus.FAILED
            fixed_content = None
            if not is_valid:
                fixed_content = self.mcp_validator.fix(content)
            results.append(ValidationResult(
                plugin_name=plugin_dir.name,
                plugin_version="unknown",
                validation_type=ValidationType.MCP,
                status=status,
                file_path=str(mcp_path),
                errors=errors,
                fixed_content=fixed_content,
            ))

        return results

    def validate_all_plugins(self, plugins_root: Path) -> list[ValidationResult]:
        """Validate all plugins in a marketplace directory."""
        all_results = []
        for plugin_dir in plugins_root.iterdir():
            if plugin_dir.is_dir():
                all_results.extend(self.validate_plugin_directory(plugin_dir))
        return all_results

    def fix_all_plugins(self, plugins_root: Path, dry_run: bool = True) -> list[ValidationResult]:
        """Fix all invalid plugin config files."""
        results = self.validate_all_plugins(plugins_root)
        fixed_results = []

        for result in results:
            if result.status == ValidationStatus.FAILED and result.fixed_content:
                if not dry_run:
                    Path(result.file_path).write_text(result.fixed_content)
                    result = ValidationResult(
                        plugin_name=result.plugin_name,
                        plugin_version=result.plugin_version,
                        validation_type=result.validation_type,
                        status=ValidationStatus.FIXED,
                        file_path=result.file_path,
                        errors=result.errors,
                        fixed_content=result.fixed_content,
                    )
                fixed_results.append(result)

        return fixed_results