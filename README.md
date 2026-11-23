# Assistente para Gestão de Estoque de Medicamentos

Trabalho de Conclusão de Curso – Ciência da Informação , Universidade Federal de Santa Catarina (UFSC).
Orientador: Prof. Dr. Douglas Dylon Jerônimo de Macedo.

## Sobre o projeto

Sistema de apoio à gestão de estoque de medicamentos, composto por:

- **API** (FastAPI + SQLAlchemy + PostgreSQL) com cadastro de medicamentos, usuários e movimentações de entrada e saída;
- **Chatbot no Telegram** (baseado em regras) que consulta e registra movimentações pela API;
- **Frontend web** em React (Vite), com painel, estoque, movimentações e usuários;
- **Alertas** de estoque baixo e de validade dos medicamentos.

## Tecnologias

Python, FastAPI, SQLAlchemy, Pydantic, PostgreSQL, pyTelegramBotAPI, React, Vite.

## Como executar

### 1. Banco de dados
Crie um banco no PostgreSQL e rode o script `banco_schema.sql`.

### 2. Variáveis de ambiente
Copie `.env.example` para `.env` e preencha com seus dados (banco e token do bot).

### 3. API
    pip install -r requirements.txt
    uvicorn main:app --reload
Documentação interativa em `http://localhost:8000/docs`.

### 4. Bot do Telegram
    python bot.py

### 5. Frontend
    cd frontend
    npm install
    npm run dev

## Comandos do bot

/start, /estoque, /alerta, /entrada, /saida, /entradas, /saidas, /validade

## Autor

Gustavo 
