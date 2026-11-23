#models / movimentacao

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

#atualizado pois foi feito uns ajustes no código, como a adição de novos campos e a modificação de alguns tipos de dados.
class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    medicamento_id = Column(Integer, ForeignKey("medicamentos.id"))
    quantidade = Column(Integer)
    tipo = Column(String)
    data = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    origem = Column(String, nullable=True)

    medicamento = relationship("Medicamento")
    usuario = relationship("Usuario")

    @property
    def responsavel(self):
        return self.usuario.nome if self.usuario else (self.origem or "—")