import csv
import json
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, Literal

import yaml
from dotenv import dotenv_values


def find_project_root(start: Path) -> Path:
    """Walk up from *start* until a directory containing pyproject.toml is found."""
    for parent in start.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not locate project root (no pyproject.toml found).")


PROJECT_ROOT = find_project_root(Path(__file__).resolve())
CONFIG_DIR = PROJECT_ROOT / "config"
class ConfigLoader:
    """
    Loads every config file found inside the project's `config/` folder
    and merges them into attributes on this instance.

    Supported formats
    -----------------
    .env          — KEY=VALUE  (python-dotenv) — matched by suffix, any name (e.g. exemplo.env)
    .yaml / .yml  — YAML mappings
    .json         — JSON objects
    """

    SUPPORTED_LOADERS = {
        ".yaml": "_load_yaml",
        ".yml":  "_load_yaml",
        ".json": "_load_json",
    }

    def __init__(self, config_dir: Path = CONFIG_DIR):
        self.config_dir = config_dir
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

        self._load_env()
        self._load_config_files()
        pprint(vars(self))

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_env(self) -> None:
        """Load the first *.env file found in the config directory (any name)."""
        env_files = list(self.config_dir.glob("*.env"))
        if not env_files:
            print(f"No *.env file found in {self.config_dir} — skipping.")
            return
        for env_path in env_files:
            print(f"Loading env vars from: {env_path.name}")
            self._set_attributes(dotenv_values(env_path))

    def _load_config_files(self) -> None:
        for path in self.config_dir.iterdir():
            if path.name == ".env" or path.suffix.lower() == ".env":
                continue
            loader_method = self.SUPPORTED_LOADERS.get(path.suffix.lower())
            if loader_method:
                getattr(self, loader_method)(path)
            else:
                print(f"Unsupported format '{path.suffix}' — skipping {path.name}.")

    def _load_yaml(self, path: Path) -> None:
        with open(path, encoding="utf-8") as f:
            self._set_attributes(yaml.safe_load(f) or {})

    def _load_json(self, path: Path) -> None:
        with open(path, encoding="utf-8") as f:
            self._set_attributes(json.load(f))

    def _set_attributes(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Return the config value for *key*, or *default* if absent."""
        return getattr(self, key, default)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, data: Any, filename: str, output_format: Literal["csv", "json", "md"]) -> Path:
        """
        Save *data* to the directory configured in ``self.save_paths[output_format]``.

        Args:
            data:          Content to write (type must match *output_format*).
            filename:      Base filename — the correct extension is applied automatically.
            output_format: One of ``"csv"``, ``"json"``, or ``"md"``.

        Returns:
            Absolute path of the written file.
        """
        save_paths: Dict[str, str] = self.get("save_paths") or {}
        if output_format not in save_paths:
            raise KeyError(
                f"No save path configured for '{output_format}'. "
                f"Available: {list(save_paths.keys())}"
            )

        output_dir = PROJECT_ROOT / save_paths[output_format]
        output_dir.mkdir(parents=True, exist_ok=True)

        extension = ".md" if output_format == "md" else f".{output_format}"
        target = output_dir / f"{Path(filename).stem}{extension}"

        writers = {
            "csv":  self._save_csv,
            "json": self._save_json,
            "md":   self._save_md,
        }
        writers[output_format](data, target)
        return target

    def _save_csv(self, data: Any, path: Path) -> None:
        if hasattr(data, "to_csv"):          # pandas DataFrame
            data.to_csv(path, index=False, encoding="utf-8")
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            if data and isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                csv.writer(f).writerows(data or [])

    def _save_json(self, data: Any, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_md(self, data: str, path: Path) -> None:
        if not isinstance(data, str):
            raise TypeError(f"Markdown output requires a str, got {type(data).__name__}.")
        path.write_text(data, encoding="utf-8")

