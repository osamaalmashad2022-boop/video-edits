# PWA & Web Share Target Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the video watermark remover web tool into an installable Progressive Web App (PWA) on Android that receives shared videos from any app via the Android system Share sheet and automatically processes them client-side.

**Architecture:** Client-side PWA architecture utilizing a Web App Manifest (`manifest.json`) with `share_target`, a Service Worker (`sw.js`) that intercepts shared multipart video payloads, an IndexedDB bridge for temporary video Blob transport, and seamless automatic queueing inside the existing `index.html` FFmpeg WebAssembly engine.

**Tech Stack:** HTML5, Modern Vanilla JavaScript, Service Workers (Cache API, Fetch interceptor), IndexedDB API, Web App Manifest, Web Share Target API, Python (Flask), Vercel configuration.

**Spec:** [docs/superpowers/specs/2026-11-02-pwa-share-target-design.md](file:///c:/Users/Osama/Desktop/تعديل%20الفيديو%20أوتوماتيك/docs/superpowers/specs/2026-11-02-pwa-share-target-design.md)

## Global Constraints
- Target platform: Android (Chrome/Edge/Samsung Internet) and modern desktop/mobile browsers.
- Video processing must remain 100% client-side via WebAssembly; no video upload to any server for PWA share target.
- Service Worker must have root scope (`/`) with `Service-Worker-Allowed: /` header.
- High-res PWA icons must be generated and properly referenced in 192x192, 512x512, and maskable formats.
- Offline support for core UI assets via Service Worker cache.

## Review Focus
1. User shares a 150MB+ video file from gallery: ensure IndexedDB does not exceed quota or crash the browser; handle quota errors cleanly.
2. User shares a video while app is completely closed: ensure Android launches PWA, SW intercepts POST, saves to IndexedDB, redirects to `/?shared=1`, and UI loads the file into the queue without dropping it.
3. User navigates directly to `/?shared=1` when no file exists in IndexedDB: UI must handle empty store gracefully without false error cards.
4. User clicks "Install App" prompt: beforeinstallprompt event handled cleanly, install banner vanishes upon successful installation.
5. Service Worker caching must not cache heavy dynamic video blobs or stale HTML updates.

---

### Task 1: Generate High-Resolution App Icons & Web App Manifest

**Files:**
- Create: `static/icons/icon-192.png`
- Create: `static/icons/icon-512.png`
- Create: `static/icons/icon-maskable-512.png`
- Create: `static/icons/icon.svg`
- Create: `static/manifest.json`
- Test: `tests/test_pwa_manifest.py`

**Interfaces:**
- Consumes: None
- Produces: `static/manifest.json` specifying app name, theme color `#6c5ce7`, standalone display, icons, and `share_target` pointing to `/share-target` with `params.files[0].name = "video"` and `accept = ["video/*"]`.

- [ ] **Step 1: Write test for manifest schema and icon existence**
Create `tests/test_pwa_manifest.py` validating that `static/manifest.json` is valid JSON, contains `share_target` with expected structure, and references existing icon files.

- [ ] **Step 2: Run test to verify it fails**
Run: `python tests/test_pwa_manifest.py`
Expected: FAIL (files do not exist yet).

- [ ] **Step 3: Create SVG and generate crisp PNG app icons in `static/icons/`**
Generate modern, visually striking icons representing video cutting/scissors with purple/neon accents in 192x192 and 512x512 formats.

- [ ] **Step 4: Create `static/manifest.json`**
Configure name, short_name, description, theme_color, background_color, icons array, and `share_target` configuration.

- [ ] **Step 5: Run test to verify it passes**
Run: `python tests/test_pwa_manifest.py`
Expected: PASS.

- [ ] **Step 6: Commit**
`git add static/icons/ static/manifest.json tests/test_pwa_manifest.py`
`git commit -m "feat(pwa): add app icons and manifest with share_target"`

---

### Task 2: Implement IndexedDB Video Store & Service Worker (`sw.js`)

**Files:**
- Create: `static/idb-store.js`
- Create: `static/sw.js`
- Test: `tests/test_sw_syntax.py`

**Interfaces:**
- Consumes: `static/manifest.json` `share_target` action `/share-target`
- Produces: 
  - `idb-store.js`: `saveSharedVideo(file: File|Blob, name: string): Promise<void>`, `getSharedVideo(): Promise<{file: Blob, name: string}|null>`, `clearSharedVideo(): Promise<void>`.
  - `sw.js`: Service worker with install, activate, fetch cache strategy, and POST `/share-target` interception saving video to IndexedDB and redirecting to `/?shared=1`.

- [ ] **Step 1: Write syntax and structure validation test for `sw.js` and `idb-store.js`**
Create `tests/test_sw_syntax.py` to verify that `sw.js` includes fetch listener, share-target interception logic, and `idb-store.js` exports required functions.

- [ ] **Step 2: Run test to verify it fails**
Run: `python tests/test_sw_syntax.py`
Expected: FAIL.

- [ ] **Step 3: Implement `static/idb-store.js`**
Provide a standalone, promise-based IndexedDB utility (`video-trimmer-store`) that can be imported or included both in the Service Worker and the client window.

- [ ] **Step 4: Implement `static/sw.js`**
Handle:
1. `install` event: cache essential app shell assets (`/`, `/static/index.html`, `/static/idb-store.js`, icons, vendor scripts).
2. `activate` event: delete older cache versions and claim clients.
3. `fetch` event:
   - If POST to `/share-target`: parse `formData()`, extract file, store in IndexedDB via `saveSharedVideo`, and respond with `Response.redirect('/?shared=1', 303)`.
   - Normal GET requests: Cache-first / Network-fallback strategy for static assets.

- [ ] **Step 5: Run test to verify it passes**
Run: `python tests/test_sw_syntax.py`
Expected: PASS.

- [ ] **Step 6: Commit**
`git add static/idb-store.js static/sw.js tests/test_sw_syntax.py`
`git commit -m "feat(pwa): implement idb-store and service worker with share-target"`

---

### Task 3: Update `app.py` and `vercel.json` for PWA Serving & Routing

**Files:**
- Modify: `app.py`
- Modify: `vercel.json`
- Test: `tests/test_server_routes.py`

**Interfaces:**
- Consumes: `static/manifest.json`, `static/sw.js`
- Produces: 
  - Root routes for `/manifest.json` and `/sw.js` with `Service-Worker-Allowed: /` header.
  - Vercel rewrites and COOP/COEP headers.

- [ ] **Step 1: Write test for server endpoints**
Create `tests/test_server_routes.py` testing that `GET /manifest.json` returns application/manifest+json and `GET /sw.js` returns application/javascript with header `Service-Worker-Allowed: /`.

- [ ] **Step 2: Run test to verify it fails**
Run: `python tests/test_server_routes.py`
Expected: FAIL (404 on /sw.js and /manifest.json).

- [ ] **Step 3: Add routes in `app.py`**
Serve `manifest.json` and `sw.js` directly from root with correct content types and `Service-Worker-Allowed: /`.

- [ ] **Step 4: Update `vercel.json`**
Configure clean routes for `/sw.js`, `/manifest.json`, and static caching headers.

- [ ] **Step 5: Run test to verify it passes**
Run: `python tests/test_server_routes.py`
Expected: PASS.

- [ ] **Step 6: Commit**
`git add app.py vercel.json tests/test_server_routes.py`
`git commit -m "feat(server): serve manifest and service worker with correct PWA headers"`

---

### Task 4: Integrate PWA Lifecycle, Share Detection, and Install UI in `static/index.html`

**Files:**
- Modify: `static/index.html`
- Modify: `index.html` (sync root copy with static/index.html)
- Test: `tests/test_ui_pwa_integration.py`

**Interfaces:**
- Consumes: `idb-store.js`, `manifest.json`, `sw.js`
- Produces: 
  - Manifest link and meta tags in `<head>`.
  - Service worker registration on window load.
  - Automatic detection of `?shared=1` parameter: loads file from IndexedDB, displays incoming notification, calls `enqueueFile(file)`, cleans up IndexedDB and URL query.
  - Floating / Header "تثبيت التطبيق (Install)" button wired to `beforeinstallprompt`.

- [ ] **Step 1: Write verification test for PWA tags and hooks in `static/index.html`**
Create `tests/test_ui_pwa_integration.py` asserting presence of manifest link, apple-touch-icon, theme-color, script inclusion for `idb-store.js`, and `beforeinstallprompt` handler.

- [ ] **Step 2: Run test to verify it fails**
Run: `python tests/test_ui_pwa_integration.py`
Expected: FAIL.

- [ ] **Step 3: Update `static/index.html`**
1. Add `<head>` tags: `<link rel="manifest" href="/manifest.json">`, theme-color, apple-mobile-web-app tags.
2. Include `<script src="/static/idb-store.js"></script>`.
3. Add "تثبيت التطبيق / Install App" button in navbar/header (hidden by default).
4. Add Service Worker registration and `beforeinstallprompt` event listener to show the install button and trigger prompt on click.
5. In initialization, check `if (window.location.search.includes('shared=1'))`: retrieve video from `idbStore.getSharedVideo()`, call `enqueueFile(videoFile)`, clear store with `idbStore.clearSharedVideo()`, and clean URL with `history.replaceState`.
6. Synchronize root `index.html` with `static/index.html`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python tests/test_ui_pwa_integration.py`
Expected: PASS.

- [ ] **Step 5: Commit**
`git add static/index.html index.html tests/test_ui_pwa_integration.py`
`git commit -m "feat(ui): connect pwa lifecycle, install prompt and incoming shared video handler"`

---

### Task 5: End-to-End Verification & User Documentation

**Files:**
- Modify: `README.md`
- Create: `tests/test_e2e_pwa_flow.py`

**Interfaces:**
- Consumes: All components from Tasks 1-4.
- Produces: Validated full pipeline and clear instructions in Arabic and English in `README.md` detailing how to deploy to Vercel, install on Android, and share videos from other apps.

- [ ] **Step 1: Write and run end-to-end integration test**
Create `tests/test_e2e_pwa_flow.py` simulating manifest retrieval, SW response, and verification of all PWA assets.
Run: `python tests/test_e2e_pwa_flow.py`
Expected: PASS.

- [ ] **Step 2: Update `README.md` with PWA Installation & Sharing Guide**
Document step-by-step instructions:
1. Deploying to Vercel (or running via local HTTPS).
2. Opening in Android Chrome and tapping "تثبيت التطبيق" (Install).
3. Sharing any video from Gallery/TikTok/WhatsApp to the app.

- [ ] **Step 3: Commit and verify git status**
`git add README.md tests/test_e2e_pwa_flow.py`
`git commit -m "docs: add PWA mobile installation and share target usage guide"`

