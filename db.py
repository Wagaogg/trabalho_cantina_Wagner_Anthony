import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def conexao():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def _adicionar_coluna(con, tabela, coluna, definicao):
    existentes = [linha["name"] for linha in con.execute(f"PRAGMA table_info({tabela})")]
    if coluna not in existentes:
        con.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")


def init_db():
    with conexao() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nome    TEXT NOT NULL,
                preco   REAL NOT NULL,
                estado  TEXT NOT NULL DEFAULT 'DISPONIVEL',
                estoque INTEGER
            );

            CREATE TABLE IF NOT EXISTS recebedor (
                id        INTEGER PRIMARY KEY CHECK (id = 1),
                chave_pix TEXT NOT NULL,
                nome      TEXT NOT NULL,
                cidade    TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pedidos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                valor_total     REAL NOT NULL,
                status          TEXT NOT NULL DEFAULT 'PENDENTE',
                forma_pagamento TEXT NOT NULL DEFAULT 'PIX',
                payload         TEXT NOT NULL DEFAULT '',
                criado_em       TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS itens_pedido (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id  INTEGER NOT NULL REFERENCES pedidos(id),
                produto_id INTEGER NOT NULL REFERENCES produtos(id),
                nome       TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unit REAL NOT NULL
            );
            """
        )
        _adicionar_coluna(con, "produtos", "estoque", "INTEGER")
        _adicionar_coluna(con, "pedidos", "forma_pagamento", "TEXT NOT NULL DEFAULT 'PIX'")
