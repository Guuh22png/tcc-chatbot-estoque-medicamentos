from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioOut
from security import gerar_hash, verificar_senha
from schemas.usuario import UsuarioCreate, UsuarioOut, LoginIn

router = APIRouter()

# Funções para lidar com os endpoints de usuários
@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

# Função para criar um novo usuário
@router.post("/login", response_model=UsuarioOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not u or not verificar_senha(dados.senha, u.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    if not u.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    return u

# Função para alterar o status ativo de um usuário
@router.put("/{usuario_id}/ativo", response_model=UsuarioOut)
def alterar_ativo(usuario_id: int, ativo: bool, db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    u.ativo = ativo
    db.commit()
    db.refresh(u)
    return u

# Função para deletar um usuário
@router.delete("/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensagem": f"Usuário {usuario_id} removido com sucesso"}

# Função para criar um novo usuário
@router.post("/", response_model=UsuarioOut)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    dados = usuario.dict()
    dados["senha"] = gerar_hash(dados["senha"])
    novo = Usuario(**dados)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

# Função para editar um usuário
@router.put("/{usuario_id}", response_model=UsuarioOut)
def editar_usuario(usuario_id: int, dados: UsuarioCreate, db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    for campo, valor in dados.dict().items():
        setattr(u, campo, valor)
    db.commit()
    db.refresh(u)
    return u

# Função para login
@router.post("/login", response_model=UsuarioOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not u or not verificar_senha(dados.senha, u.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    return u
