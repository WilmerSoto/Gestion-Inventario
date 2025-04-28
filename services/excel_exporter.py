import pandas as pd
from tkinter import filedialog
import xlsxwriter
from ttkbootstrap.dialogs import Messagebox


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
                
        df_transacciones = pd.DataFrame(self.transacciones).drop(columns=["id"])
        df_ingresos = pd.DataFrame(array_ingresos).drop(columns=["id"])
        df_egresos = pd.DataFrame(array_egresos).drop(columns=["id"])
        
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
    