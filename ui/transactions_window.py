from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from .edit_window import VentanaEditar

class VentanaTransacciones:
    def __init__(self, repo_transacciones, actualizar_label_total):
        self.top = ttk.Toplevel(title="Lista de Transacciones")
        self.top.geometry("804x500")
        self.top.resizable(False, False)
        self.repo_transacciones = repo_transacciones
        self.actualizar_label_total = actualizar_label_total
        
        ttk.Style().configure("Treeview.Heading", font=("Roboto bold", 14))
        ttk.Style().configure("Treeview", font=("Open Sans", 11))
        ttk.Style().map("Treeview", rowheight=[("!disabled", 22)]) 
        
        self.frame_btn = ttk.Frame(self.top)
        self.frame_btn.pack(side=BOTTOM, anchor=W)
        
        self.btn_separar = ttk.Button(self.frame_btn, text="Separar por tipo", command=self.separar_por_tipos)
        self.btn_separar.pack(side=LEFT, padx=10, pady=10)
        
        self.btn_ambos = ttk.Button(self.frame_btn, text="Mostrar lista combinada", command=self.lista_combinada)
        self.btn_ambos.pack(side=LEFT, padx=10, pady=10)
        
        self.btn_editar = ttk.Button(self.frame_btn, text="Editar transaccion", command=self.editar_transaccion, bootstyle="info")
        self.btn_editar.pack(side=LEFT, padx=10, pady=10)
        
        self.btn_borrar = ttk.Button(self.frame_btn, text="Borrar transaccion", command=self.borrar_transacciones, bootstyle="danger")
        self.btn_borrar.pack(side=LEFT, padx=10, pady=10)
        
        self.coldata = [{"text": "id", "width": 0},
                   {"text": "Fecha", "width": 120, "anchor": CENTER}, 
                   {"text": "Concepto", "width": 350, "anchor": CENTER}, 
                   {"text": "Tipo", "width": 100, "anchor": CENTER}, 
                   {"text": "Monto", "width": 150, "anchor": CENTER}, 
                   {"text": "Saldo", "width": 150, "anchor": CENTER}
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
            exito_eliminar = self.repo_transacciones.borrar_transaccion(items_seleccionados)
            if exito_eliminar:
                Messagebox.show_info("Transaccion(es) eliminada(s) exitosamente","EXITO")
                self.actualizar_label_total(self.repo_transacciones.calcular_total())
        
        self.recargar_tablas()
    
    def editar_transaccion(self):
        item_seleccionado = []
        if hasattr(self, "table_combinada"):
            item_seleccionado = self.table_combinada.get_rows(selected=True)
        elif hasattr(self, "table") and hasattr(self, "table2"):
            item_seleccionado = self.table.get_rows(selected=True)
            if not item_seleccionado:
                item_seleccionado = self.table2.get_rows(selected=True)
        else:
            item_seleccionado = []
        
        if not item_seleccionado:
            Messagebox.show_error("No se selecciono ninguna transaccion","ERROR")
            return
        elif len(item_seleccionado) > 1:
            Messagebox.show_error("No se puede editar mas de una transaccion a la vez","ERROR")
            return
        else:   
            VentanaEditar(item_seleccionado[0].values, self.repo_transacciones, self.actualizar_label_total, self.recargar_tablas)
        
    def recargar_tablas(self):
        if hasattr(self, "table_combinada"):
            self.lista_combinada()
        elif hasattr(self, "table") and hasattr(self, "table2"):
            self.separar_por_tipos()
  
    def lista_combinada(self):
        self.top.geometry("875x520")
        transacciones = self.repo_transacciones.obtener_transacciones()
        self.destruir_tablas()
         
        self.table_combinada = Tableview(self.top, coldata=self.coldata, searchable=True, paginated=True, pagesize=15)
        
        self.table_combinada.get_column(0).hide()
                
        total = 0
        transacciones_ordenadas = sorted(transacciones, key=lambda transaccion: datetime.strptime(transaccion["fecha"], "%d/%m/%Y"))
        for transaccion in transacciones_ordenadas:
            if transaccion["tipo"] == "Ingreso":
                total += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                total -= transaccion["monto"]
                
            self.table_combinada.insert_row(END, values=[transaccion["id"], transaccion["fecha"], transaccion["concepto"], transaccion["tipo"],"$ {:,.0f}".format(transaccion["monto"]), "$ {:,.0f}".format(total)])
        
        self.table_combinada.sort_column_data(cid=1, sort=1)
        self.table_combinada.pack(side=LEFT, expand=True, fill=BOTH)
        self.table_combinada.load_table_data()

    def separar_por_tipos(self):
        self.top.geometry("1450x520")
        transacciones = self.repo_transacciones.obtener_transacciones()
        self.destruir_tablas()
        
        self.table = Tableview(self.top, coldata=self.coldata_no_saldo, searchable=True, paginated=True, pagesize=15)
        self.table2 = Tableview(self.top, coldata=self.coldata_no_saldo, searchable=True, paginated=True, pagesize=15)
        
        self.table.get_column(0).hide()
        self.table2.get_column(0).hide()
        
        transacciones_ordenadas = sorted(transacciones, key=lambda transaccion: datetime.strptime(transaccion["fecha"], "%d/%m/%Y"), reverse=True)
        for transaccion in transacciones_ordenadas:
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