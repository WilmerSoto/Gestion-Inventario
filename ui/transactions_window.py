import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview

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