from dataclasses import dataclass
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

@dataclass         
class TransaccionFormulario:
    fecha: str
    concepto_ingreso: str
    monto_ingreso: int
    concepto_egreso: str
    monto_egreso: int
    
    def __post_init__(self):
        if self.monto_ingreso == 0 and self.monto_egreso == 0:
            raise ValueError("Debe haber un valor de ingreso o egreso como mínimo")
        
        if self.monto_ingreso < 0 or self.monto_egreso < 0:
            raise ValueError("Los valores de ingreso y/o egreso deben ser positivos")
class VentanaPrincipal:
    def __init__(self,  master, repo_transacciones):
        self.master = master
        master.title("Gestion de Transacciones")
        ttk.Style().configure("TLabel", font=("Open Sans bold", 12))
        ttk.Style().configure("TButton", font=("Open Sans bold", 10))

        master.geometry("385x410")
        master.resizable(False, False)
        
        self.repo_transacciones = repo_transacciones
        excel = ExportadorExcel(self.repo_transacciones)
        self.total_transacciones = 0
        total = self.repo_transacciones.calcular_total()
                
        ttk.Label(master, text="Fecha (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_transaccion = ttk.DateEntry(firstweekday=0)
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
        self.actualizar_label_total(total)
        
        self.btn_añadir = ttk.Button(master, text="Añadir transaccion", command=self.añadir_transaccion)
        self.btn_añadir.grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        self.btn_revisar_lista = ttk.Button(master, text="Revisar lista de transacciones", command=self.abrir_ventana_transacciones)
        self.btn_revisar_lista.grid(row=7, column=0, columnspan=2, padx=5, pady=10)
        
        self.btn_generar_excel= ttk.Button(master, text="Generar excel", command=excel.generar_excel)
        self.btn_generar_excel.grid(row=8, column=0, columnspan=2, padx=5, pady=10)
    
    def añadir_transaccion(self):
        try:
            transaccion = TransaccionFormulario(
                fecha=datetime.strptime(self.date_transaccion.entry.get(), "%d/%m/%Y").strftime("%d/%m/%Y"),
                concepto_ingreso=self.input_concepto_ingreso.get(),
                monto_ingreso=int(self.input_ingreso.get() or 0),
                concepto_egreso=self.input_concepto_egreso.get(),
                monto_egreso=int(self.input_egreso.get() or 0)
            )
        except ValueError as e:
            Messagebox.show_error(f"Error: {e}","ERROR")
            return
            
        self.repo_transacciones.añadir_transaccion(transaccion)
        
        total = self.repo_transacciones.calcular_total()
        self.actualizar_label_total(total)
        
        today = str(datetime.now().date())
        self.date_transaccion.entry.delete(0, ttk.END)
        self.date_transaccion.entry.insert(ttk.END, today)
        self.input_concepto_ingreso.delete(0, ttk.END)
        self.input_ingreso.delete(0, ttk.END)
        self.input_concepto_egreso.delete(0, ttk.END)
        self.input_egreso.delete(0, ttk.END)
           
    def actualizar_label_total(self, total):
        self.var_total.set(f"$ {total:,.0f}")
    
    def abrir_ventana_transacciones(self):
        VentanaTransacciones(self.repo_transacciones)
        
class VentanaTransacciones:
    def __init__(self, repo_transacciones):
        self.top = ttk.Toplevel(title="Lista de Transacciones")
        self.top.geometry("804x450")
        self.top.resizable(False, False)
        self.repo_transacciones = repo_transacciones
        
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
        
        self.coldata = [{"text": "id", "width": 0},
                   {"text": "Fecha", "width": 100}, 
                   {"text": "Concepto", "width": 300, "anchor": CENTER}, 
                   {"text": "Tipo", "width": 100, "anchor": CENTER}, 
                   {"text": "Monto", "width": 150}, 
                   {"text": "Saldo", "width": 150}
                   ]
        self.coldata_no_saldo = self.coldata.copy()[:-1]        
        self.lista_combinada()
        
    def borrar_transacciones(self):
        items_seleccionados = []
        if hasattr(self, "table_combinada"):
            items_seleccionados.extend(self.table_combinada.get_rows(selected=True))
        elif hasattr(self, "table") and hasattr(self, "table2"):
            items_seleccionados.extend(self.table.get_rows(selected=True))
            items_seleccionados.extend(self.table2.get_rows(selected=True))
        else:
            items_seleccionados = []
        
        if not items_seleccionados:
            Messagebox.show_error("No se selecciono ninguna transaccion","ERROR")
            return
        else:
            self.repo_transacciones.borrar_transaccion(items_seleccionados)
        
        if hasattr(self, "table_combinada"):
            self.lista_combinada()
        elif hasattr(self, "table") and hasattr(self, "table2"):
            self.separar_por_tipos()
    
    def lista_combinada(self):
        self.top.geometry("804x450")
        transacciones = self.repo_transacciones.obtener_transacciones()
        self.destruir_tablas()
         
        self.table_combinada = Tableview(self.top, coldata=self.coldata, searchable=True, paginated=True)
        
        self.table_combinada.get_column(0).hide()
                
        total = 0
        for transaccion in reversed(transacciones):
            if transaccion["tipo"] == "Ingreso":
                total += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                total -= transaccion["monto"]
                
            self.table_combinada.insert_row(END, values=[transaccion["id"], transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"]), "$ {:,.0f}".format(total)])
            
        self.table_combinada.pack(side=LEFT, expand=True, fill=BOTH)
        self.table_combinada.load_table_data()

    def separar_por_tipos(self):
        self.top.geometry("1308x450")
        transacciones = self.repo_transacciones.obtener_transacciones()
        self.destruir_tablas()
        
        self.table = Tableview(self.top, coldata=self.coldata_no_saldo, searchable=True, paginated=True)
        self.table2 = Tableview(self.top, coldata=self.coldata_no_saldo, searchable=True, paginated=True)
        
        self.table.get_column(0).hide()
        self.table2.get_column(0).hide()
        
        for transaccion in reversed(transacciones):
            if transaccion["tipo"] == "Ingreso":
                self.table.insert_row(END, values=[transaccion["id"], transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"])])
            elif transaccion["tipo"] == "Egreso":
                self.table2.insert_row(END, values=[transaccion["id"], transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"])])
                
        self.table.pack(side=LEFT, expand=True, fill=BOTH)
        self.table2.pack(side=RIGHT, expand=True, fill=BOTH)

        self.table.load_table_data()
        self.table2.load_table_data()
    
    def destruir_tablas(self):
        for tabla in ["table_combinada", "table", "table2"]:
            if hasattr(self, tabla):
                getattr(self, tabla).destroy()
                delattr(self, tabla)
                
class RepositorioTransacciones:
    def __init__(self, path):
        self.path = path
        self.transacciones = self.cargar_transacciones()
        self.siguiente_id = self.obtener_siguiente_id()
    
    def obtener_transacciones(self):
        return self.transacciones
    
    def guardar_transacciones(self, transacciones):
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
                json.dump(transacciones, f, indent=4)
                self.transacciones = transacciones
        except Exception as e:
            Messagebox().show_error(f"No se pudo guardar las transacciones: {e}","ERROR")

    def cargar_transacciones(self):
        expanded_path =  os.path.expanduser(self.path)
        transacciones = []
        try:
            if os.path.exists(expanded_path):
                with open(expanded_path, "r") as f:
                    transacciones = json.load(f)
            else:
                transacciones = []
        except Exception as e:
            Messagebox.show_error(f"No se pudo cargar las transacciones: {e}","ERROR")
            transacciones = []
        
        transacciones.sort(key=lambda x: datetime.strptime(x["fecha"], '%d/%m/%Y'))
        return transacciones

    def obtener_siguiente_id(self):
        return max((transaccion["id"] for transaccion in self.transacciones), default=0) + 1
    
    def añadir_transaccion(self, transaccion: TransaccionFormulario):
        transaccion_ingreso = self.crear_transaccion(self.siguiente_id, transaccion.fecha, transaccion.concepto_ingreso, "Ingreso", transaccion.monto_ingreso)
        
        if transaccion_ingreso:
            self.transacciones.append(transaccion_ingreso)
            self.siguiente_id += 1
            
        transaccion_egreso = self.crear_transaccion(self.siguiente_id, transaccion.fecha, transaccion.concepto_egreso, "Egreso", transaccion.monto_egreso)
        
        if transaccion_egreso:
            self.transacciones.append(transaccion_egreso)
            self.siguiente_id += 1

        self.guardar_transacciones(self.transacciones)
        Messagebox.show_info("Transaccion(es) añadidas exitosamente","EXITO")
    
    def borrar_transaccion(self, items_seleccionados):
        try:
            for item in items_seleccionados:
                for i, transaccion in enumerate(self.transacciones):
                    if transaccion["id"] == item.values[0]:
                        del self.transacciones[i]
                        break
            self.guardar_transacciones(self.transacciones)
        except Exception as e:
            Messagebox.show_error(f"No se pudo borrar la transaccion: {e}","ERROR")
            return
        
    def crear_transaccion(self, siguiente_id,fecha, concepto, tipo, monto):
        if monto > 0:
            return {
                "id": siguiente_id,
                "fecha": fecha,
                "concepto": concepto,
                "tipo": tipo,
                "monto": monto
            }
        else:
            return None
    
    def calcular_total(self):        
        total_transacciones = 0
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "Ingreso":
                total_transacciones += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                total_transacciones -= transaccion["monto"]

        return total_transacciones

class ExportadorExcel:
    def __init__(self, repo_transacciones):
        self.repo_transacciones = repo_transacciones
        self.transacciones = self.repo_transacciones.obtener_transacciones()
           
    def generar_excel(self):
        try:                
            df_transacciones, df_ingresos, df_egresos = self.crear_dataframes()            
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Guardar archivo de excel") 
            
            if file_path:
                writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
                df_transacciones.to_excel(writer, index=False, sheet_name="Transacciones")
                df_ingresos.to_excel(writer, index=False, sheet_name="Ingresos")
                df_egresos.to_excel(writer, index=False, sheet_name="Egresos")
                
                workbook = writer.book
                worksheet_transacciones = writer.sheets["Transacciones"]
                worksheet_ingresos = writer.sheets["Ingresos"]
                worksheet_egresos = writer.sheets["Egresos"]
                
                self.formato_hojas(workbook, worksheet_transacciones, worksheet_ingresos, worksheet_egresos, df_transacciones, df_ingresos, df_egresos)
                      
                writer.close()
                Messagebox.show_info("Archivo excel generado exitosamente","EXITO")
                return
            else:
                Messagebox.show_error("Se cancelo el guardado del archivo excel","ERROR")
                return
        except Exception as e:
            Messagebox.show_error(f"No se pudo generar el archivo excel: {e}","ERROR")
            return
    
    def formato_hojas(self, workbook, worksheet_transacciones, worksheet_ingresos, worksheet_egresos, df_transacciones, df_ingresos, df_egresos):     
        for worksheet in [worksheet_transacciones, worksheet_ingresos, worksheet_egresos]:
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, 15, cell_format=workbook.add_format({"num_format": "dd/mm/yyyy", "align": "center"}))
            worksheet.set_column(2, 2, 40)
            worksheet.set_column(4, 5, 15, cell_format=workbook.add_format({"num_format": "$#,##0"}))
                                
        header_format = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "bg_color": "#D7E4BC", "font_color": "#000000", "border": 1})                
                
        for df, worksheet in zip([df_transacciones, df_ingresos, df_egresos], [worksheet_transacciones, worksheet_ingresos, worksheet_egresos]):
            for col_num, value in enumerate(df.columns.values):                        
                worksheet.write(0, col_num, value, header_format)
        
        index_ingreso = 2
        index_egreso = 2
        
        for i, transaccion in enumerate(self.transacciones):
            if transaccion["tipo"] == "Ingreso":
                worksheet_transacciones.write_formula(f"A{i+2}", f"=Ingresos!A{index_ingreso}")
                index_ingreso += 1
            elif transaccion["tipo"] == "Egreso":
                worksheet_transacciones.write_formula(f"A{i+2}", f"=Egresos!A{index_egreso}")
                index_egreso += 1
        
    def crear_dataframes(self):
        array_ingresos = []
        array_egresos = []
        
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "Ingreso":
                array_ingresos.append(transaccion)
            elif transaccion["tipo"] == "Egreso":
                array_egresos.append(transaccion)
                
        df_transacciones = pd.DataFrame(self.transacciones)
        df_ingresos = pd.DataFrame(array_ingresos)
        df_egresos = pd.DataFrame(array_egresos)
        
        for df in [df_transacciones, df_ingresos, df_egresos]:
            df.rename(columns={"fecha": "Fecha", "concepto": "Concepto", "tipo": "Tipo", "monto": "Monto"}, inplace=True)
            df.insert(0, "Codigo","")

        total = 0
        array_total = []
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "Ingreso":
                total += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                total -= transaccion["monto"]
            array_total.append(total)
            
        df_transacciones["Saldo"] = array_total
        return df_transacciones, df_ingresos, df_egresos
    
if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    
    path = "~/Documents/Gestion Ingresos-Egresos/transacciones.json"
    repo_transacciones = RepositorioTransacciones(path)
    
    app = VentanaPrincipal(root, repo_transacciones)
    root.mainloop()