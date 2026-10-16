import tkinter as tk
from tkinter import filedialog, ttk, messagebox
# PyMuPDF must be installed as 'fitz' for the import
import fitz 
from PIL import Image
import os

# --- Attempt to import DOCX library, needed for new features ---
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    # This error is handled gracefully in the app, but installation is required for features 7 & 8
    DOCX_AVAILABLE = False
    
# Helper function for size formatting
def format_size(size_bytes):
    """Convert bytes to a human-readable format (MB or KB)."""
    if size_bytes >= (1024 * 1024):
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} Bytes"

# --- Core Utility Logic ---

class FileProcessor:
    def __init__(self, logger_callback):
        """Initializes the FileProcessor with a callback function for logging messages."""
        self.log = logger_callback

    # [1] PDF to Image
    def pdf_to_images(self, pdf_path, output_dir, img_format):
        """Converts a PDF to a series of images (PNG or JPEG)."""
        self.log(f"Starting PDF to {img_format.upper()} conversion...")
        try:
            doc = fitz.open(pdf_path)
            base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Set a high resolution (300 DPI) for quality export
                zoom = 3
                matrix = fitz.Matrix(zoom, zoom)
                
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                
                output_filename = f"{base_filename}_page{page_num+1}.{img_format.lower()}"
                output_filepath = os.path.join(output_dir, output_filename)
                
                pix.save(output_filepath)
                self.log(f"Saved: {output_filename}")
            
            doc.close()
            self.log("PDF to Image conversion successful!")
            return True

        except Exception as e:
            self.log(f"ERROR during PDF to Image conversion: {e}")
            return False

    # [2] Images to PDF
    def images_to_pdf(self, image_paths, output_pdf_path):
        """Converts multiple images into a single PDF."""
        self.log("Starting Images to PDF conversion...")
        if not image_paths:
            self.log("ERROR: No images selected.")
            return False
            
        try:
            img_list = [Image.open(path) for path in image_paths]
            first_image = img_list[0].convert('RGB')
            other_images = [img.convert('RGB') for img in img_list[1:]]
            
            first_image.save(
                output_pdf_path, 
                "PDF", 
                resolution=100.0, 
                save_all=True, 
                append_images=other_images
            )
            
            self.log(f"Images successfully converted to PDF: {os.path.basename(output_pdf_path)}")
            return True
            
        except Exception as e:
            self.log(f"ERROR during Images to PDF conversion: {e}")
            return False

    # [3] Merge PDFs
    def merge_pdfs(self, pdf_paths, output_pdf_path):
        """Merges multiple PDF files into one."""
        self.log("Starting PDF Merge operation...")
        if len(pdf_paths) < 2:
            self.log("ERROR: Select at least two PDF files to merge.")
            return False

        try:
            merged_doc = fitz.open()
            for path in pdf_paths:
                doc = fitz.open(path)
                merged_doc.insert_pdf(doc)
                doc.close()
                self.log(f"Appended: {os.path.basename(path)}")

            merged_doc.save(output_pdf_path)
            merged_doc.close()
            self.log(f"PDFs successfully merged into: {os.path.basename(output_pdf_path)}")
            return True

        except Exception as e:
            self.log(f"ERROR during PDF Merge: {e}")
            return False
            
    # [4] Reduce Image Size
    def reduce_image_size(self, image_paths, output_dir, quality=85, progress_callback=None):
        """Reduces the size of selected images."""
        self.log(f"Starting Image Size Reduction for {len(image_paths)} files...")
        success_count = 0
        total_files = len(image_paths)
        
        try:
            for i, path in enumerate(image_paths):
                img = Image.open(path)
                base, ext = os.path.splitext(os.path.basename(path))
                output_filepath = os.path.join(output_dir, f"{base}_reduced{ext}")
                original_size = os.path.getsize(path)
                
                if ext.lower() in ['.jpeg', '.jpg']:
                    # JPEG quality reduction
                    img.save(output_filepath, img.format, quality=quality)
                elif ext.lower() == '.png':
                    # PNG lossless optimization
                    img.save(output_filepath, optimize=True)
                else:
                    self.log(f"Skipping {os.path.basename(path)}: Format not supported for compression.")
                    continue

                reduced_size = os.path.getsize(output_filepath)
                reduction_percent = 100 * (original_size - reduced_size) / original_size
                
                self.log(f"--- Processed {i + 1}/{total_files}: {os.path.basename(path)} ({reduction_percent:.1f}% reduction)")
                
                if progress_callback:
                    progress_callback((i + 1) / total_files * 100)
                    
                success_count += 1
            
            self.log(f"Image reduction complete. {success_count}/{total_files} files processed.")
            return True

        except Exception as e:
            self.log(f"ERROR during Image Size Reduction: {e}")
            if progress_callback:
                 progress_callback(100)
            return False

    # [5] Reduce PDF Size
    def reduce_pdf_size(self, pdf_path, output_pdf_path, progress_callback=None):
        """Attempts to reduce the size of a PDF."""
        self.log("Starting PDF Size Reduction...")
        
        try:
            original_size = os.path.getsize(pdf_path)
            doc = fitz.open(pdf_path)
            
            # Use maximal cleanup and compression
            doc.save(
                output_pdf_path,
                garbage=4,
                deflate=True
            )
            
            doc.close()
            
            reduced_size = os.path.getsize(output_pdf_path)
            reduction_percent = 100 * (original_size - reduced_size) / original_size
            
            self.log(f"PDF reduction successful. Saved to {os.path.basename(output_pdf_path)}")
            self.log(f"    Original Size: {format_size(original_size)}")
            self.log(f"    Reduced Size:  {format_size(reduced_size)}")
            self.log(f"    Reduction:     {reduction_percent:.1f}%")
            
            if progress_callback:
                progress_callback(100)

            return True
            
        except Exception as e:
            self.log(f"ERROR during PDF Size Reduction: {e}")
            if progress_callback:
                progress_callback(100)
            return False

    # [6] Remove PDF Pages
    def remove_pdf_pages(self, pdf_path, pages_to_keep_0_based, output_pdf_path):
        """Creates a new PDF containing only the specified pages (0-based indices)."""
        self.log("Starting PDF Page Removal...")
        
        if not pages_to_keep_0_based:
            self.log("WARNING: No pages remaining after filtering. Creating an empty PDF.")

        try:
            doc = fitz.open(pdf_path)
            output_doc = fitz.open()

            kept_pages_count = 0
            for page_num_0_based in pages_to_keep_0_based:
                if 0 <= page_num_0_based < len(doc):
                    output_doc.insert_pdf(doc, from_page=page_num_0_based, to_page=page_num_0_based)
                    kept_pages_count += 1
            
            output_doc.save(output_pdf_path)
            output_doc.close()
            doc.close()
            
            self.log(f"PDF pages successfully filtered. Kept {kept_pages_count} pages.")
            self.log(f"New file saved as: {os.path.basename(output_pdf_path)}")
            return True

        except Exception as e:
            self.log(f"ERROR during PDF Page Removal: {e}")
            return False

    # [7] PDF to DOCX
    def pdf_to_docx(self, pdf_path, output_docx_path):
        """Converts PDF text content to a DOCX file (TEXT ONLY)."""
        if not DOCX_AVAILABLE:
            self.log("FATAL ERROR: 'python-docx' library is not installed. Conversion aborted.")
            self.log("Please install it: pip install python-docx")
            return False
            
        self.log("Starting PDF to DOCX (Text Only) conversion...")
        
        try:
            doc = fitz.open(pdf_path)
            # Create a new Word document
            word_doc = Document()
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Extract text block by block to preserve some paragraph structure
                text = page.get_text("text")
                word_doc.add_paragraph(text)
                word_doc.add_page_break()
                
            word_doc.save(output_docx_path)
            doc.close()
            
            self.log(f"PDF text successfully extracted and saved to DOCX: {os.path.basename(output_docx_path)}")
            self.log("NOTE: This is a TEXT-ONLY conversion. Layout, images, and complex tables are not preserved.")
            return True

        except Exception as e:
            self.log(f"ERROR during PDF to DOCX conversion: {e}")
            return False

    # [8] DOCX to PDF (Placeholder/Warning)
    def docx_to_pdf(self, docx_path, output_pdf_path):
        """Placeholder for DOCX to PDF conversion (requires complex setup or external tools)."""
        self.log("--- DOCX to PDF Conversion Warning ---")
        self.log("This operation is highly complex in pure Python.")
        self.log("Reliable DOCX to PDF rendering typically requires external software (like MS Word, LibreOffice, or Pandoc) to be installed and accessible.")
        self.log("No simple, pure-Python library exists to guarantee perfect layout translation.")
        self.log("Operation aborted. Please use an external tool or service for this conversion.")
        return False

