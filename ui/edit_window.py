import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

class VentanaEditar:
    def __init__(self, transaccion_a_editar, repo_transacciones, actualizar_label_total):
        self.top = ttk.Toplevel(title="Editar Transaccion")
        ttk.Style().configure("TLabel", font=("Open Sans bold", 12))
        ttk.Style().configure("TButton", font=("Open Sans bold", 10))
        self.top.geometry("385x180")
        self.top.resizable(True, True)
        
        self.repo_transacciones = repo_transacciones
        self.actualizar_label_total = actualizar_label_total
        self.transaccion_a_editar = transaccion_a_editar

        ttk.Style().configure("TLabel", font=("Open Sans bold", 12))
        ttk.Style().configure("TButton", font=("Open Sans bold", 10))

        ttk.Label(self.top, text="Fecha (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_transaccion = ttk.DateEntry(master=self.top, firstweekday=0)
        self.date_transaccion.entry.configure(font=("Open Sans bold", 10))
        self.date_transaccion.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
                
        ttk.Label(self.top, text="Tipo de transaccion").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combobox_transaccion = ttk.Combobox(self.top, values=["Ingreso", "Egreso"], state="readonly")
        self.combobox_transaccion.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        if transaccion_a_editar[3] == "Ingreso":
            self.combobox_transaccion.set("Ingreso")
        else:
            self.combobox_transaccion.set("Egreso")        
        
        ttk.Label(self.top, text="Monto").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.input_monto = ttk.Entry(self.top, font=("Open Sans", 10))
        self.input_monto.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.btn_editar = ttk.Button(self.top, text="Editar transaccion", command=self.editar_transaccion)
        self.btn_editar.grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
    def editar_transaccion(self):
        pass