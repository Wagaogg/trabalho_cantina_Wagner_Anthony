from config import (
    FORMA_DINHEIRO,
    FORMA_PIX,
    STATUS_CANCELADO,
    STATUS_PAGO,
    STATUS_PENDENTE,
)
from core import pix, produtos, recebedor
from db import conexao


def _validar_itens(itens):
    if not itens:
        raise ValueError("O carrinho está vazio.")
    linhas = []
    for produto_id, quantidade in itens:
        produto = produtos.obter(produto_id)
        if produto is None or produto["estado"] != produtos.DISPONIVEL:
            nome = produto["nome"] if produto else f"#{produto_id}"
            raise ValueError(f"'{nome}' não está disponível.")
        if quantidade <= 0:
            raise ValueError("Quantidade inválida.")
        if produto["estoque"] is not None and quantidade > produto["estoque"]:
            raise ValueError(f"Só restam {produto['estoque']} de '{produto['nome']}'.")
        linhas.append((produto, quantidade))
    return linhas


def _baixar_estoque(con, produto, quantidade):
    if produto["estoque"] is None:
        return
    cur = con.execute(
        """
        UPDATE produtos SET
            estado = CASE WHEN estoque - :q = 0 THEN 'ESGOTADO' ELSE estado END,
            estoque = estoque - :q
        WHERE id = :id AND estoque >= :q
        """,
        {"q": quantidade, "id": produto["id"]},
    )
    if cur.rowcount == 0:
        raise ValueError(f"Estoque insuficiente de '{produto['nome']}'.")


def _devolver_estoque(con, pedido_id):
    itens = con.execute(
        "SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?",
        (pedido_id,),
    ).fetchall()
    for item in itens:
        con.execute(
            """
            UPDATE produtos SET
                estado = CASE WHEN estoque = 0 AND estado = 'ESGOTADO'
                              THEN 'DISPONIVEL' ELSE estado END,
                estoque = estoque + :q
            WHERE id = :id AND estoque IS NOT NULL
            """,
            {"q": item["quantidade"], "id": item["produto_id"]},
        )


def criar(itens, forma=FORMA_PIX):
    """itens: lista de tuplas (produto_id, quantidade)."""
    if forma not in (FORMA_PIX, FORMA_DINHEIRO):
        raise ValueError(f"Forma de pagamento inválida: {forma}")

    linhas = _validar_itens(itens)

    dados_recebedor = None
    if forma == FORMA_PIX:
        dados_recebedor = recebedor.obter()
        if dados_recebedor is None:
            raise ValueError("Cadastre o recebedor na janela Admin antes de vender no Pix.")

    status = STATUS_PENDENTE if forma == FORMA_PIX else STATUS_PAGO
    total = round(sum(p["preco"] * q for p, q in linhas), 2)

    with conexao() as con:
        pedido_id = con.execute(
            "INSERT INTO pedidos (valor_total, status, forma_pagamento) VALUES (?, ?, ?)",
            (total, status, forma),
        ).lastrowid

        if dados_recebedor:
            payload = pix.gerar_payload(
                dados_recebedor["chave_pix"],
                dados_recebedor["nome"],
                dados_recebedor["cidade"],
                total,
                f"PED{pedido_id:06d}",
            )
            con.execute("UPDATE pedidos SET payload = ? WHERE id = ?", (payload, pedido_id))

        con.executemany(
            """
            INSERT INTO itens_pedido (pedido_id, produto_id, nome, quantidade, preco_unit)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(pedido_id, p["id"], p["nome"], q, p["preco"]) for p, q in linhas],
        )
        for produto, quantidade in linhas:
            _baixar_estoque(con, produto, quantidade)

    return obter(pedido_id)


def obter(pedido_id):
    with conexao() as con:
        linha = con.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    return dict(linha) if linha else None


def listar(status=None):
    sql, params = "SELECT * FROM pedidos", ()
    if status:
        sql += " WHERE status = ?"
        params = (status,)
    sql += " ORDER BY id DESC"
    with conexao() as con:
        return [dict(linha) for linha in con.execute(sql, params)]


def itens_do_pedido(pedido_id):
    with conexao() as con:
        linhas = con.execute(
            "SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido_id,)
        )
        return [dict(linha) for linha in linhas]


def ultimo_id():
    with conexao() as con:
        return con.execute("SELECT COALESCE(MAX(id), 0) FROM pedidos").fetchone()[0]


def marcar_pago(pedido_id):
    with conexao() as con:
        con.execute(
            "UPDATE pedidos SET status = ? WHERE id = ? AND status = ?",
            (STATUS_PAGO, pedido_id, STATUS_PENDENTE),
        )


def cancelar(pedido_id):
    """Cancela um pedido PENDENTE (Pix) ou um PAGO em DINHEIRO.

    Pedidos pagos em Pix não são cancelados aqui — o dinheiro teria que
    ser estornado pelo banco primeiro.
    """
    with conexao() as con:
        pedido = con.execute(
            "SELECT status, forma_pagamento FROM pedidos WHERE id = ?",
            (pedido_id,),
        ).fetchone()

        if pedido is None:
            raise ValueError("Pedido não encontrado.")
        if pedido["status"] == STATUS_CANCELADO:
            raise ValueError("Este pedido já está cancelado.")
        if (
            pedido["status"] == STATUS_PAGO
            and pedido["forma_pagamento"] != FORMA_DINHEIRO
        ):
            raise ValueError(
                "Pedido pago em Pix não pode ser cancelado aqui. "
                "Estorne pelo banco e marque manualmente."
            )

        con.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (STATUS_CANCELADO, pedido_id),
        )
        _devolver_estoque(con, pedido_id)