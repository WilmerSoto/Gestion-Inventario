import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from tkinter import filedialog
import xlsxwriter
from datetime import datetime
import json
import os
import pandas as pd

class IngresosEgresos:
    def __init__(self,  master):
        self.master = master
        master.title("Gestion de Transacciones")
        ttk.Style().configure("TLabel", font=("Open Sans bold", 12))
        ttk.Style().configure("TButton", font=("Open Sans bold", 10))

        master.geometry("385x410")
        master.resizable(False, False)
        
        self.path = "~/Documents/Gestion Ingresos-Egresos/transacciones.json"
        self.transacciones = []
        self.total_transacciones = 0
        self.cargar_transacciones()
                
        ttk.Label(master, text="Fecha (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_transaccion = ttk.DateEntry()
        self.date_transaccion.entry.configure(font=("Open Sans bold", 10))
        self.date_transaccion.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
                
        ttk.Label(master, text="Concepto Ingreso").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_concepto_ingreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_concepto_ingreso.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Ingresos").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.input_ingreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_ingreso.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Concepto Egreso").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.input_concepto_egreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_concepto_egreso.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(master, text="Egresos").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.input_egreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_egreso.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Saldo").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.var_total = ttk.StringVar(value="$ 0")
        ttk.Label(master, textvariable=self.var_total).grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.actualizar_label_total()
        
        self.btn_añadir = ttk.Button(master, text="Añadir transaccion", command=self.añadir_transaccion)
        self.btn_añadir.grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        self.btn_revisar_lista = ttk.Button(master, text="Revisar lista de transacciones", command=self.abrir_ventana_transacciones)
        self.btn_revisar_lista.grid(row=7, column=0, columnspan=2, padx=5, pady=10)
        
        self.btn_generar_excel= ttk.Button(master, text="Generar excel", command=self.generar_excel)
        self.btn_generar_excel.grid(row=8, column=0, columnspan=2, padx=5, pady=10)
    
    def añadir_transaccion(self):
        fecha = self.date_transaccion.entry.get()
        concepto_ingreso = self.input_concepto_ingreso.get()
        ingreso = self.input_ingreso.get()
        concepto_egreso = self.input_concepto_egreso.get()
        egreso = self.input_egreso.get()
        
        try:
            ingreso_monto = int(ingreso) if ingreso else 0
            egreso_monto = int(egreso) if egreso else 0
        except ValueError:
            Messagebox.show_error("Los valores de ingreso y/o egresos debe ser numericos","ERROR")
            return
        
        if ingreso_monto == 0 and egreso_monto == 0:
            Messagebox.show_error("Deber haber un valor de ingreso o egreso como minimo","ERROR")
            return
        
        if ingreso_monto > 0:
            self.transacciones.append(self.crear_transaccion(fecha, concepto_ingreso, "Ingreso", ingreso_monto))
        
        if egreso_monto > 0:
            self.transacciones.append(self.crear_transaccion(fecha, concepto_egreso, "Egreso", egreso_monto))

        Messagebox.show_info("Transaccion(es) añadidas exitosamente","EXITO")
        
        self.calcular_total()
        self.actualizar_label_total()
        self.guardar_transacciones()
        
        today = str(datetime.now().date())
        self.date_transaccion.entry.delete(0, ttk.END)
        self.date_transaccion.entry.insert(ttk.END, today)
        self.input_concepto_ingreso.delete(0, ttk.END)
        self.input_ingreso.delete(0, ttk.END)
        self.input_concepto_egreso.delete(0, ttk.END)
        self.input_egreso.delete(0, ttk.END)
        
    def crear_transaccion(self, fecha, concepto, tipo, monto):
        return {
            "fecha": fecha,
            "concepto": concepto,
            "tipo": tipo,
            "monto": monto
        }
        
    def actualizar_label_total(self):
        self.var_total.set(f"$ {self.total_transacciones:,.0f}")

    def guardar_transacciones(self):
        expanded_path = os.path.expanduser(self.path)
        directory = os.path.dirname(expanded_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                Messagebox().show_error(f"No se pudo crear el directorio: {e}","ERROR")
                return
        
        try:
            with open(expanded_path, "w") as f:
                json.dump(self.transacciones, f, indent=4)
        except Exception as e:
            Messagebox().show_error(f"No se pudo guardar las transacciones: {e}","ERROR")

    def cargar_transacciones(self):
        expanded_path =  os.path.expanduser(self.path)
        try:
            if os.path.exists(expanded_path):
                with open(expanded_path, "r") as f:
                    self.transacciones = json.load(f)
            else:
                self.transacciones = []
        except Exception as e:
            Messagebox.show_error(f"No se pudo cargar las transacciones: {e}","ERROR")
            self.transacciones = []
        
        self.calcular_total()
        
    def calcular_total(self):
        self.transacciones.sort(key=lambda x: datetime.strptime(x["fecha"], '%d/%m/%Y'))
        
        self.total_transacciones = 0
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "Ingreso":
                self.total_transacciones += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                self.total_transacciones -= transaccion["monto"]
    
    def abrir_ventana_transacciones(self):
        VentanaTransacciones(self.master, self.transacciones)
    
    def generar_excel(self):
        try:
            df = pd.DataFrame(self.transacciones)
            df.rename(columns={"fecha": "Fecha", "concepto": "Concepto", "tipo": "Tipo", "monto": "Monto"}, inplace=True)
            
            total = 0
            array_total = []
            for transaccion in self.transacciones:
                if transaccion["tipo"] == "Ingreso":
                    total += transaccion["monto"]
                elif transaccion["tipo"] == "Egreso":
                    total -= transaccion["monto"]
                array_total.append(total)
                
            df["Saldo"] = array_total
            df.insert(0, "Codigo","")
            
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Guardar archivo de excel") 
            
            if file_path:
                writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
                df.to_excel(writer, index=False, sheet_name="Transacciones")
                
                workbook = writer.book
                worksheet = writer.sheets["Transacciones"]
                worksheet.set_column(0, 0, 10)
                worksheet.set_column(1, 1, 15, cell_format=workbook.add_format({"num_format": "dd/mm/yyyy", "align": "center"}))
                worksheet.set_column(2, 2, 40)
                worksheet.set_column(4, 5, 15, cell_format=workbook.add_format({"num_format": "$#,##0"}))
                
                header_format = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "bg_color": "#D7E4BC", "font_color": "#000000", "border": 1})                
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                        
                writer.close()
                Messagebox.show_info("Archivo excel generado exitosamente","EXITO")
                return
            else:
                Messagebox.show_error("Se cancelo el guardado del archivo excel","ERROR")
                return
        except Exception as e:
            Messagebox.show_error(f"No se pudo generar el archivo excel: {e}","ERROR")
            return
