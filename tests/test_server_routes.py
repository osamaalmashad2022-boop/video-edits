"""
Test server routes for PWA manifest, service worker, and Vercel configuration.
"""
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

from app import app


def test_flask_pwa_routes():
    client = app.test_client()

    # 1. Manifest endpoint
    resp_manifest = client.get("/manifest.json")
    assert resp_manifest.status_code == 200, f"/manifest.json returned {resp_manifest.status_code}"
    assert "json" in resp_manifest.content_type.lower()
    manifest_data = json.loads(resp_manifest.data)
    assert manifest_data.get("short_name") == "VideoTrimmer"

    # 2. Service Worker endpoint
    resp_sw = client.get("/sw.js")
    assert resp_sw.status_code == 200, f"/sw.js returned {resp_sw.status_code}"
    assert "javascript" in resp_sw.content_type.lower()
    assert resp_sw.headers.get("Service-Worker-Allowed") == "/", "Missing Service-Worker-Allowed: / header"
    assert b"share-target" in resp_sw.data


def test_vercel_config():
    vercel_path = WORKSPACE / "vercel.json"
    assert vercel_path.exists()
    config = json.loads(vercel_path.read_text(encoding="utf-8"))

    # Must NOT use legacy 'routes' together with cleanUrls or headers
    assert "routes" not in config, "vercel.json must not use legacy 'routes' with cleanUrls/headers"
    
    # Must use rewrites for PWA files
    rewrites = config.get("rewrites", [])
    has_sw_rewrite = any("sw.js" in r.get("source", "") for r in rewrites)
    has_manifest_rewrite = any("manifest.json" in r.get("source", "") for r in rewrites)

    assert has_sw_rewrite, "vercel.json missing rewrite for /sw.js"
    assert has_manifest_rewrite, "vercel.json missing rewrite for /manifest.json"


if __name__ == "__main__":
    test_flask_pwa_routes()
    test_vercel_config()
    print("PASS: test_flask_pwa_routes and test_vercel_config")
