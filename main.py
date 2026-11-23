from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import medicamentos, usuarios, movimentacao

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Assistente de Estoque de Medicamentos")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(medicamentos.router, prefix="/medicamentos", tags=["Medicamentos"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(movimentacao.router, prefix="/movimentacoes", tags=["Movimentacoes"])
