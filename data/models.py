from dataclasses import dataclass

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
        
        if self.monto_ingreso > 0 and self.concepto_ingreso.strip() == "":
            raise ValueError("El concepto de ingreso no puede estar vacío")

        if self.monto_egreso > 0 and self.concepto_egreso.strip() == "":
            raise ValueError("El concepto de egreso no puede estar vacío")

@dataclass
class TransaccionEditar:
    fecha: str
    concepto: str
    tipo: str
    monto: int
    
    def __post_init__(self):
        if self.monto < 0:
            raise ValueError("El valor de la transaccion debe ser positivo")
        
        if self.monto == 0:
            raise ValueError("Debe haber un valor de monto como mínimo")