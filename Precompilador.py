import tkinter as tk
from tkinter import filedialog, messagebox
import re

class MicroCCompiler:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroC Precompilador - Sin Título")
        self.root.geometry("900x800")
        
        # Variables de estado
        self.archivo_actual = None
        self.contenido_guardado = ""
        
        # --- Configuración de Estilo (Tema Oscuro) ---
        self.bg_color = "#1e1e1e"       # Fondo del texbox1
        self.fg_color = "#d4d4d4"       # Texto normal
        self.keyword_color = "#569cd6"  # int, return, etc.
        self.string_color = "#ce9178"   # "Textos"
        self.comment_color = "#6a9955"  # // Comentarios
        self.ui_bg = "#252526"          # Fondo del color de la terminal 
        
        self.root.configure(bg=self.ui_bg)

        # --- Menú Superior ---
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # Menú Archivo
        archivo_menu = tk.Menu(self.menu_bar, tearoff=0)
        archivo_menu.add_command(label="Nuevo", command=self.nuevo_archivo)
        archivo_menu.add_command(label="Abrir", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar", command=self.guardar_archivo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.salir_aplicacion)
        self.menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

        # Menú Editar
        editar_menu = tk.Menu(self.menu_bar, tearoff=0)
        editar_menu.add_command(label="Habilitar Edición", command=self.habilitar_edicion)
        self.menu_bar.add_cascade(label="Editar", menu=editar_menu)

        # Menú Compilar
        compilar_menu = tk.Menu(self.menu_bar, tearoff=0)
        compilar_menu.add_command(label="Compilar Código", command=self.compilar)
        self.menu_bar.add_cascade(label="Compilar", menu=compilar_menu)

        # Menú Ayuda
        ayuda_menu = tk.Menu(self.menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_ayuda)
        self.menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)

        # --- Interfaz Gráfica ---
        
        # Frame Principal
        main_frame = tk.Frame(root, bg=self.ui_bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Etiqueta de Archivo (Requisito 10)
        self.lbl_archivo = tk.Label(main_frame, text="Archivo: [Nuevo]", bg=self.ui_bg, fg="#ffffff", anchor="w")
        self.lbl_archivo.pack(fill=tk.X)

        # Editor con Números de Línea
        editor_frame = tk.Frame(main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Números de línea
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, border=0,
                                    background=self.ui_bg, foreground="#858585", state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # TextBox1: Editor de Código 
        self.text_editor = tk.Text(editor_frame, undo=True, wrap="none", bg=self.bg_color, 
                                   fg=self.fg_color, insertbackground="white", font=("Consolas", 12))
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para el editor
        scrollbar = tk.Scrollbar(editor_frame, command=self.text_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.config(yscrollcommand=self.sync_scroll_y(scrollbar, self.text_editor, self.line_numbers))
        
        # Eventos para resaltado y números de línea
        self.text_editor.bind('<KeyRelease>', self.actualizar_interfaz)
        self.text_editor.bind('<MouseWheel>', self.actualizar_lineas)

        # TextBox2: Consola de Salida 
        lbl_consola = tk.Label(main_frame, text="Salida del Compilador:", bg=self.ui_bg, fg="#ffffff", anchor="w")
        lbl_consola.pack(fill=tk.X, pady=(10, 0))
        
        self.text_console = tk.Text(main_frame, height=8, bg="black", fg="#00ff00", font=("Consolas", 10))
        self.text_console.pack(fill=tk.X, pady=5)
        self.text_console.insert(tk.END, "MicroC Compiler Ready...\n")
        self.text_console.config(state='disabled') # Solo lectura por defecto

        # Configuración de Tags para coloreado
        self.configurar_tags()

    # ---Scroll y Líneas ---
    def sync_scroll_y(self, scrollbar, widget1, widget2):
        # Sincroniza el scrollbar con el editor y los números de línea
        def scroll_command(*args):
            scrollbar.set(*args)
            widget2.yview_moveto(args[0])
        return scroll_command

    def actualizar_interfaz(self, event=None):
        self.actualizar_lineas()
        self.resaltar_sintaxis()

    def actualizar_lineas(self, event=None):
        lines = self.text_editor.get('1.0', 'end-1c').count('\n') + 1
        line_numbers_content = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_content)
        self.line_numbers.config(state='disabled')
        # Sincronizar vista
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])

    # --- Lógica de Resaltado de Sintaxis ---
    def configurar_tags(self):
        # Definir colores para las categorías
        self.text_editor.tag_config("keyword", foreground=self.keyword_color)
        self.text_editor.tag_config("string", foreground=self.string_color)
        self.text_editor.tag_config("comment", foreground=self.comment_color)

    def resaltar_sintaxis(self):
        # Limpiar tags previos
        for tag in ["keyword", "string", "comment"]:
            self.text_editor.tag_remove(tag, "1.0", tk.END)

        texto = self.text_editor.get("1.0", tk.END)
        
        # Palabras  C
        keywords = r"\b(int|float|char|if|else|while|for|return|void|include|printf|scanf)\b"
        for match in re.finditer(keywords, texto):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add("keyword", start, end)

        # Cadenas de texto "..."
        for match in re.finditer(r'\".*?\"', texto):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add("string", start, end)

        # Comentarios //
        for match in re.finditer(r'//.*', texto):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add("comment", start, end)

    # --- Funciones Principales  ---

    def nuevo_archivo(self): 
        self.archivo_actual = None
        self.text_editor.delete(1.0, tk.END)
        self.habilitar_edicion() # Habilitar edición al ser nuevo
        self.actualizar_info_archivo("Nuevo Archivo")
        self.log_consola("Nuevo archivo creado.")

    def abrir_archivo(self): 
        filepath = filedialog.askopenfilename(filetypes=[("Archivos C", "*.c"), ("Todos", "*.*")])
        if filepath:
            self.archivo_actual = filepath
            with open(filepath, 'r') as f:
                content = f.read()
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, content)
            self.contenido_guardado = content
            
            # Bloquear edición hasta que se pulse Editar
            self.text_editor.config(state='disabled')
            self.actualizar_info_archivo(filepath)
            self.log_consola(f"Archivo cargado: {filepath}")
            self.log_consola("Modo LECTURA. Presione 'Editar' para modificar.")
            self.resaltar_sintaxis()
            self.actualizar_lineas()

    def guardar_archivo(self): # Requisito 5
        if self.archivo_actual:
            # Sobreescribir (Requisito 5b)
            with open(self.archivo_actual, 'w') as f:
                content = self.text_editor.get(1.0, tk.END).strip()
                f.write(content)
            self.contenido_guardado = content
            self.log_consola(f"Guardado en: {self.archivo_actual}")
        else:
            # Guardar como... (Requisito 5a)
            filepath = filedialog.asksaveasfilename(defaultextension=".c",
                                                    filetypes=[("Archivos C", "*.c")])
            if filepath:
                self.archivo_actual = filepath
                with open(filepath, 'w') as f:
                    content = self.text_editor.get(1.0, tk.END).strip()
                    f.write(content)
                self.contenido_guardado = content
                self.actualizar_info_archivo(filepath)
                self.log_consola(f"Archivo guardado: {filepath}")

    def habilitar_edicion(self): 
        self.text_editor.config(state='normal')
        self.log_consola("Modo EDICIÓN activado.")

    def compilar(self): 
        # Simulación de compilación
        self.log_consola("-" * 30)
        self.log_consola("Iniciando compilación...")
        self.log_consola("[Compilación en desarrollo] Función pendiente.")
        self.log_consola("[el administrador colocara en una actualizacion esta funcion]")
        self.log_consola("-" * 30)

    def mostrar_ayuda(self): 
        messagebox.showinfo("Ayuda", "Compilador MicroC v1.0\nDesarrollado para el curso de Autómatas y Lenguajes.\nel administrador colocara en una actualizacion esta funcion\n el administrador se pondra en contacto con un usted para darle una mejor experiencia")

    def salir_aplicacion(self): 
        # Verificar cambios sin guardar
        contenido_actual = self.text_editor.get(1.0, tk.END).strip()
        # Nota: Al obtener texto de tk.Text siempre agrega un salto de línea al final, por eso el  para que no de error al comparar strip()
        
        # Comparación simple para ver si hubo cambios
        if self.archivo_actual and contenido_actual != self.contenido_guardado.strip():
             respuesta = messagebox.askyesnocancel("Salir", "¿Desea guardar los cambios antes de salir?")
             if respuesta: # Sí
                 self.guardar_archivo()
                 self.root.destroy()
             elif respuesta is False: # No
                 self.root.destroy()
             # Cancelar no hace nada
        elif not self.archivo_actual and len(contenido_actual) > 0:
            respuesta = messagebox.askyesnocancel("Salir", "El archivo no se ha guardado. ¿Desea guardarlo?")
            if respuesta:
                self.guardar_archivo()
                self.root.destroy()
            elif respuesta is False:
                self.root.destroy()
        else:
            self.root.destroy()

    # --- Utilidades ---
    def actualizar_info_archivo(self, nombre): #(Título y TextBox)
        self.root.title(f"MicroC Compiler - {nombre}")
        self.lbl_archivo.config(text=f"Archivo actual: {nombre}")

    def log_consola(self, mensaje):
        self.text_console.config(state='normal')
        self.text_console.insert(tk.END, mensaje + "\n")
        self.text_console.see(tk.END)
        self.text_console.config(state='disabled')

# Inicialización
if __name__ == "__main__":
    root = tk.Tk()
    app = MicroCCompiler(root)
    # Icono genérico para la ventana (opcional)
    #nota:se colocara un icono en una actualizacion pero debe de saber que la imagen o icono deber de tener un nombre y que este guardado en la misma carpeta que el archivo .py
    # root.iconbitmap('icono.ico') 
    root.mainloop()