"""Read-only preflight. Never print configuration values or change credentials."""
import argparse
import json
from pathlib import Path


def inspect(config, plugin):
    server = plugin.get("mcpServers", {}).get("hi", {})
    headers = server.get("http_headers", {})
    plugin_ready = (
        server.get("url") == "https://mcp.hirey.ai/mcp"
        and headers.get("x-hirey-plugin-host") == "codex"
        and bool(headers.get("x-hirey-plugin-version"))
    )
    manual = config.get("mcp_servers", {}).get("hi")
    if manual is None:
        return {"status": "plugin_only" if plugin_ready else "plugin_config_incomplete"}
    if not isinstance(manual, dict):
        return {"status": "review_required"}
    if plugin_ready and manual == {"url": "https://mcp.hirey.ai/mcp"}:
        return {"status": "legacy_url_only_override", "repair_command": "codex mcp remove hi",
                "logout_required": False}
    # Custom URLs, auth, tool restrictions, disabled entries and timeouts are user choices.
    return {"status": "review_required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--plugin-mcp", required=True)
    args = parser.parse_args()
    try:
        import tomllib
        path = Path(args.config)
        config = tomllib.loads(path.read_text()) if path.exists() else {}
        plugin = json.loads(Path(args.plugin_mcp).read_text())
        print(json.dumps(inspect(config, plugin)))
    except Exception:
        # Parser errors can include secrets from malformed config; never echo them.
        print(json.dumps({"status": "inspection_failed", "requires": "Python 3.11+ and valid TOML/JSON"}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
