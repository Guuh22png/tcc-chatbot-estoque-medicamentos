#routers/medicamentos
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.medicamento import Medicamento
from schemas.medicamentos import MedicamentoCreate, MedicamentoOut

router = APIRouter()

# Constants for stock and validity alerts
LIMITE_ESTOQUE_BAIXO = 30
DIAS_ALERTA_VALIDADE = 30

# Funções para lidar com os endpoints de medicamentos
@router.get("/", response_model=list[MedicamentoOut])
def listar_medicamentos(db: Session = Depends(get_db)):
    return db.query(Medicamento).all()

# Função para lidar com o endpoint de alerta de estoque baixo
@router.get("/alerta-estoque-baixo", response_model=list[MedicamentoOut])
def alerta_estoque_baixo(db: Session = Depends(get_db)):
    return db.query(Medicamento).filter(Medicamento.estoque_atual < LIMITE_ESTOQUE_BAIXO).all()

# Função para lidar com o endpoint de alerta de validade
@router.get("/alerta-validade", response_model=list[MedicamentoOut])
def alerta_validade(db: Session = Depends(get_db)):
    limite = date.today() + timedelta(days=DIAS_ALERTA_VALIDADE)
    return (db.query(Medicamento)
            .filter(Medicamento.validade.isnot(None), Medicamento.validade <= limite)
            .order_by(Medicamento.validade)
            .all())

#  Função para buscar um medicamento específico
@router.get("/{medicamento_id}", response_model=MedicamentoOut)
def buscar_medicamento(medicamento_id: int, db: Session = Depends(get_db)):
    medicamento = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return medicamento

# Função para criar um novo medicamento
@router.post("/", response_model=MedicamentoOut)
def criar_medicamento(medicamento: MedicamentoCreate, db: Session = Depends(get_db)):
    novo = Medicamento(**medicamento.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

# Função para deletar um medicamento
@router.delete("/{medicamento_id}")
def deletar_medicamento(medicamento_id: int, db: Session = Depends(get_db)):
    medicamento = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    db.delete(medicamento)
    db.commit()
    return {"mensagem": f"Medicamento {medicamento_id} removido com sucesso"}

# Função para editar um medicamento
@router.put("/{medicamento_id}", response_model=MedicamentoOut)
def editar_medicamento(medicamento_id: int, dados: MedicamentoCreate, db: Session = Depends(get_db)):
    med = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    for campo, valor in dados.dict().items():
        setattr(med, campo, valor)
    db.commit()
    db.refresh(med)
    return med