# schemas/movimentacao

from pydantic import BaseModel
from datetime import datetime

class MovimentacaoCreate(BaseModel):
    medicamento_id: int
    quantidade: int
    tipo: str
    usuario_id: int | None = None
    origem: str | None = None

class MovimentacaoOut(MovimentacaoCreate):
    id: int
    data: datetime
    responsavel: str | None = None

    class Config:
        from_attributes = True