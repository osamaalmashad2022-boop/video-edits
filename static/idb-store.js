/**
 * Video Trimmer - IndexedDB Storage Helper for Shared Videos
 * Works in both Window and ServiceWorker scopes.
 */
(function (global) {
  'use strict';

  const DB_NAME = 'VideoTrimmerDB';
  const DB_VERSION = 1;
  const STORE_NAME = 'shared_videos';
  const RECORD_KEY = 'latest_shared_video';

  function openDB() {
    return new Promise((resolve, reject) => {
      const indexedDB = global.indexedDB || global.webkitIndexedDB || global.mozIndexedDB;
      if (!indexedDB) {
        reject(new Error('IndexedDB is not supported in this environment.'));
        return;
      }

      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = function (event) {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        }
      };

      request.onsuccess = function (event) {
        resolve(event.target.result);
      };

      request.onerror = function (event) {
        reject(event.target.error || new Error('Failed to open IndexedDB.'));
      };
    });
  }

  /**
   * Save a shared video File/Blob to IndexedDB
   * Resolves only when transaction commits to disk (tx.oncomplete)
   * @param {Blob|File} file
   * @param {string} [filename]
   * @returns {Promise<void>}
   */
  async function saveSharedVideo(file, filename) {
    if (!file) return;
    const db = await openDB();
    return new Promise((resolve, reject) => {
      try {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);

        const record = {
          id: RECORD_KEY,
          file: file,
          name: filename || file.name || 'shared_video.mp4',
          type: file.type || 'video/mp4',
          size: file.size || 0,
          timestamp: Date.now()
        };

        store.put(record);

        tx.oncomplete = function () {
          try { db.close(); } catch {}
          resolve();
        };

        tx.onerror = function () {
          const err = tx.error || new Error('Transaction error while saving video');
          try { db.close(); } catch {}
          reject(err);
        };

        tx.onabort = function () {
          const err = tx.error || new Error('Transaction aborted (quota exceeded or canceled)');
          try { db.close(); } catch {}
          reject(err);
        };
      } catch (err) {
        try { db.close(); } catch {}
        reject(err);
      }
    });
  }

  /**
   * Get the latest shared video from IndexedDB
   * @returns {Promise<{file: Blob|File, name: string, type: string, size: number}|null>}
   */
  async function getSharedVideo() {
    try {
      const db = await openDB();
      return new Promise((resolve, reject) => {
        let result = null;
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const getReq = store.get(RECORD_KEY);

        getReq.onsuccess = function () {
          result = getReq.result || null;
        };

        tx.oncomplete = function () {
          try { db.close(); } catch {}
          resolve(result);
        };

        tx.onerror = function () {
          try { db.close(); } catch {}
          reject(tx.error || new Error('Failed to retrieve video record'));
        };
      });
    } catch (err) {
      console.warn('[idb-store] getSharedVideo error:', err);
      return null;
    }
  }

  /**
   * Clear shared video record from IndexedDB
   * @returns {Promise<void>}
   */
  async function clearSharedVideo() {
    try {
      const db = await openDB();
      return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.delete(RECORD_KEY);

        tx.oncomplete = function () {
          try { db.close(); } catch {}
          resolve();
        };

        tx.onerror = function () {
          try { db.close(); } catch {}
          reject(tx.error);
        };
      });
    } catch (err) {
      console.warn('[idb-store] clearSharedVideo error:', err);
    }
  }

  const api = {
    openDB,
    saveSharedVideo,
    getSharedVideo,
    clearSharedVideo
  };

  // Expose to global scope
  global.idbStore = api;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof self !== 'undefined' ? self : this);
