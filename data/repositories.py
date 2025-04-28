from datetime import datetime
from data.models import TransaccionFormulario
from ttkbootstrap.dialogs import Messagebox
import os
import json

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
        transacciones_ordenadas = sorted(self.transacciones, key=lambda transaccion: datetime.strptime(transaccion["fecha"], "%d/%m/%Y"), reverse=True)
        for transaccion in transacciones_ordenadas:
            if transaccion["tipo"] == "Ingreso":
                total_transacciones += transaccion["monto"]
            elif transaccion["tipo"] == "Egreso":
                total_transacciones -= transaccion["monto"]

        return total_transacciones