"""
Test PWA Lifecycle, Meta Tags, and Share Target Integration in index.html.
"""
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
STATIC_INDEX = WORKSPACE / "static" / "index.html"
ROOT_INDEX = WORKSPACE / "index.html"


def test_ui_pwa_integration():
    assert STATIC_INDEX.exists()
    content = STATIC_INDEX.read_text(encoding="utf-8")

    # 1. PWA Manifest and mobile meta tags
    assert 'rel="manifest"' in content, "Missing manifest link in static/index.html"
    assert 'name="theme-color"' in content, "Missing theme-color meta tag"
    assert 'rel="apple-touch-icon"' in content, "Missing apple-touch-icon link"
    assert 'apple-mobile-web-app-capable' in content, "Missing apple-mobile-web-app-capable"

    # 2. idb-store script
    assert "idb-store.js" in content, "Missing script tag for idb-store.js"

    # 3. Service Worker registration
    assert "navigator.serviceWorker.register" in content, "Missing SW registration"

    # 4. Share handling logic
    assert "getSharedVideo" in content, "Missing call to idbStore.getSharedVideo"
    assert "clearSharedVideo" in content, "Missing call to idbStore.clearSharedVideo"
    assert "shared=1" in content or "shared" in content, "Missing check for shared URL param"

    # 5. Install App button / prompt
    assert "beforeinstallprompt" in content, "Missing beforeinstallprompt listener"
    assert "pwa-install" in content or "install-btn" in content, "Missing install button"

    # 6. Ensure root index.html is synced with static/index.html
    root_content = ROOT_INDEX.read_text(encoding="utf-8")
    assert 'rel="manifest"' in root_content, "Root index.html not updated with PWA manifest"
    assert "idb-store.js" in root_content, "Root index.html missing idb-store.js"


if __name__ == "__main__":
    test_ui_pwa_integration()
    print("PASS: test_ui_pwa_integration")