class VentanaTransacciones:
    def __init__(self, master, transacciones):
        self.top = ttk.Toplevel(title="Lista de Transacciones")
        self.top.geometry("804x450")
        self.top.resizable(False, False)
        self.transacciones = transacciones
        
        ttk.Style().configure("Treeview.Heading", font=("Roboto bold", 14))
        ttk.Style().configure("Treeview", font=("Open Sans", 11))
        ttk.Style().map("Treeview", rowheight=[("!disabled", 22)]) 
        
        self.frame_btn = ttk.Frame(self.top)
        self.frame_btn.pack(side=BOTTOM, anchor=W)
        
        self.btn_separar = ttk.Button(self.frame_btn, text="Separar por tipo", command=self.separar_por_tipos)
        self.btn_separar.pack(side=LEFT, padx=10, pady=10)
        
        self.btn_ambos = ttk.Button(self.frame_btn, text="Mostrar lista combinada", command=self.lista_combinada)
        self.btn_ambos.pack(side=LEFT, padx=10, pady=10)
        
        self.btn_borrar = ttk.Button(self.frame_btn, text="Borrar fila", command=self.borrar_transacciones)
        self.btn_borrar.pack(side=LEFT, padx=10, pady=10)
        
        self.coldata = [{"text": "Fecha", "width": 100}, 
                   {"text": "Concepto", "width": 300, "anchor": CENTER}, 
                   {"text": "Tipo", "width": 100, "anchor": CENTER}, 
                   {"text": "Monto", "width": 150}, 
                   {"text": "Saldo", "width": 150}
                   ]
        self.coldata_no_saldo = self.coldata.copy()[:-1]        
        self.lista_combinada()
        
    # CORREGIR EL PROBLEMA DE QUE NO SE PUEDE BORRAR LA FILA SELECCIONADA. Tener en cuenta las tres tablas
    # y que se pueda borrar la fila seleccionada de la tabla combinada o de las tablas separadas.
    # TO-DO: Añadir tipos de gastos y ingresos
    def borrar_transacciones(self):
        try:
            selected_items = self.table_combinada.selection_get()
            print(selected_items)
        except Exception as e:
            Messagebox.show_error(f"No se pudo borrar la transaccion: {e}","ERROR")
            return
    
    def lista_combinada(self):
        self.top.geometry("804x450")
        
        if hasattr(self, "table_combinada"):
            self.table_combinada.destroy()
        if hasattr(self, "table"):
            self.table.destroy()
        if hasattr(self, "table2"):
            self.table2.destroy()
            
        self.table_combinada = Tableview(self.top, coldata=self.coldata, searchable=True, paginated=True)
        self.table_combinada.bind("<Double-1>", lambda event: self.separar_por_tipos())
                
        total = 0
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "Ingreso":
                total += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                total -= transaccion["monto"]
            self.table_combinada.insert_row(END, values=[transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"]), "$ {:,.0f}".format(total)])
            
        self.table_combinada.pack(side=LEFT, expand=True, fill=BOTH)
        self.table_combinada.load_table_data()

    def separar_por_tipos(self):
        self.top.geometry("1308x450")
        
        if hasattr(self, "table_combinada"):
            self.table_combinada.destroy()
        if hasattr(self, "table"):
            self.table.destroy()
        if hasattr(self, "table2"):
            self.table2.destroy()
        
        self.table = Tableview(self.top, coldata=self.coldata_no_saldo, searchable=True, paginated=True)
        self.table2 = Tableview(self.top, coldata=self.coldata_no_saldo, searchable=True, paginated=True)
        
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "Ingreso":
                self.table.insert_row(END, values=[transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"])])
            elif transaccion["tipo"] == "Egreso":
                self.table2.insert_row(END, values=[transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"])])
                
        self.table.pack(side=LEFT, expand=True, fill=BOTH)
        self.table2.pack(side=RIGHT, expand=True, fill=BOTH)

        self.table.load_table_data()
        self.table2.load_table_data()
        
if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = IngresosEgresos(root)
    root.mainloop()