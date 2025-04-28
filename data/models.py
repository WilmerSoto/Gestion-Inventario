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