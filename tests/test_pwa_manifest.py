"""
Test PWA Manifest and Icons specification conformance.
"""
import json
import os
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
STATIC_DIR = WORKSPACE / "static"
MANIFEST_PATH = STATIC_DIR / "manifest.json"


def test_manifest_exists_and_valid():
    assert MANIFEST_PATH.exists(), f"manifest.json not found at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Core PWA properties
    assert "name" in data and len(data["name"]) > 0
    assert "short_name" in data and len(data["short_name"]) > 0
    assert data.get("display") == "standalone"
    assert data.get("start_url") in ("/", "./", "index.html")
    assert "theme_color" in data
    assert "background_color" in data

    # Icons validation
    icons = data.get("icons", [])
    assert len(icons) >= 2, "Manifest should define at least 192 and 512 icons"

    sizes = [icon.get("sizes") for icon in icons]
    assert "192x192" in sizes, "Missing 192x192 icon"
    assert "512x512" in sizes, "Missing 512x512 icon"

    for icon in icons:
        src = icon.get("src", "").lstrip("/")
        # If relative or absolute static path
        if src.startswith("static/"):
            icon_file = WORKSPACE / src
        else:
            icon_file = STATIC_DIR / src
        assert icon_file.exists(), f"Referenced icon file does not exist: {icon_file}"
        assert icon_file.stat().st_size > 0, f"Icon file is empty: {icon_file}"

    # Web Share Target validation
    assert "share_target" in data, "Missing share_target in manifest.json"
    st = data["share_target"]
    assert st.get("action") == "/share-target" or st.get("action") == "share-target"
    assert st.get("method", "").upper() == "POST"
    assert st.get("enctype") == "multipart/form-data"

    params = st.get("params", {})
    files = params.get("files", [])
    assert len(files) > 0, "share_target must accept files"
    video_file_spec = next((f for f in files if f.get("name") == "video"), None)
    assert video_file_spec is not None, "share_target files must include a param named 'video'"
    accepts = video_file_spec.get("accept", [])
    assert any("video" in a for a in accepts), "share_target must accept video/* files"


if __name__ == "__main__":
    test_manifest_exists_and_valid()
    print("PASS: test_manifest_exists_and_valid")
