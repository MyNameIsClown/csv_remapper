
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

class CSVRemapperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Remapper")
        self.root.geometry("800x600")  # Tamaño mínimo con proporción 4:3
        self.root.minsize(800, 600)
        # Cargar el icono de la aplicación
        # self.root.iconbitmap("app_icon.ico")  
        self.filepath = None
        self.df = None

        self.style = ttk.Style("flatly")  # Usar el tema 'flatly' de ttkbootstrap para colores consistentes

        # Frame inicial con el botón para cargar el CSV
        self.initial_frame = ttk.Frame(root)
        self.initial_frame.pack(fill=BOTH, expand=True)

        self.load_button = ttk.Button(self.initial_frame, text="Cargar CSV", command=self.load_csv, bootstyle=PRIMARY)
        self.load_button.pack(pady=20, ipadx=20, ipady=10, expand=True)

        # Frame para la animación de carga (simple Label por ahora)
        self.loading_frame = ttk.Frame(root)

        self.loading_label = ttk.Label(self.loading_frame, text="Cargando...", font=("Helvetica", 16))
        self.loading_label.pack(pady=20)

        # Frame para el panel de edición
        self.editor_frame = ttk.Frame(root)

        # Frame para los botones de la izquierda
        self.button_frame = ttk.Frame(self.editor_frame)
        self.button_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        self.save_button = ttk.Button(self.button_frame, text="Guardar CSV", command=self.save_csv, bootstyle=SUCCESS)
        self.save_button.pack(pady=10, fill=X)
        self.save_button.config(state=tk.DISABLED)

        self.save_config_button = ttk.Button(self.button_frame, text="Guardar Configuración", command=self.save_config, bootstyle=INFO)
        self.save_config_button.pack(pady=10, fill=X)

        self.load_config_button = ttk.Button(self.button_frame, text="Cargar Configuración", command=self.load_config, bootstyle=WARNING)
        self.load_config_button.pack(pady=10, fill=X)

        self.help_button = ttk.Button(self.button_frame, text="Ayuda", command=self.show_help, bootstyle=SECONDARY)
        self.help_button.pack(pady=10, fill=X)

        self.back_button = ttk.Button(self.button_frame, text="Volver", command=self.go_back, bootstyle=SECONDARY)
        self.back_button.pack(side=BOTTOM, pady=10, fill=X)

        # Frame para el panel de edición con scrollbar
        self.columns_frame_container = ttk.Frame(self.editor_frame)
        self.columns_frame_container.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.columns_frame_container)
        self.scrollbar = ttk.Scrollbar(self.columns_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show_loading(self):
        self.initial_frame.pack_forget()
        self.editor_frame.pack_forget()
        self.loading_frame.pack(fill=BOTH, expand=True)
        self.root.update_idletasks()

    def hide_loading(self):
        self.loading_frame.pack_forget()
        self.editor_frame.pack(fill=BOTH, expand=True)

    def go_back(self):
        self.editor_frame.pack_forget()
        self.initial_frame.pack(fill=BOTH, expand=True)

    def load_csv(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not self.filepath:
            return

        self.show_loading()
        self.df = pd.read_csv(self.filepath, decimal=",")
        self.display_columns()
        self.hide_loading()

    def display_columns(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.column_vars = {}
        self.include_vars = {}
        self.type_vars = {}

        for col in self.df.columns:
            var = tk.StringVar(value=col)
            include_var = tk.BooleanVar(value=False)  # Casillas desmarcadas por defecto
            type_var = tk.StringVar(value="Texto")  # Tipo de dato por defecto

            self.column_vars[col] = var
            self.include_vars[col] = include_var
            self.type_vars[col] = type_var

            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill='x', pady=2)

            checkbutton = ttk.Checkbutton(frame, variable=include_var)
            checkbutton.pack(side='left', padx=5)

            label = ttk.Label(frame, text=col)
            label.pack(side='left', padx=5)

            entry = ttk.Entry(frame, textvariable=var)
            entry.pack(side='left', fill='x', expand=True, padx=5)

            type_menu = ttk.Combobox(frame, textvariable=type_var, values=["Numero negativo", "Numero positivo", "Texto", "Fecha"])
            type_menu.pack(side='left', padx=5)

        self.save_button.config(state=tk.NORMAL)

    def save_csv(self):
        new_columns = {old: var.get() for old, var in self.column_vars.items() if self.include_vars[old].get()}
        column_types = {old: self.type_vars[old].get() for old in new_columns.keys()}

        merged_columns = {}

        for old_col, new_col in new_columns.items():
            col_type = column_types[old_col]
            converted_col = self.convert_column(self.df[old_col], col_type)

            if converted_col is None:
                Messagebox.show_error(f"Column '{old_col}' contains invalid data for type '{col_type}'.", parent=self.root)
                return

            if new_col in merged_columns:
                merged_columns[new_col] = merged_columns[new_col].combine_first(converted_col)
            else:
                merged_columns[new_col] = converted_col

        new_df = pd.DataFrame(merged_columns)

        # Formatear los números antes de guardar
        for col in new_df.select_dtypes(include=['float64', 'int64']).columns:
            new_df[col] = new_df[col].apply(lambda x: "{:,.2f}".format(x))

        new_filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if new_filepath:
            new_df.to_csv(new_filepath, index=False, decimal=",")
            Messagebox.show_info("CSV file saved successfully!", parent=self.root)

    def convert_column(self, col, col_type):
        if col_type == "Texto":
            return col.astype(str)
        elif col_type == "Numero negativo":
            valid_col = col.apply(lambda x: self.is_valid_to_convert_to_number(x) if pd.notna(x) else True)
            if valid_col.all():
                return col.apply(lambda x: self.convert_to_number(x, negative=True) if pd.notna(x) else x)
            else:
                return None
        elif col_type == "Numero positivo":
            valid_col = col.apply(lambda x: self.is_valid_to_convert_to_number(x) if pd.notna(x) else True)
            if valid_col.all():
                return col.apply(lambda x: self.convert_to_number(x) if pd.notna(x) else x)
            else:
                return None
        elif col_type == "Fecha":
            try:
                return pd.to_datetime(col, errors='coerce')
            except Exception as e:
                print(f"Error converting column to date: {e}")
                return None

    def merge_columns(self, col1, col2):
        return col1.combine_first(col2)

    def is_valid_to_convert_to_number(self, value):
        try:
            self.convert_to_number(value)
            return True
        except ValueError:
            return False

    def convert_to_number(self, value, negative=False):
        # Convertir el valor usando la coma como separador decimal
        number = float(str(value).replace(".", "").replace(",", "."))
        return number if not negative else number * -1

    def save_config(self):
        config = {
            "columns": {col: var.get() for col, var in self.column_vars.items()},
            "includes": {col: var.get() for col, var in self.include_vars.items()},
            "types": {col: var.get() for col, var in self.type_vars.items()},
        }
        config_filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if config_filepath:
            with open(config_filepath, 'w') as f:
                json.dump(config, f)
            Messagebox.show_info("Configuration saved successfully!", parent=self.root)

    def load_config(self):
        config_filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not config_filepath:
            return

        with open(config_filepath, 'r') as f:
            config = json.load(f)

        for col, new_name in config["columns"].items():
            if col in self.column_vars:
                self.column_vars[col].set(new_name)

        for col, include in config["includes"].items():
            if col in self.include_vars:
                self.include_vars[col].set(include)

        for col, col_type in config["types"].items():
            if col in self.type_vars:
                self.type_vars[col].set(col_type)

        Messagebox.show_info("Configuration loaded successfully!", parent=self.root)

    def show_help(self):
        help_text = (
            "Instrucciones de Uso:\n"
            "1. Cargue un archivo CSV usando el botón 'Cargar CSV'.\n"
            "2. Seleccione las columnas que desea incluir.\n"
            "3. Renombre las columnas si es necesario.\n"
            "4. Si dos columnas tienen el mismo nombre estas se fusionarán.\n"
            "5. Seleccione el tipo de dato para cada columna.\n"
            "6. Puede guardar la configuración actual usando 'Guardar Configuración'.\n"
            "7. Puede cargar una configuración guardada previamente usando 'Cargar Configuración'.\n"
            "8. Cuando esté listo, guarde el archivo CSV usando 'Guardar CSV'."
        )
        Messagebox.show_info(help_text, title="Ayuda", parent=self.root)

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = CSVRemapperApp(root)
    root.mainloop()

