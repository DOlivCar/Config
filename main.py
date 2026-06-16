from pathlib import Path
from src.config import ConfigLoader, CONFIG_DIR


# ----------------------------------------------------------------------
# Sample data for save demo
# ----------------------------------------------------------------------

SAMPLE_DATA = {
    "csv": [
        {"name": "Alice", "role": "Engineer", "score": 92},
        {"name": "Bob",   "role": "Analyst",  "score": 85},
        {"name": "Carol", "role": "Designer",  "score": 88},
    ],
    "json": {
        "project": "Config_DSAA",
        "version": "1.0.0",
        "settings": {
            "debug": True,
            "max_retries": 3,
            "timeout": 30,
        },
    },
    "md": """\
    # Config_DSAA Report

    ## Summary
    This report was generated automatically by the save demo script.

    ## Results
    - All config files loaded successfully.
    - Outputs saved in CSV, JSON, and Markdown formats.

    ## Notes
    Adjust `save_paths` in your config to control where each format is written.
    """,
    }

# ----------------------------------------------------------------------
# Display
# ----------------------------------------------------------------------

def display_attributes(loader: ConfigLoader) -> None:
    """Print all config attributes loaded onto the ConfigLoader instance."""
    attrs = {
        key: value
        for key, value in vars(loader).items()
        if not key.startswith("_")
    }

    print("\n" + "=" * 50)
    print(f"  Config loaded from: {loader.config_dir}")
    print(f"  Total attributes:   {len(attrs)}")
    print("=" * 50)

    for key, value in attrs.items():
        print(f"\n  {key}:")
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"    {k}: {v}")
        elif isinstance(value, list):
            for item in value:
                print(f"    - {item}")
        else:
            print(f"    {value}")

    print("\n" + "=" * 50)


# ----------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------

def save_all(loader: ConfigLoader) -> None:
    """Save one example file per supported output format."""
    outputs = [
        ("csv",  "sample_data",   SAMPLE_DATA["csv"]),
        ("json", "sample_config", SAMPLE_DATA["json"]),
        ("md",   "sample_report", SAMPLE_DATA["md"]),
    ]

    print("\n" + "=" * 50)
    print("  Saving outputs")
    print("=" * 50)

    for fmt, filename, data in outputs:
        try:
            path = loader.save(data, filename, fmt)
            print(f"  [{fmt.upper():4}]  saved → {path}")
        except (KeyError, TypeError) as e:
            print(f"  [{fmt.upper():4}]  failed — {e}")

    print("=" * 50)


# ----------------------------------------------------------------------
# Multiple files demo
# ----------------------------------------------------------------------

def demo_multiple_files(loader: ConfigLoader) -> None:
    """Show attributes sourced from multiple files of the same format."""
    print("\n" + "=" * 50)
    print("  Multiple config files — use case")
    print("=" * 50)

    # Attributes from exemplo.env
    print("\n  [exemplo.env]")
    print(f"    APP_NAME : {loader.get('APP_NAME')}")
    print(f"    API_KEY  : {loader.get('API_KEY')}")

    # Attributes from database.env (loaded alongside exemplo.env)
    print("\n  [database.env]")
    print(f"    DB_HOST  : {loader.get('DB_HOST')}")
    print(f"    DB_PORT  : {loader.get('DB_PORT')}")
    print(f"    DB_NAME  : {loader.get('DB_NAME')}")

    # Attributes from config_exemplo.json
    print("\n  [config_exemplo.json]")
    print(f"    input_paths : {loader.get('input_paths')}")

    # Attributes from database.json (loaded alongside config_exemplo.json)
    print("\n  [database.json]")
    print(f"    db_settings : {loader.get('db_settings')}")

    print("\n" + "=" * 50)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    loader = ConfigLoader(CONFIG_DIR)
    display_attributes(loader)
    demo_multiple_files(loader)
    save_all(loader)