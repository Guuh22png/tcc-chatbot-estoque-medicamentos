# models/ medicamentos 

from sqlalchemy import Column, Integer, String, Date
from database import Base

class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    estoque_atual = Column(Integer)
    estoque_minimo = Column(Integer)
    validade = Column(Date, nullable=True)