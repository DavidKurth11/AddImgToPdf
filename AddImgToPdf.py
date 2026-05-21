#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insertar Imagen en PDFs - Versión con Interfaz Gráfica
Permite seleccionar carpetas e imagen mediante ventanas
"""

import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading


class PDFImageInserterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Insertar Imagen en PDFs")
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        
        # Variables
        self.carpeta_pdfs = tk.StringVar()
        self.carpeta_salida = tk.StringVar()
        self.imagen = tk.StringVar()
        self.coord_x = tk.IntVar(value=350)
        self.coord_y = tk.IntVar(value=600)
        self.pagina = tk.IntVar(value=1)
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20 20 30 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="Insertar Imagen en Múltiples PDFs", 
                          font=('Arial', 14, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Carpeta de PDFs
        ttk.Label(main_frame, text="Carpeta con PDFs:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.carpeta_pdfs, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Buscar...", command=self.seleccionar_carpeta_pdfs).grid(row=1, column=2, padx=(0, 10))
        
        # Carpeta de salida
        ttk.Label(main_frame, text="Carpeta de salida:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.carpeta_salida, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(main_frame, text="Buscar...", command=self.seleccionar_carpeta_salida).grid(row=2, column=2, padx=(0, 10))
        
        # Imagen
        ttk.Label(main_frame, text="Imagen a insertar:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.imagen, width=50).grid(row=3, column=1, padx=5)
        ttk.Button(main_frame, text="Buscar...", command=self.seleccionar_imagen).grid(row=3, column=2, padx=(0, 10))
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Coordenadas
        coord_frame = ttk.LabelFrame(main_frame, text="Posición de la imagen", padding="10")
        coord_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(coord_frame, text="Coordenada X (horizontal):").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Spinbox(coord_frame, from_=0, to=1000, textvariable=self.coord_x, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(coord_frame, text="puntos desde la izquierda").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(coord_frame, text="Coordenada Y (vertical):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(coord_frame, from_=0, to=1000, textvariable=self.coord_y, width=10).grid(row=1, column=1, padx=5)
        ttk.Label(coord_frame, text="puntos desde arriba").grid(row=1, column=2, sticky=tk.W)
        
        # Página
        ttk.Label(coord_frame, text="Número de página:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(coord_frame, from_=1, to=100, textvariable=self.pagina, width=10).grid(row=2, column=1, padx=5)
        ttk.Label(coord_frame, text="(1 = primera página)").grid(row=2, column=2, sticky=tk.W)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=6, width=70, state='disabled')
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.btn_procesar = ttk.Button(button_frame, text="▶ Procesar PDFs", 
                                       command=self.procesar_pdfs, style='Accent.TButton')
        self.btn_procesar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
    def seleccionar_carpeta_pdfs(self):
        """Selecciona la carpeta con los PDFs originales"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta con PDFs")
        if carpeta:
            self.carpeta_pdfs.set(carpeta)
            # Sugerir carpeta de salida automáticamente con /output
            if not self.carpeta_salida.get():
                salida = os.path.join(carpeta, "output")
                self.carpeta_salida.set(salida)
    
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
    
    def log(self, mensaje):
        """Añade un mensaje al log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, mensaje + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def validar_entradas(self):
        """Valida que todos los campos estén completos"""
        if not self.carpeta_pdfs.get():
            messagebox.showerror("Error", "Debes seleccionar la carpeta con los PDFs")
            return False
        
        if not self.carpeta_salida.get():
            messagebox.showerror("Error", "Debes seleccionar la carpeta de salida")
            return False
        
        if not self.imagen.get():
            messagebox.showerror("Error", "Debes seleccionar la imagen a insertar")
            return False
        
        if not os.path.exists(self.carpeta_pdfs.get()):
            messagebox.showerror("Error", "La carpeta de PDFs no existe")
            return False
        
        if not os.path.exists(self.imagen.get()):
            messagebox.showerror("Error", "La imagen no existe")
            return False
        
        # Advertir si entrada y salida son la misma carpeta
        carpeta_pdfs_abs = os.path.abspath(self.carpeta_pdfs.get())
        carpeta_salida_abs = os.path.abspath(self.carpeta_salida.get())
        
        if carpeta_pdfs_abs.lower() == carpeta_salida_abs.lower():
            respuesta = messagebox.askokcancel(
                "⚠️ Advertencia",
                "La carpeta de entrada y salida son la misma.\n\n"
                "Esto SOBRESCRIBIRÁ los archivos PDF originales.\n"
                "No habrá forma de recuperarlos si algo sale mal.\n\n"
                "¿Estás seguro de que quieres continuar?"
            )
            if not respuesta:
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
            
            carpeta_pdfs = self.carpeta_pdfs.get()
            carpeta_salida = self.carpeta_salida.get()
            imagen = self.imagen.get()
            x = self.coord_x.get()
            y = self.coord_y.get()
            pagina = self.pagina.get() - 1  # Convertir a índice 0
            
            # Crear carpeta de salida
            os.makedirs(carpeta_salida, exist_ok=True)
            
            # Buscar PDFs
            pdfs = list(Path(carpeta_pdfs).glob("*.pdf"))
            
            if len(pdfs) == 0:
                self.log("❌ No se encontraron archivos PDF")
                messagebox.showwarning("Aviso", "No se encontraron archivos PDF en la carpeta seleccionada")
                return
            
            self.log(f"📁 Encontrados {len(pdfs)} archivos PDF")
            self.log(f"🖼️  Imagen: {os.path.basename(imagen)}")
            self.log(f"📍 Coordenadas: X={x}, Y={y}")
            self.log(f"📄 Página: {pagina + 1}")
            self.log("-" * 60)
            
            procesados = 0
            errores = 0
            
            for pdf_path in pdfs:
                nombre = pdf_path.name
                output_path = os.path.join(carpeta_salida, nombre)
                
                self.log(f"Procesando: {nombre}...")
                
                if self.insertar_imagen_en_pdf(str(pdf_path), imagen, x, y, pagina, output_path):
                    self.log(f"✅ {nombre} completado")
                    procesados += 1
                else:
                    errores += 1
            
            self.log("-" * 60)
            self.log(f"✅ Procesados correctamente: {procesados}")
            if errores > 0:
                self.log(f"❌ Errores: {errores}")
            self.log(f"📂 Archivos guardados en: {carpeta_salida}")
            self.log("\n🎉 ¡Proceso completado!")
            
            messagebox.showinfo("Completado", 
                              f"Proceso finalizado\n\n✅ Procesados: {procesados}\n❌ Errores: {errores}\n\nArchivos guardados en:\n{carpeta_salida}")
            
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
        
        # Ejecutar en hilo separado para no bloquear la interfaz
        thread = threading.Thread(target=self.procesar_pdfs_thread)
        thread.daemon = True
        thread.start()


def main():
    """Función principal"""
    root = tk.Tk()
    
    # Estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar color de fondo de la ventana para que coincida con el tema
    root.configure(bg=style.lookup('TFrame', 'background'))
    
    app = PDFImageInserterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()