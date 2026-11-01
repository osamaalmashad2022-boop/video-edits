"""
End-to-End verification test suite for PWA and Web Share Target features.
"""
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

from app import app


def test_full_pwa_stack():
    print("Testing PWA manifest and icons...")
    manifest_file = WORKSPACE / "static" / "manifest.json"
    assert manifest_file.exists()
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_data["share_target"]["action"] == "/share-target"

    for icon in manifest_data["icons"]:
        src = icon["src"].lstrip("/")
        icon_path = WORKSPACE / src if src.startswith("static/") else WORKSPACE / "static" / src
        assert icon_path.exists()
        assert icon_path.stat().st_size > 0

    print("Testing Service Worker and JS Store syntax...")
    sw_file = WORKSPACE / "static" / "sw.js"
    idb_file = WORKSPACE / "static" / "idb-store.js"
    assert subprocess.run(["node", "-c", str(sw_file)]).returncode == 0
    assert subprocess.run(["node", "-c", str(idb_file)]).returncode == 0

    print("Testing Flask app PWA endpoints...")
    client = app.test_client()

    # Index page
    r_index = client.get("/")
    assert r_index.status_code == 200
    assert b"manifest.json" in r_index.data
    assert b"idb-store.js" in r_index.data
    assert b"pwa-install-banner" in r_index.data

    # Manifest
    r_manifest = client.get("/manifest.json")
    assert r_manifest.status_code == 200
    assert "json" in r_manifest.content_type.lower()

    # Service Worker
    r_sw = client.get("/sw.js")
    assert r_sw.status_code == 200
    assert r_sw.headers.get("Service-Worker-Allowed") == "/"

    # Share target fallback redirect
    r_share = client.post("/share-target")
    assert r_share.status_code in (302, 303)

    print("Testing Vercel deployment configuration...")
    vercel_file = WORKSPACE / "vercel.json"
    assert vercel_file.exists()
    vercel_data = json.loads(vercel_file.read_text(encoding="utf-8"))
    assert "routes" not in vercel_data
    assert any("sw.js" in r.get("source", "") for r in vercel_data.get("rewrites", []))
    assert any("manifest.json" in r.get("source", "") for r in vercel_data.get("rewrites", []))

    print("ALL END-TO-END CHECKS PASSED SUCCESSFULLY.")


if __name__ == "__main__":
    test_full_pwa_stack()

