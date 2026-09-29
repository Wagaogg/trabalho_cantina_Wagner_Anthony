from db import conexao

DISPONIVEL = "DISPONIVEL"
ESGOTADO = "ESGOTADO"
REMOVIDO = "REMOVIDO"


def _validar(nome, preco, estoque):
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("Informe o nome do produto.")
    if preco is None or preco <= 0:
        raise ValueError("O preço precisa ser maior que zero.")
    if estoque is not None and estoque < 0:
        raise ValueError("O estoque não pode ser negativo.")
    return nome, round(float(preco), 2)


def criar(nome, preco, estoque=None):
    nome, preco = _validar(nome, preco, estoque)
    estado = ESGOTADO if estoque == 0 else DISPONIVEL
    with conexao() as con:
        cur = con.execute(
            "INSERT INTO produtos (nome, preco, estoque, estado) VALUES (?, ?, ?, ?)",
            (nome, preco, estoque, estado),
        )
        return cur.lastrowid


def listar(incluir_removidos=False):
    sql = "SELECT * FROM produtos"
    if not incluir_removidos:
        sql += f" WHERE estado != '{REMOVIDO}'"
    sql += " ORDER BY nome COLLATE NOCASE"
    with conexao() as con:
        return [dict(linha) for linha in con.execute(sql)]


def obter(produto_id):
    with conexao() as con:
        linha = con.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
    return dict(linha) if linha else None


def atualizar(produto_id, nome, preco, estoque=None):
    nome, preco = _validar(nome, preco, estoque)
    atual = obter(produto_id)
    estado = atual["estado"]
    if estoque is not None and estoque != atual["estoque"]:
        estado = ESGOTADO if estoque == 0 else DISPONIVEL
    with conexao() as con:
        con.execute(
            "UPDATE produtos SET nome = ?, preco = ?, estoque = ?, estado = ? WHERE id = ?",
            (nome, preco, estoque, estado, produto_id),
        )


def definir_estado(produto_id, estado):
    if estado not in (DISPONIVEL, ESGOTADO, REMOVIDO):
        raise ValueError(f"Estado inválido: {estado}")
    with conexao() as con:
        con.execute(
            "UPDATE produtos SET estado = ? WHERE id = ?", (estado, produto_id)
        )


def alternar_esgotado(produto_id):
    produto = obter(produto_id)
    if produto is None:
        return
    if produto["estado"] == ESGOTADO:
        if produto["estoque"] == 0:
            raise ValueError("O estoque está zerado. Use Editar para informar a nova quantidade.")
        definir_estado(produto_id, DISPONIVEL)
    else:
        definir_estado(produto_id, ESGOTADO)


def remover(produto_id):
    definir_estado(produto_id, REMOVIDO)
