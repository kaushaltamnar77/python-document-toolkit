# 🛠️ File Utility Suite

An offline Python desktop GUI application built with **Tkinter** for fast, private PDF, Image, and DOCX processing. All operations run 100% locally with zero internet dependency.

## 📸 Screenshots

| PDF & Image Conversion | PDF Management & Compression |
| :---: | :---: |
| ![Conversion Tabs](screenshots/conversion_tabs.png) | ![PDF Tools](screenshots/pdf_tools.png) |

*(Add your screenshots inside a `screenshots/` folder in your repository.)*

## ✨ Features (8 Built-in Tools)

1. **PDF to Image:** Export PDF pages as high-res (`300 DPI`) **PNG** or **JPEG** files.
2. **Image to PDF:** Combine multiple **PNG/JPG/JPEG** images into a single PDF.
3. **Merge PDFs:** Sequentially merge multiple PDF files into one document.
4. **Image Reducer:** Batch-compress images with adjustable **JPEG quality (`1–100`)**, lossless PNG optimization, and a live progress bar.
5. **PDF Reducer:** Optimize PDF file size using PyMuPDF garbage collection & stream deflation with before/after size metrics.
6. **PDF Page Remover:** Delete specific pages or ranges (e.g., `1, 3-5, 8`) and export the remaining pages.
7. **PDF to DOCX:** Extract text content from PDFs into an editable `.docx` file.
8. **DOCX to PDF:** Interface tab with dependency guidance for external converters (LibreOffice / MS Word).

*Includes a bottom-docked **Activity Log** for real-time status updates and automatic dependency checks.*

## 🛠 Tech Stack

* **GUI:** Python 3, `tkinter` (`ttk`)
* **Libraries:** `PyMuPDF` (`fitz`), `Pillow` (`PIL`), `python-docx`

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/file-utility-suite.git
cd file-utility-suite
```

### 2. Install Dependencies
```bash
pip install pymupdf pillow python-docx
```
*(Linux users may also need `sudo apt-get install python3-tk`.)*

### 3. Run the App
```bash
python main.py
```

## ⚠️ Notes

* **PDF to DOCX** performs text-only extraction (complex layouts and images are not preserved).
* **DOCX to PDF** is a placeholder tab requiring external office rendering tools like LibreOffice.

## 👨‍💻 Developer

* **Kaushal Tamnar** — [GitHub](https://github.com/<your-username>)