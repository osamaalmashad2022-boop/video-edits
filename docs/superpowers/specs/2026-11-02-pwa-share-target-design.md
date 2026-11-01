# PWA and Web Share Target for Video Watermark Remover

## Intent & Why
Enable users to install the video watermark remover web app onto their mobile devices (specifically Android) as a Progressive Web App (PWA) that registers with the system Share menu (`ACTION_SEND` / `Web Share Target`). When a user shares a video from any app on their device (Gallery, Files, TikTok, WhatsApp, etc.), the PWA opens, receives the shared video, queues it, and trims the watermark (last 3.1 seconds) using client-side FFmpeg WebAssembly.

## Goals
- Provide a PWA `manifest.json` with high-res responsive app icons, standalone display mode, and `share_target` configuration for `video/*`.
- Implement a Service Worker (`sw.js`) that intercepts the `share_target` POST requests, extracts the video file, stores it into `IndexedDB` (`shared-videos`), and redirects the user to the app root (`/?shared=1`).
- Update `static/index.html` to:
  - Register `sw.js` and link `manifest.json`.
  - Check for incoming shared videos in `IndexedDB` on launch, and enqueue them into the processing pipeline (`enqueueFile`).
  - Provide an "Install App" button / prompt banner for smooth one-tap installation on Android.
- Provide responsive vector/PNG app icons in `static/icons/`.
- Update `vercel.json` and `app.py` to correctly serve `sw.js` and `manifest.json` with proper MIME types and Service-Worker-Allowed headers.
- Update `README.md` with instructions on installing as PWA and using the Share Target on Android.

## Non-Goals
- Native Android APK compilation via Android Studio or Google Play deployment (PWA is lighter and update-free).
- Server-side video upload for PWA share target (all processing remains client-side in the browser via FFmpeg WASM for privacy, zero bandwidth cost, and speed).

## Constraints
- Web Share Target with file payload requires HTTPS in production (e.g. Vercel) and Chrome/Edge on Android.
- Service worker scope must encompass the root `/`.
- IndexedDB storage must handle large video Blobs gracefully and clean up entries immediately after enqueueing.

