import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

class CSVRemapperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Remapper")
        self.filepath = None
        self.df = None

        self.load_button = tk.Button(root, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        self.columns_frame = tk.Frame(root)
        self.columns_frame.pack(pady=10)

        self.save_button = tk.Button(root, text="Save CSV", command=self.save_csv)
        self.save_button.pack(pady=10)
        self.save_button.config(state=tk.DISABLED)

    def load_csv(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not self.filepath:
            return

        self.df = pd.read_csv(self.filepath, decimal=",")
        self.display_columns()

    def display_columns(self):
        for widget in self.columns_frame.winfo_children():
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

            frame = tk.Frame(self.columns_frame)
            frame.pack(fill='x', pady=2)

            checkbutton = tk.Checkbutton(frame, variable=include_var)
            checkbutton.pack(side='left', padx=5)

            label = tk.Label(frame, text=col)
            label.pack(side='left', padx=5)

            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side='left', fill='x', expand=True, padx=5)

            type_menu = tk.OptionMenu(frame, type_var, "Numero negativo", "Numero positivo", "Texto")
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
                messagebox.showerror("Error", f"Column '{old_col}' contains invalid data for type '{col_type}'.")
                return

            if new_col in merged_columns:
                merged_columns[new_col] = merged_columns[new_col].combine_first(converted_col)
            else:
                merged_columns[new_col] = converted_col

        new_df = pd.DataFrame(merged_columns)

        new_filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if new_filepath:
            new_df.to_csv(new_filepath, index=False, decimal=",")
            messagebox.showinfo("Success", "CSV file saved successfully!")

    def convert_column(self, col, col_type):
        if col_type == "Texto":
            return col.astype(str)
        elif col_type == "Numero negativo":
            valid_col = col.apply(lambda x: self.is_valid_to_convert_to_number(x) if pd.notna(x) else True)
            if valid_col.all():
                return col.apply(lambda x: float(str(x).replace(".", "").replace(",", ".")) * -1 if pd.notna(x) else x)
            else:
                return None
        elif col_type == "Numero positivo":
            valid_col = col.apply(lambda x: self.is_valid_to_convert_to_number(x) if pd.notna(x) else True)
            if valid_col.all():
                return col.apply(lambda x: float(str(x).replace(".", "").replace(",", ".")) if pd.notna(x) else x)
            else:
                return None
            
    def is_valid_to_convert_to_number(self, value):
        try:
            float(str(value).replace(".", "").replace(",", "."))
            return True
        except ValueError:
            return False
        
        
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVRemapperApp(root)
    root.mainloop()
