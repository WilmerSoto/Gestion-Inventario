import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime

from .transactions_window import VentanaTransacciones
from data.repositories import RepositorioTransacciones
from data.models import TransaccionFormulario
from services.excel_exporter import ExportadorExcel

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
                
        ttk.Label(master, text="Concepto Ingreso:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_concepto_ingreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_concepto_ingreso.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Ingresos:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.input_ingreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_ingreso.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Concepto Egreso:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.input_concepto_egreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_concepto_egreso.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(master, text="Egresos:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.input_egreso = ttk.Entry(master, font=("Open Sans", 10))
        self.input_egreso.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(master, text="Saldo:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
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
        VentanaTransacciones(self.repo_transacciones, self.actualizar_label_total)