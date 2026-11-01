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
   * @param {Blob|File} file
   * @param {string} [filename]
   * @returns {Promise<void>}
   */
  async function saveSharedVideo(file, filename) {
    if (!file) return;
    const db = await openDB();
    return new Promise((resolve, reject) => {
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

      const putReq = store.put(record);
      putReq.onsuccess = () => resolve();
      putReq.onerror = () => reject(putReq.error);
      tx.oncomplete = () => db.close();
      tx.onerror = () => reject(tx.error);
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
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const getReq = store.get(RECORD_KEY);

        getReq.onsuccess = function () {
          resolve(getReq.result || null);
        };
        getReq.onerror = function () {
          reject(getReq.error);
        };
        tx.oncomplete = () => db.close();
        tx.onerror = () => reject(tx.error);
      });
    } catch (err) {
      console.warn('idb-store getSharedVideo error:', err);
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
        const delReq = store.delete(RECORD_KEY);

        delReq.onsuccess = () => resolve();
        delReq.onerror = () => reject(delReq.error);
        tx.oncomplete = () => db.close();
        tx.onerror = () => reject(tx.error);
      });
    } catch (err) {
      console.warn('idb-store clearSharedVideo error:', err);
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
