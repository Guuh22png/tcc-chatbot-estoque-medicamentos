from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.movimentacao import Movimentacao
from models.medicamento import Medicamento
from schemas.movimentacoes import MovimentacaoCreate, MovimentacaoOut

router = APIRouter()

@router.get("/", response_model=list[MovimentacaoOut])
def listar_movimentacoes(db: Session = Depends(get_db)):
    return db.query(Movimentacao).all()

@router.post("/", response_model=MovimentacaoOut)
def criar_movimentacao(movimentacao: MovimentacaoCreate, db: Session = Depends(get_db)):
    medicamento = db.query(Medicamento).filter(Medicamento.id == movimentacao.medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")

    if movimentacao.tipo == "entrada":
        medicamento.estoque_atual += movimentacao.quantidade
    elif movimentacao.tipo == "saida":
        if medicamento.estoque_atual < movimentacao.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente")
        medicamento.estoque_atual -= movimentacao.quantidade
    else:
        raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'")

    nova = Movimentacao(**movimentacao.dict())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    db.commit()  # confirma a atualização do estoque também
    return nova