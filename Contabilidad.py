import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
import json
import os

class IngresosEgresos:
    def __init__(self,  master):
        self.master = master
        master.title("Gestion de Transacciones")
        master.geometry("320x350")
        master.resizable(False, False)
        
        self.path = "~/Documents/Gestion Ingresos-Egresos/transacciones.json"
        self.transacciones = []
        self.total_transacciones = 0.0
        self.cargar_transacciones()
                
        ttk.Label(master, text="Fecha (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_transaccion = ttk.DateEntry()
        self.date_transaccion.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
                
        ttk.Label(master, text="Concepto").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_concepto = ttk.Entry(master)
        self.input_concepto.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Ingresos").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.input_ingreso = ttk.Entry(master)
        self.input_ingreso.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(master, text="Egresos").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.input_egreso = ttk.Entry(master)
        self.input_egreso.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Saldo").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.var_total = ttk.StringVar(value="0.0")
        ttk.Label(master, textvariable=self.var_total).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.actualizar_label_total()
        
        self.btn_añadir = ttk.Button(master, text="Añadir transaccion", command=self.añadir_transaccion)
        self.btn_añadir.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        self.btn_revisarLista = ttk.Button(master, text="Revisar lista de transacciones", command=self.abrir_ventana_transacciones)
        self.btn_revisarLista.grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        self.btn_generarExcel= ttk.Button(master, text="Generar excel", command=self)
        self.btn_generarExcel.grid(row=7, column=0, columnspan=2, padx=5, pady=10)
    
    def añadir_transaccion(self):
        fecha = self.date_transaccion.entry.get()
        concepto = self.input_concepto.get()
        ingreso = self.input_ingreso.get()
        egreso = self.input_egreso.get()
        
        try:
            ingreso_monto = float(ingreso) if ingreso else 0.0
            egreso_monto = float(egreso) if egreso else 0.0
        except ValueError:
            Messagebox.show_error("Los valores de ingreso y/o egresos debe ser numericos","ERROR")
            return
        
        if ingreso_monto == 0 and egreso_monto == 0:
            Messagebox.show_error("Deber haber un valor de ingreso o egreso como minimo","ERROR")
            return
        
        if ingreso_monto > 0:
            self.transacciones.append(self.crear_transaccion(fecha, concepto, "ingreso", ingreso_monto))
        
        if egreso_monto > 0:
            self.transacciones.append(self.crear_transaccion(fecha, concepto, "egreso", egreso_monto))

        Messagebox.show_info("Transaccion(es) añadidas exitosamente","EXITO")
        
        self.calcular_total()
        self.actualizar_label_total()
        self.guardar_transacciones()
        
        today = str(datetime.now().date())
        self.date_transaccion.entry.delete(0, ttk.END)
        self.date_transaccion.entry.insert(ttk.END, today)
        self.input_concepto.delete(0, ttk.END)
        self.input_ingreso.delete(0, ttk.END)
        self.input_egreso.delete(0, ttk.END)
        
    def crear_transaccion(self, fecha, concepto, tipo, monto):
        return {
            "fecha": fecha,
            "concepto": concepto,
            "tipo": tipo,
            "monto": monto
        }
        
    def actualizar_label_total(self):
        self.var_total.set(f"{self.total_transacciones:.1f}")

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
        
        self.total_transacciones = 0.0
        for transaccion in self.transacciones:
            if transaccion["tipo"] == "ingreso":
                self.total_transacciones += transaccion["monto"]
            elif transaccion["tipo"] == "egreso":
                self.total_transacciones -= transaccion["monto"]
    
    def abrir_ventana_transacciones(self):
        VentanaTransacciones(self.master, self.transacciones)
        
class VentanaTransacciones:
    def __init__(self, master, transacciones):
        self.top = ttk.Toplevel(master)
        self.top.geometry("900x400")
        self.top.resizable(False, False)
        self.top.title("Lista de Transacciones")
        self.transacciones = transacciones
        
        self.tree = ttk.Treeview(self.top, columns=("Fecha", "Concepto", "Tipo", "Monto", "Saldo"), show="headings")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Concepto", text="Concepto")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Monto", text="Monto")
        self.tree.heading("Saldo", text="Saldo")

        for transaccion in self.transacciones:
            self.tree.insert("", "end", values=(transaccion["fecha"], transaccion["concepto"], transaccion["tipo"], transaccion["monto"]))
     
        self.tree.pack(expand=True, fill="both")
        
if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = IngresosEgresos(root)
    root.mainloop()