# --- GUI Application Class ---

class FileUtilityApp:
    def __init__(self, master):
        self.master = master
        master.title("File Utility Suite")
        master.configure(bg="#f0f0f0")

        # Configuration and State
        self.processor = FileProcessor(self.log_message)
        
        # Style Configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=('Inter', 10, 'bold'), padding=[15, 5])
        style.configure('TLabel', background="#f0f0f0", font=('Inter', 10))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=6, background="#4CAF50", foreground="black")
        style.map('TButton', background=[('active', '#388E3C')])
        
        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Create all 8 Tabs
        self.create_pdf_to_image_tab()
        self.create_image_to_pdf_tab()
        self.create_merge_pdfs_tab()
        self.create_image_reducer_tab()
        self.create_pdf_reducer_tab()
        self.create_pdf_page_remover_tab() 
        self.create_pdf_to_docx_tab()
        self.create_docx_to_pdf_tab()

        # Log Panel
        log_frame = tk.Frame(master, bg="#e0e0e0", padx=10, pady=10)
        log_frame.pack(fill="x", side="bottom")
        tk.Label(log_frame, text="Activity Log", font=('Inter', 10, 'bold'), bg="#e0e0e0").pack(pady=(0, 5))
        self.log_text = tk.Text(log_frame, height=5, state='disabled', bg="#ffffff", fg="#333333", borderwidth=1, relief="sunken", font=('Consolas', 9))
        self.log_text.pack(fill="x")
        
        # Initial Welcome Message
        self.log_message("Welcome to the File Utility Suite! 8 tools available.")
        self.log_message("--- DEPENDENCY CHECK ---")
        self.log_message("Required: PyMuPDF (fitz) and Pillow (PIL).")
        if DOCX_AVAILABLE:
            self.log_message("'python-docx' found. DOCX tools are enabled.")
        else:
            self.log_message("WARNING: 'python-docx' is missing. PDF to DOCX will fail. Run: pip install python-docx")


    def log_message(self, message):
        """Enables the Text widget, inserts the message, and then disables it."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.master.update()

    # --- Tab 1: PDF to Image ---
    def create_pdf_to_image_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='PDF to Image')
        self.pdf_path_var = tk.StringVar()
        self.img_format_var = tk.StringVar(value='png')
        
        ttk.Label(tab, text="Select PDF File:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(tab, textvariable=self.pdf_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(tab, text="Browse", command=self._select_pdf_input).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(tab, text="Output Format:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Radiobutton(tab, text="PNG", variable=self.img_format_var, value='png').grid(row=1, column=1, sticky="w", padx=5)
        ttk.Radiobutton(tab, text="JPEG", variable=self.img_format_var, value='jpeg').grid(row=1, column=1, sticky="w", padx=60)
        
        ttk.Button(tab, text="Convert PDF to Images", command=self._convert_pdf_to_images).grid(row=2, column=0, columnspan=3, pady=15)

    def _select_pdf_input(self):
        filepath = filedialog.askopenfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.pdf_path_var.set(filepath)

    def _convert_pdf_to_images(self):
        pdf_path = self.pdf_path_var.get()
        img_format = self.img_format_var.get()
        
        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder for Images")
        if not output_dir:
            self.log_message("Conversion cancelled by user.")
            return

        self.processor.pdf_to_images(pdf_path, output_dir, img_format)

    # --- Tab 2: Image to PDF ---
    def create_image_to_pdf_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='Image to PDF')
        self.selected_images = []
        
        ttk.Label(tab, text="Select Images (PNG/JPEG) to combine into one PDF:").grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=1, column=0, sticky="w", columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Add Images", command=self._select_images_to_pdf).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear List", command=self._clear_image_list).pack(side="left", padx=5)
        
        self.image_listbox = tk.Listbox(tab, width=65, height=8, selectmode=tk.SINGLE, font=('Inter', 9))
        self.image_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        tab.grid_rowconfigure(2, weight=1)
        
        ttk.Button(tab, text="Create PDF from Images", command=self._convert_images_to_pdf).grid(row=3, column=0, columnspan=2, pady=15)
        
    def _select_images_to_pdf(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Image Files", 
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        for path in file_paths:
            if path not in self.selected_images:
                self.selected_images.append(path)
                self.image_listbox.insert(tk.END, os.path.basename(path))

    def _clear_image_list(self):
        self.selected_images = []
        self.image_listbox.delete(0, tk.END)
        self.log_message("Image list cleared.")

    def _convert_images_to_pdf(self):
        if not self.selected_images:
            messagebox.showerror("Error", "Please add at least one image to the list.")
            return
        
        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            title="Save Output PDF File"
        )
        if not output_pdf_path:
            self.log_message("Conversion cancelled by user.")
            return
        
        self.processor.images_to_pdf(self.selected_images, output_pdf_path)

    # --- Tab 3: Merge PDFs ---
    def create_merge_pdfs_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='Merge PDFs')
        self.pdfs_to_merge = []
        
        ttk.Label(tab, text="Select PDFs to merge (order matters):").grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=1, column=0, sticky="w", columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Add PDF(s)", command=self._select_pdfs_to_merge).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear List", command=self._clear_merge_list).pack(side="left", padx=5)
        
        self.merge_listbox = tk.Listbox(tab, width=65, height=8, selectmode=tk.SINGLE, font=('Inter', 9))
        self.merge_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        tab.grid_rowconfigure(2, weight=1)
        
        ttk.Button(tab, text="Merge PDFs", command=self._process_pdf_merge).grid(row=3, column=0, columnspan=2, pady=15)
        
    def _select_pdfs_to_merge(self):
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files to Merge", 
            filetypes=[("PDF files", "*.pdf")]
        )
        for path in file_paths:
            self.pdfs_to_merge.append(path)
            self.merge_listbox.insert(tk.END, os.path.basename(path))

    def _clear_merge_list(self):
        self.pdfs_to_merge = []
        self.merge_listbox.delete(0, tk.END)
        self.log_message("PDF merge list cleared.")

    def _process_pdf_merge(self):
        if len(self.pdfs_to_merge) < 2:
            messagebox.showerror("Error", "Please add at least two PDF files to merge.")
            return

        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            title="Save Merged PDF File"
        )
        if not output_pdf_path:
            self.log_message("Merge operation cancelled by user.")
            return

        self.processor.merge_pdfs(self.pdfs_to_merge, output_pdf_path)

    # --- Tab 4: Image Reducer ---
    def create_image_reducer_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='Image Reducer')

        self.images_to_reduce = []
        
        ttk.Label(tab, text="Select PNG/JPEG images to reduce file size:").grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=1, column=0, sticky="w", columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Add Images", command=self._select_images_to_reduce).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear List", command=self._clear_reduce_img_list).pack(side="left", padx=5)
        
        self.reduce_img_listbox = tk.Listbox(tab, width=65, height=6, selectmode=tk.SINGLE, font=('Inter', 9))
        self.reduce_img_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        tab.grid_rowconfigure(2, weight=1)
        
        ttk.Label(tab, text="JPEG Quality (1-100, default 85):").grid(row=3, column=0, sticky="w", pady=5)
        self.quality_scale = tk.Scale(tab, from_=1, to=100, orient=tk.HORIZONTAL, length=200, bg="#f0f0f0", highlightbackground="#f0f0f0")
        self.quality_scale.set(85)
        self.quality_scale.grid(row=3, column=1, sticky="w", pady=5)
        
        ttk.Label(tab, text="Progress:").grid(row=4, column=0, sticky="w", pady=5)
        self.image_progress = ttk.Progressbar(tab, orient='horizontal', length=300, mode='determinate')
        self.image_progress.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Button(tab, text="Reduce Image Sizes", command=self._process_image_reduction).grid(row=5, column=0, columnspan=2, pady=15)
        
    def _select_images_to_reduce(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Images to Compress", 
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        for path in file_paths:
            if path not in self.images_to_reduce:
                self.images_to_reduce.append(path)
                self.reduce_img_listbox.insert(tk.END, os.path.basename(path))

    def _clear_reduce_img_list(self):
        self.images_to_reduce = []
        self.reduce_img_listbox.delete(0, tk.END)
        self.image_progress['value'] = 0
        self.log_message("Image reduction list cleared.")

    def _process_image_reduction(self):
        if not self.images_to_reduce:
            messagebox.showerror("Error", "Please add at least one image to reduce.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder for Reduced Images")
        if not output_dir:
            self.log_message("Image reduction cancelled by user.")
            return
        
        self.image_progress['value'] = 0
        quality = self.quality_scale.get()
        
        def update_progress(value):
            self.image_progress['value'] = value
            self.master.update_idletasks()

        self.processor.reduce_image_size(self.images_to_reduce, output_dir, quality, update_progress)
        self.image_progress['value'] = 100

    # --- Tab 5: PDF Reducer ---
    def create_pdf_reducer_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='PDF Reducer')

        self.pdf_reduce_path_var = tk.StringVar()
        
        ttk.Label(tab, text="Select PDF File to Reduce:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(tab, textvariable=self.pdf_reduce_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(tab, text="Browse", command=self._select_pdf_reduce_input).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(tab, text="Note: Reduction works best on PDFs containing large, unoptimized images.").grid(row=1, column=0, columnspan=3, sticky="w", pady=10)
        
        ttk.Label(tab, text="Progress:").grid(row=2, column=0, sticky="w", pady=5)
        self.pdf_progress = ttk.Progressbar(tab, orient='horizontal', length=300, mode='determinate')
        self.pdf_progress.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Button(tab, text="Reduce PDF Size", command=self._process_pdf_reduction).grid(row=3, column=0, columnspan=3, pady=15)

    def _select_pdf_reduce_input(self):
        filepath = filedialog.askopenfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.pdf_reduce_path_var.set(filepath)
            self.pdf_progress['value'] = 0

    def _process_pdf_reduction(self):
        pdf_path = self.pdf_reduce_path_var.get()
        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return
            
        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(pdf_path).replace('.pdf', '_reduced.pdf'),
            title="Save Reduced PDF File As"
        )
        if not output_pdf_path:
            self.log_message("PDF reduction cancelled by user.")
            return

        self.pdf_progress['value'] = 0
        
        def update_progress(value):
            self.pdf_progress['value'] = value
            self.master.update_idletasks()

        self.processor.reduce_pdf_size(pdf_path, output_pdf_path, update_progress)

    # --- Tab 6: PDF Page Remover ---
    def create_pdf_page_remover_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='PDF Page Remover')

        self.pdf_remover_path_var = tk.StringVar()
        self.pages_to_remove_var = tk.StringVar()
        self.pdf_page_count_var = tk.StringVar(value="Pages: N/A")
        
        ttk.Label(tab, text="Select PDF File:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(tab, textvariable=self.pdf_remover_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(tab, text="Browse", command=self._select_pdf_remover_input).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(tab, textvariable=self.pdf_page_count_var, foreground="#388E3C", font=('Inter', 10, 'bold')).grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 10))

        ttk.Label(tab, text="Pages to REMOVE (e.g., 1, 3-5, 8):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(tab, textvariable=self.pages_to_remove_var, width=40).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab, text="A new PDF will be created with the remaining pages.").grid(row=3, column=0, columnspan=3, sticky="w", pady=10)
        
        ttk.Button(tab, text="Remove Pages & Save New PDF", command=self._process_pdf_page_removal).grid(row=4, column=0, columnspan=3, pady=15)
        
    def _select_pdf_remover_input(self):
        filepath = filedialog.askopenfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.pdf_remover_path_var.set(filepath)
            try:
                doc = fitz.open(filepath)
                self.pdf_page_count_var.set(f"Total Pages: {len(doc)}")
                doc.close()
            except Exception:
                self.pdf_page_count_var.set("Pages: Error reading file")
                self.log_message(f"Error reading page count for {os.path.basename(filepath)}")

    def _process_pdf_page_removal(self):
        pdf_path = self.pdf_remover_path_var.get()
        pages_to_remove_str = self.pages_to_remove_var.get()
        
        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return

        if not pages_to_remove_str:
            messagebox.showerror("Error", "Please enter the page numbers or ranges you wish to remove.")
            return

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            pages_to_remove_1_based = set()
            parts = pages_to_remove_str.replace(" ", "").split(',')
            
            for part in parts:
                if not part: continue
                if '-' in part:
                    start_s, end_s = part.split('-')
                    start = max(1, int(start_s))
                    end = min(total_pages, int(end_s))
                    pages_to_remove_1_based.update(range(start, end + 1))
                else:
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        pages_to_remove_1_based.add(page_num)
                    else:
                        messagebox.showerror("Input Error", f"Page number {page_num} is out of bounds (1-{total_pages}).")
                        return

        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid page range format: {e}")
            return
            
        all_pages_0_based = set(range(total_pages))
        pages_to_keep_0_based = all_pages_0_based - {p - 1 for p in pages_to_remove_1_based}
        pages_to_keep_0_based = sorted(list(pages_to_keep_0_based))

        if not pages_to_keep_0_based:
             messagebox.showwarning("Warning", "All pages have been selected for removal. The output PDF will be empty.")

        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(pdf_path).replace('.pdf', '_filtered.pdf'),
            title="Save New PDF File As"
        )
        
        if not output_pdf_path:
            self.log_message("Page removal cancelled by user.")
            return

        self.processor.remove_pdf_pages(pdf_path, pages_to_keep_0_based, output_pdf_path)

    # --- Tab 7: PDF to DOCX ---
    def create_pdf_to_docx_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='PDF to DOCX (Text Only)')

        self.pdf_to_docx_path_var = tk.StringVar()
        
        ttk.Label(tab, text="Select PDF File to convert to DOCX:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(tab, textvariable=self.pdf_to_docx_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(tab, text="Browse", command=self._select_pdf_to_docx_input).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(tab, text="NOTE: This performs a text-only extraction. Complex layouts, tables, and images will be lost.", foreground="red").grid(row=1, column=0, columnspan=3, sticky="w", pady=10)
        
        ttk.Button(tab, text="Convert PDF to DOCX", command=self._process_pdf_to_docx).grid(row=2, column=0, columnspan=3, pady=15)

    def _select_pdf_to_docx_input(self):
        filepath = filedialog.askopenfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.pdf_to_docx_path_var.set(filepath)

    def _process_pdf_to_docx(self):
        pdf_path = self.pdf_to_docx_path_var.get()
        
        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return
            
        output_docx_path = filedialog.asksaveasfilename(
            defaultextension=".docx", 
            filetypes=[("Word Document", "*.docx")],
            initialfile=os.path.basename(pdf_path).replace('.pdf', '.docx'),
            title="Save Output DOCX File As"
        )
        
        if not output_docx_path:
            self.log_message("Conversion cancelled by user.")
            return

        self.processor.pdf_to_docx(pdf_path, output_docx_path)


    # --- Tab 8: DOCX to PDF (Placeholder) ---
    def create_docx_to_pdf_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text='DOCX to PDF')

        self.docx_to_pdf_path_var = tk.StringVar()
        
        ttk.Label(tab, text="Select DOCX File to convert to PDF:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(tab, textvariable=self.docx_to_pdf_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(tab, text="Browse", command=self._select_docx_to_pdf_input).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(tab, text="NOTE: This requires specialized rendering software (e.g., LibreOffice).", foreground="red", font=('Inter', 10, 'bold')).grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 5))
        ttk.Label(tab, text="Pure Python does not reliably support complex DOCX-to-PDF conversion.", foreground="red").grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        ttk.Button(tab, text="Convert DOCX to PDF", command=self._process_docx_to_pdf).grid(row=3, column=0, columnspan=3, pady=15)

    def _select_docx_to_pdf_input(self):
        filepath = filedialog.askopenfilename(defaultextension=".docx", filetypes=[("Word Documents", "*.docx")])
        if filepath:
            self.docx_to_pdf_path_var.set(filepath)

    def _process_docx_to_pdf(self):
        docx_path = self.docx_to_pdf_path_var.get()
        
        if not docx_path:
            messagebox.showerror("Error", "Please select a DOCX file.")
            return
            
        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(docx_path).replace('.docx', '.pdf'),
            title="Save Output PDF File As"
        )
        
        if not output_pdf_path:
            self.log_message("Conversion cancelled by user.")
            return

        # This will trigger the warning message in the log
        self.processor.docx_to_pdf(docx_path, output_pdf_path)


# --- Main Execution ---
if __name__ == "__main__":
    # Perform initial check for core libraries
    try:
        # Check for PyMuPDF and Pillow first
        import fitz
        from PIL import Image
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        # Give a clear error message that specifies the install command
        messagebox.showerror(
            "Missing Dependencies", 
            f"A core library is missing: {e}. Please install all packages: pip install PyMuPDF Pillow python-docx"
        )
        root.destroy()
        exit()
        
    root = tk.Tk()
    app = FileUtilityApp(root)
    root.mainloop()
