# models/ usuario 

from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# Modelo para a tabela de usuários
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    perfil = Column(String)
    ativo = Column(Boolean, nullable=False, default=True)

#atualizado pois foi feito uns ajustes no código, como a adição de novos campos e a modificação de alguns tipos de dados.