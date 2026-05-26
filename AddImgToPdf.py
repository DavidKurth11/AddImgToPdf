#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insertar Imagen en PDFs - Versión 2 con Vista Previa
Permite seleccionar archivos individuales y ver preview en tiempo real
"""

import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import io
import threading


class PDFImageInserterGUI_V2:
    def __init__(self, root):
        self.root = root
        self.root.title("Insertar Imagen en PDFs v2")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.root.minsize(900, 750)
        
        # Variables
        self.archivos_pdf = []  # Lista de rutas de PDFs seleccionados
        self.carpeta_salida = tk.StringVar()
        self.imagen = tk.StringVar()
        self.coord_x = tk.IntVar(value=350)
        self.coord_y = tk.IntVar(value=600)
        self.pagina = tk.IntVar(value=1)
        
        # Variable para la imagen de preview
        self.preview_image = None
        
        # Añadir trazas para actualización automática del preview
        self.coord_x.trace_add('write', lambda *args: self.actualizar_preview())
        self.coord_y.trace_add('write', lambda *args: self.actualizar_preview())
        self.pagina.trace_add('write', lambda *args: self.actualizar_preview())
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar columnas para que la preview tenga espacio
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ============ COLUMNA IZQUIERDA ============
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=(0, 10))
        
        # Seleccionar PDFs
        ttk.Label(left_frame, text="Archivos PDF:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Button(left_frame, text="Seleccionar PDFs...", 
                  command=self.seleccionar_pdfs).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Lista de PDFs seleccionados
        list_frame = ttk.LabelFrame(left_frame, text="PDFs seleccionados", padding="5")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Listbox con scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_list = ttk.Scrollbar(list_container)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pdf_listbox = tk.Listbox(list_container, height=6, 
                                       yscrollcommand=scrollbar_list.set)
        self.pdf_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_list.config(command=self.pdf_listbox.yview)
        
        # Botón para quitar PDF seleccionado
        ttk.Button(list_frame, text="❌ Quitar seleccionado", 
                  command=self.quitar_pdf).pack(pady=5)
        
        # Carpeta de salida
        ttk.Label(left_frame, text="Carpeta de salida:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(left_frame, textvariable=self.carpeta_salida, width=35).grid(row=2, column=1, padx=5)
        ttk.Button(left_frame, text="Buscar...", 
                  command=self.seleccionar_carpeta_salida).grid(row=2, column=2)
        
        # Imagen
        ttk.Label(left_frame, text="Imagen a insertar:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(left_frame, textvariable=self.imagen, width=35).grid(row=3, column=1, padx=5)
        ttk.Button(left_frame, text="Buscar...", 
                  command=self.seleccionar_imagen).grid(row=3, column=2)
        
        # Separador
        ttk.Separator(left_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, 
                                                            sticky=(tk.W, tk.E), pady=15)
        
        # Coordenadas
        coord_frame = ttk.LabelFrame(left_frame, text="Posición de la imagen", padding="10")
        coord_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(coord_frame, text="Coordenada X:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Spinbox(coord_frame, from_=0, to=1000, textvariable=self.coord_x, 
                   width=10).grid(row=0, column=1, padx=5)
        ttk.Label(coord_frame, text="px desde izquierda").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(coord_frame, text="Coordenada Y:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(coord_frame, from_=0, to=1000, textvariable=self.coord_y, 
                   width=10).grid(row=1, column=1, padx=5)
        ttk.Label(coord_frame, text="px desde arriba").grid(row=1, column=2, sticky=tk.W)
        
        # Página
        ttk.Label(coord_frame, text="Número de página:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(coord_frame, from_=1, to=100, textvariable=self.pagina, 
                   width=10).grid(row=2, column=1, padx=5)
        ttk.Label(coord_frame, text="(1 = primera)").grid(row=2, column=2, sticky=tk.W)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(left_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Área de log
        log_frame = ttk.LabelFrame(left_frame, text="Progreso", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.log_text = tk.Text(log_frame, height=4, width=50, state='disabled')
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Botones de acción
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.btn_procesar = ttk.Button(button_frame, text="▶ Procesar PDFs", 
                                       command=self.procesar_pdfs)
        self.btn_procesar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # ============ COLUMNA DERECHA - VISTA PREVIA ============
        preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding="10")
        preview_frame.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        # Canvas para la vista previa
        self.preview_canvas = tk.Canvas(preview_frame, width=350, height=500, bg='white')
        self.preview_canvas.pack()
        
        # Etiqueta de ayuda
        self.preview_label = ttk.Label(preview_frame, 
                                       text="Selecciona PDFs e imagen para ver la vista previa",
                                       wraplength=300)
        self.preview_label.pack(pady=10)
        
    def seleccionar_pdfs(self):
        """Selecciona múltiples archivos PDF"""
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        
        if archivos:
            # Agregar archivos a la lista (evitar duplicados)
            for archivo in archivos:
                if archivo not in self.archivos_pdf:
                    self.archivos_pdf.append(archivo)
                    self.pdf_listbox.insert(tk.END, os.path.basename(archivo))
            
            # Si no hay carpeta de salida, sugerir una basada en el primer PDF
            if not self.carpeta_salida.get() and self.archivos_pdf:
                carpeta_primer_pdf = os.path.dirname(self.archivos_pdf[0])
                salida = os.path.join(carpeta_primer_pdf, "output")
                self.carpeta_salida.set(salida)
            
            # Actualizar preview
            self.actualizar_preview()
    
    def quitar_pdf(self):
        """Quita el PDF seleccionado de la lista"""
        seleccion = self.pdf_listbox.curselection()
        if seleccion:
            index = seleccion[0]
            self.pdf_listbox.delete(index)
            self.archivos_pdf.pop(index)
            self.actualizar_preview()
    
    def seleccionar_carpeta_salida(self):
        """Selecciona la carpeta de salida"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_salida.set(carpeta)
    
    def seleccionar_imagen(self):
        """Selecciona la imagen a insertar"""
        imagen = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        if imagen:
            self.imagen.set(imagen)
            self.actualizar_preview()
    
    def actualizar_preview(self):
        """Actualiza la vista previa con el PDF y la imagen"""
        # Verificar que tenemos lo necesario
        if not self.archivos_pdf:
            self.preview_label.config(text="Selecciona al menos un PDF")
            return
        
        if not self.imagen.get() or not os.path.exists(self.imagen.get()):
            self.preview_label.config(text="Selecciona una imagen para ver la vista previa")
            return
        
        try:
            # Usar el primer PDF de la lista
            pdf_path = self.archivos_pdf[0]
            imagen_path = self.imagen.get()
            pagina = self.pagina.get() - 1
            x = self.coord_x.get()
            y = self.coord_y.get()
            
            # Abrir PDF
            doc = fitz.open(pdf_path)
            
            if pagina >= len(doc):
                self.preview_label.config(text=f"El PDF solo tiene {len(doc)} página(s)")
                doc.close()
                return
            
            page = doc[pagina]
            
            # Obtener dimensiones de la imagen
            img_doc = fitz.open(imagen_path)
            img_rect = img_doc[0].rect
            img_width = img_rect.width
            img_height = img_rect.height
            img_doc.close()
            
            # Insertar imagen en el PDF (en memoria, no guardamos)
            rect = fitz.Rect(x, y, x + img_width, y + img_height)
            page.insert_image(rect, filename=imagen_path)
            
            # Renderizar la página a imagen
            zoom = 0.5  # Factor de zoom para ajustar al canvas
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convertir a formato PIL
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Redimensionar si es necesario para que quepa en el canvas
            canvas_width = 350
            canvas_height = 500
            
            img_width, img_height = img.size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            
            if ratio < 1:
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convertir a formato Tkinter
            self.preview_image = ImageTk.PhotoImage(img)
            
            # Mostrar en el canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width // 2, 
                canvas_height // 2, 
                image=self.preview_image, 
                anchor=tk.CENTER
            )
            
            self.preview_label.config(text=f"Preview: {os.path.basename(pdf_path)} - Página {pagina + 1}")
            
            doc.close()
            
        except Exception as e:
            self.preview_label.config(text=f"Error al generar preview: {str(e)}")
    
    def log(self, mensaje):
        """Añade un mensaje al log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, mensaje + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def validar_entradas(self):
        """Valida que todos los campos estén completos"""
        if not self.archivos_pdf:
            messagebox.showerror("Error", "Debes seleccionar al menos un archivo PDF")
            return False
        
        if not self.carpeta_salida.get():
            messagebox.showerror("Error", "Debes seleccionar la carpeta de salida")
            return False
        
        if not self.imagen.get():
            messagebox.showerror("Error", "Debes seleccionar la imagen a insertar")
            return False
        
        if not os.path.exists(self.imagen.get()):
            messagebox.showerror("Error", "La imagen no existe")
            return False
        
        # Verificar que todos los PDFs existen
        for pdf_path in self.archivos_pdf:
            if not os.path.exists(pdf_path):
                messagebox.showerror("Error", f"El archivo no existe:\n{pdf_path}")
                return False
        
        return True
    
    def insertar_imagen_en_pdf(self, pdf_path, imagen_path, x, y, pagina, output_path):
        """Inserta una imagen en un PDF"""
        try:
            doc = fitz.open(pdf_path)
            
            if pagina >= len(doc):
                self.log(f"⚠️  {os.path.basename(pdf_path)} tiene menos páginas que {pagina + 1}")
                doc.close()
                return False
            
            page = doc[pagina]
            
            # Obtener dimensiones de la imagen
            img_doc = fitz.open(imagen_path)
            img_page = img_doc[0]
            img_rect = img_page.rect
            img_width = img_rect.width
            img_height = img_rect.height
            img_doc.close()
            
            # Insertar la imagen
            rect = fitz.Rect(x, y, x + img_width, y + img_height)
            page.insert_image(rect, filename=imagen_path)
            
            # Guardar
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error en {os.path.basename(pdf_path)}: {str(e)}")
            if 'doc' in locals():
                doc.close()
            return False
    
    def procesar_pdfs_thread(self):
        """Procesa los PDFs en un hilo separado"""
        try:
            # Deshabilitar botón
            self.btn_procesar.config(state='disabled')
            self.progress.start()
            
            carpeta_salida = self.carpeta_salida.get()
            imagen = self.imagen.get()
            x = self.coord_x.get()
            y = self.coord_y.get()
            pagina = self.pagina.get() - 1
            
            # Crear carpeta de salida
            os.makedirs(carpeta_salida, exist_ok=True)
            
            self.log(f"📁 Procesando {len(self.archivos_pdf)} archivos PDF")
            self.log(f"🖼️  Imagen: {os.path.basename(imagen)}")
            self.log(f"📍 Coordenadas: X={x}, Y={y}")
            self.log(f"📄 Página: {pagina + 1}")
            self.log("-" * 50)
            
            procesados = 0
            errores = 0
            
            for pdf_path in self.archivos_pdf:
                nombre = os.path.basename(pdf_path)
                output_path = os.path.join(carpeta_salida, nombre)
                
                self.log(f"Procesando: {nombre}...")
                
                if self.insertar_imagen_en_pdf(pdf_path, imagen, x, y, pagina, output_path):
                    self.log(f"✅ {nombre} completado")
                    procesados += 1
                else:
                    errores += 1
            
            self.log("-" * 50)
            self.log(f"✅ Procesados: {procesados}")
            if errores > 0:
                self.log(f"❌ Errores: {errores}")
            self.log(f"📂 Guardados en: {carpeta_salida}")
            
            messagebox.showinfo("Completado", 
                              f"Proceso finalizado\n\n✅ Procesados: {procesados}\n❌ Errores: {errores}")
            
        except Exception as e:
            self.log(f"❌ Error general: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.btn_procesar.config(state='normal')
    
    def procesar_pdfs(self):
        """Inicia el procesamiento de PDFs"""
        if not self.validar_entradas():
            return
        
        # Limpiar log
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.procesar_pdfs_thread)
        thread.daemon = True
        thread.start()


def main():
    """Función principal"""
    root = tk.Tk()
    
    # Estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar color de fondo
    root.configure(bg=style.lookup('TFrame', 'background'))
    
    app = PDFImageInserterGUI_V2(root)
    root.mainloop()


if __name__ == "__main__":
    main()