"""
Test Service Worker and IDB Store syntax and implementation contracts.
"""
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
STATIC_DIR = WORKSPACE / "static"
IDB_STORE_PATH = STATIC_DIR / "idb-store.js"
SW_PATH = STATIC_DIR / "sw.js"


def test_idb_store():
    assert IDB_STORE_PATH.exists(), f"idb-store.js not found at {IDB_STORE_PATH}"
    content = IDB_STORE_PATH.read_text(encoding="utf-8")
    
    # Check syntax with node -c
    res = subprocess.run(["node", "-c", str(IDB_STORE_PATH)], capture_output=True, text=True)
    assert res.returncode == 0, f"idb-store.js syntax error: {res.stderr}"

    # Required API methods
    assert "saveSharedVideo" in content, "Missing saveSharedVideo in idb-store.js"
    assert "getSharedVideo" in content, "Missing getSharedVideo in idb-store.js"
    assert "clearSharedVideo" in content, "Missing clearSharedVideo in idb-store.js"
    assert "indexedDB" in content or "open" in content


def test_sw():
    assert SW_PATH.exists(), f"sw.js not found at {SW_PATH}"
    content = SW_PATH.read_text(encoding="utf-8")

    # Check syntax with node -c
    res = subprocess.run(["node", "-c", str(SW_PATH)], capture_output=True, text=True)
    assert res.returncode == 0, f"sw.js syntax error: {res.stderr}"

    # Lifecycle events
    assert "addEventListener('install'" in content or 'addEventListener("install"' in content
    assert "addEventListener('activate'" in content or 'addEventListener("activate"' in content
    assert "addEventListener('fetch'" in content or 'addEventListener("fetch"' in content

    # Share target interception
    assert "share-target" in content, "sw.js must intercept share-target"
    assert "POST" in content, "sw.js must handle POST method for share_target"
    assert "formData" in content, "sw.js must parse formData to extract shared file"
    assert "Response.redirect" in content, "sw.js must redirect after handling share-target"


if __name__ == "__main__":
    test_idb_store()
    test_sw()
    print("PASS: test_idb_store and test_sw")
