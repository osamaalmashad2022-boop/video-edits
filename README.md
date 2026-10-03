# Video Watermark Remover (Gemini Notebook Logo Remover) 🎬

أداة تلقائية لحذف الشعار/العلامة المائية (Watermark) لنوت بوك Gemini من مقاطع الفيديو عن طريق قص آخر 3.1 ثانية بدقة فائقة وبدون إعادة ترميز الفيديو (Stream Copy) للحفاظ على الجودة الأصلية وسرعة المعالجة الفائقة.

An automated tool to remove the Gemini Notebook watermark from videos by cleanly trimming the last 3.1 seconds using FFmpeg stream copy (no re-encoding, lossless quality, near-instant speed).

---

## 🌟 المميزات (Features)

- **واجهة ويب عصرية (Web Dashboard)**: رفع مقاطع الفيديو، سحب وإفلات (Drag & Drop)، متابعة التقدم بنسبة مئوية، ومعاينة وتحميل الفيديو بعد التعديل.
- **معالجة مجمعة (Batch Processing)**: دعم معالجة ملفات متعددة ومجلدات كاملة دفعة واحدة.
- **أداة سريعة عبر سطر الأوامر وملف باتش (CLI & Drag & Drop Batch)**: يمكنك سحب الفيديو أو المجلد مباشرة فوق ملف `Remove_Watermark.bat`.
- **بدون فقدان الجودة (Lossless / Fast)**: استخدام `-c copy` في FFmpeg لقص الثواني الأخيرة في أجزاء من الثانية دون استهلاك المعالج أو تقليل الجودة.

---

## 📋 المتطلبات (Prerequisites)

1. **Python 3.8+**
2. **FFmpeg & FFprobe**: يجب أن يكون مضافاً إلى مسار النظام (System PATH).
   - للتأكد من تثبيته، شغّل في موجه الأوامر:
     ```bash
     ffmpeg -version
     ffprobe -version
     ```

---

## 🚀 التثبيت والتشغيل (Installation & Usage)

### 1. تثبيت الاعتماديات (Dependencies)
```bash
pip install -r requirements.txt
```

### 2. تشغيل واجهة الويب (Web Interface)
```bash
python app.py
```
افتح المتصفح على الرابط:
[http://localhost:5000](http://localhost:5000)

### 3. استخدام سطر الأوامر / السحب والإفلات (Batch / CLI)
- **طريقة السحب والإفلات (ويندوز)**: اسحب أي ملف فيديو أو مجلد وأسقطه فوق ملف `Remove_Watermark.bat`.
- **سطر الأوامر**:
  ```bash
  python remove_watermark.py <مسار_الفيديو_أو_المجلد>
  ```
  سيتم حفظ الفيديوهات المعالجة في مجلد `output/`.

---

## 📂 هيكل المشروع (Project Structure)

```text
├── app.py                  # خادم واجهة الويب (Flask Web App)
├── remove_watermark.py     # سكربت سطر الأوامر (CLI Script)
├── Remove_Watermark.bat    # ملف تشغيل سريع بالسحب والإفلات (Windows Batch Launcher)
├── static/
│   └── index.html          # واجهة المستخدم الحديثة (Modern Web UI)
├── uploads/                # مجلد الرفع المؤقت
├── processed/              # مجلد المخرجات لواجهة الويب
├── requirements.txt        # مكتبات بايثون المطلوبة
└── .gitignore              # تجاهل ملفات الميديا والمجلدات المؤقتة
```

---

## 📄 الترخيص (License)
MIT License
