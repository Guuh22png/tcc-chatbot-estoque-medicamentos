# shemas de medicamentos 

from datetime import date
from pydantic import BaseModel

class MedicamentoCreate(BaseModel):
    nome: str
    estoque_atual: int
    estoque_minimo: int
    validade: date | None = None

class MedicamentoOut(MedicamentoCreate):
    id: int

    class Config:
        from_attributes = True    