from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from data.models import TransaccionEditar, TransaccionFormulario

class VentanaEditar:
    def __init__(self, transaccion_a_editar, repo_transacciones, actualizar_label_total, recargar_tablas):
        self.top = ttk.Toplevel(title="Editar Transaccion")
        ttk.Style().configure("TLabel", font=("Open Sans bold", 12))
        ttk.Style().configure("TButton", font=("Open Sans bold", 10))
        self.top.geometry("385x220")
        self.top.resizable(True, True)
        
        self.repo_transacciones = repo_transacciones
        self.actualizar_label_total = actualizar_label_total
        self.recargar_tablas = recargar_tablas
        self.transaccion_a_editar = transaccion_a_editar

        ttk.Style().configure("TLabel", font=("Open Sans bold", 12))
        ttk.Style().configure("TButton", font=("Open Sans bold", 10))

        ttk.Label(self.top, text="Fecha (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        datetime_inicial = datetime.strptime(self.transaccion_a_editar[1], "%d/%m/%Y")
        self.date_transaccion = ttk.DateEntry(master=self.top, firstweekday=0, startdate=datetime_inicial)
        self.date_transaccion.entry.configure(font=("Open Sans bold", 10))
        self.date_transaccion.entry.bind("<Key>", lambda e: "break")
        self.date_transaccion.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.top, text="Concepto:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.var_input_concepto = ttk.StringVar()
        self.input_concepto = ttk.Entry(self.top, font=("Open Sans", 10), textvariable=self.var_input_concepto)
        self.input_concepto.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
                
        ttk.Label(self.top, text="Tipo de transaccion").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.var_combobox = ttk.StringVar()
        self.combobox_transaccion = ttk.Combobox(self.top, values=["Ingreso", "Egreso"], state="readonly")
        self.combobox_transaccion.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.top, text="Monto").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.var_monto = ttk.StringVar()
        self.input_monto = ttk.Entry(self.top, font=("Open Sans", 10), textvariable=self.var_monto)
        self.input_monto.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        self.btn_editar = ttk.Button(self.top, text="Editar transaccion", command=self.editar_transaccion)
        self.btn_editar.grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
        self.valores_por_defecto()
        
    def editar_transaccion(self):
        try:
            transaccion_editada = TransaccionEditar(
                fecha=datetime.strptime(self.date_transaccion.entry.get(), "%d/%m/%Y").strftime("%d/%m/%Y"),
                concepto=self.var_input_concepto.get(),
                tipo=self.combobox_transaccion.get(),
                monto=int(self.var_monto.get() or 0) 
            )
        except ValueError as e:
            Messagebox.show_error(f"Error: {e}", "ERROR")
            return
        
        self.repo_transacciones.editar_transaccion(self.transaccion_a_editar, transaccion_editada)
        self.actualizar_label_total(self.repo_transacciones.calcular_total())
        self.recargar_tablas()
        self.top.destroy()
    
    def valores_por_defecto(self):
        if self.transaccion_a_editar[3] == "Ingreso":
            self.combobox_transaccion.set("Ingreso")
        else:
            self.combobox_transaccion.set("Egreso")

        self.var_input_concepto.set(self.transaccion_a_editar[2])
        self.var_monto.set(self.transaccion_a_editar[4].replace("$ ", "").replace(",","").strip())
        