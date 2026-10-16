# PDF Image Toolkit

A Python-based desktop application for managing PDF documents and images with a simple graphical user interface (GUI). Convert files, merge PDFs, compress images, remove PDF pages, and extract PDF text into Word documents.

## Features

- **PDF to Images:** Convert PDF pages into PNG or JPEG images.
- **Images to PDF:** Combine multiple PNG or JPEG images into a single PDF.
- **Merge PDFs:** Merge two or more PDF files into one document.
- **Image Compression:** Reduce JPEG image quality or optimize PNG images.
- **PDF Compression:** Optimize PDF files to reduce their size where possible.
- **Remove PDF Pages:** Remove specific pages or page ranges from a PDF.
- **PDF to DOCX:** Extract PDF text into a Microsoft Word document.
- **DOCX to PDF:** Includes a placeholder interface for future implementation using external conversion software.

## Technologies Used

- Python
- Tkinter — graphical user interface
- PyMuPDF — PDF processing
- Pillow (PIL) — image processing
- python-docx — Word document generation

## Requirements

- Python 3.9 or later recommended
- pip package manager
- Windows, macOS, or Linux with a graphical desktop environment

## Installation

**1. Clone the repository**

```bash
https://github.com/kaushaltamnar77/python-document-toolkit.git
```



**2. Install dependencies**

```bash
pip install PyMuPDF Pillow python-docx
```

**3. Run the application**

Save the Python source code as `main.py`, then run:

```bash
python main.py
```

The File Utility Suite window will open with separate tabs for the available tools.



## How to Use

1. Launch the application.
2. Select the required operation from the tabs.
3. Browse and select your input files.
4. Choose the output folder or destination filename when prompted.
5. Check the Activity Log for processing messages and errors.

## Important Notes

- PDF-to-DOCX conversion extracts text only; images, complex tables, and original layouts are not preserved.
- PDF compression does not guarantee a smaller output file.
- Image compression supports JPEG quality adjustment and PNG optimization.
- DOCX-to-PDF conversion is not implemented in the current version. External software, such as LibreOffice, can be integrated in a future version.
- Keep backups of original files before processing important documents.

## Future Improvements

- Implement DOCX-to-PDF conversion.
- Add drag-and-drop file selection.
- Improve error handling and input validation.
- Add a modernized interface and dark mode.
- Package the application as a standalone executable.
- Display detailed before-and-after file size statistics.

## Contributing

Contributions, bug reports, and feature suggestions are welcome. Fork the repository, create a feature branch, and submit a pull request.



**Developed with Python.**



**SCREENSHORT**

<img width="1366" height="719" alt="tool kitw" src="https://github.com/user-attachments/assets/87cf6219-0b8d-4bd6-b4de-86c8592f8aa3" />
