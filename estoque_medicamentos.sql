-- =========================================================
-- Banco de dados: Assistente Inteligente para Gestão de
-- Estoque de Medicamentos utilizando IA Generativa
-- Compatível com SQLite (ajustar tipos se usar PostgreSQL/MySQL)
-- =========================================================

CREATE TABLE usuarios (
    id_usuario   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    email        TEXT NOT NULL UNIQUE,
    senha_hash   TEXT NOT NULL,
    perfil       TEXT NOT NULL CHECK (perfil IN ('administrador', 'funcionario', 'consulta')),
    ativo        BOOLEAN NOT NULL DEFAULT 1,
    criado_em    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicamentos (
    id_medicamento     INTEGER PRIMARY KEY AUTOINCREMENT,
    nome               TEXT NOT NULL,
    principio_ativo    TEXT NOT NULL,
    concentracao       TEXT,
    forma_farmaceutica TEXT,
    estoque_atual      INTEGER NOT NULL DEFAULT 0 CHECK (estoque_atual >= 0),
    estoque_minimo     INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    ativo              BOOLEAN NOT NULL DEFAULT 1,
    criado_em          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE movimentacoes (
    id_movimentacao  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario       INTEGER NOT NULL,
    id_medicamento   INTEGER NOT NULL,
    tipo             TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    quantidade       INTEGER NOT NULL CHECK (quantidade > 0),
    data_hora        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id_medicamento)
);

CREATE TABLE interacoes_chatbot (
    id_interacao  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario    INTEGER NOT NULL,
    pergunta      TEXT NOT NULL,
    resposta      TEXT NOT NULL,
    data_hora     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- =========================================================
-- Trigger para manter estoque_atual sincronizado
-- (evita ter que recalcular via SUM toda hora)
-- =========================================================

CREATE TRIGGER trg_movimentacao_entrada
AFTER INSERT ON movimentacoes
WHEN NEW.tipo = 'ENTRADA'
BEGIN
    UPDATE medicamentos
    SET estoque_atual = estoque_atual + NEW.quantidade
    WHERE id_medicamento = NEW.id_medicamento;
END;

CREATE TRIGGER trg_movimentacao_saida
AFTER INSERT ON movimentacoes
WHEN NEW.tipo = 'SAIDA'
BEGIN
    UPDATE medicamentos
    SET estoque_atual = estoque_atual - NEW.quantidade
    WHERE id_medicamento = NEW.id_medicamento;
END;

-- =========================================================
-- Consultas úteis para o chatbot responder
-- =========================================================

-- Medicamentos abaixo do estoque mínimo
-- SELECT nome, estoque_atual, estoque_minimo FROM medicamentos WHERE estoque_atual < estoque_minimo;

-- Histórico de movimentações de um medicamento
-- SELECT m.tipo, m.quantidade, m.data_hora, u.nome
-- FROM movimentacoes m JOIN usuarios u ON m.id_usuario = u.id_usuario
-- WHERE m.id_medicamento = ? ORDER BY m.data_hora;
