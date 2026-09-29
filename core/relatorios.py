import csv

from config import FORMA_DINHEIRO, FORMA_PIX, STATUS_CANCELADO, STATUS_PAGO, STATUS_PENDENTE
from db import conexao


def fechamento(dia):
    """dia no formato AAAA-MM-DD."""
    with conexao() as con:
        por_forma = {
            linha["forma_pagamento"]: linha
            for linha in con.execute(
                """
                SELECT forma_pagamento, COUNT(*) AS pedidos, SUM(valor_total) AS total
                FROM pedidos
                WHERE date(criado_em) = ? AND status = ?
                GROUP BY forma_pagamento
                """,
                (dia, STATUS_PAGO),
            )
        }
        por_status = {
            linha["status"]: linha["n"]
            for linha in con.execute(
                "SELECT status, COUNT(*) AS n FROM pedidos WHERE date(criado_em) = ? GROUP BY status",
                (dia,),
            )
        }
        vendidos = [
            dict(linha)
            for linha in con.execute(
                """
                SELECT i.nome AS nome,
                       SUM(i.quantidade) AS quantidade,
                       SUM(i.quantidade * i.preco_unit) AS total
                FROM itens_pedido i
                JOIN pedidos p ON p.id = i.pedido_id
                WHERE date(p.criado_em) = ? AND p.status = ?
                GROUP BY i.nome
                ORDER BY quantidade DESC, i.nome
                """,
                (dia, STATUS_PAGO),
            )
        ]

    def resumo(forma):
        linha = por_forma.get(forma)
        return {
            "pedidos": linha["pedidos"] if linha else 0,
            "total": round(linha["total"], 2) if linha else 0.0,
        }

    pix, dinheiro = resumo(FORMA_PIX), resumo(FORMA_DINHEIRO)
    return {
        "dia": dia,
        "pix": pix,
        "dinheiro": dinheiro,
        "total_geral": round(pix["total"] + dinheiro["total"], 2),
        "pagos": pix["pedidos"] + dinheiro["pedidos"],
        "pendentes": por_status.get(STATUS_PENDENTE, 0),
        "cancelados": por_status.get(STATUS_CANCELADO, 0),
        "produtos": vendidos,
    }


def _decimal(valor):
    return f"{valor:.2f}".replace(".", ",")


def exportar_csv(dia, caminho):
    with conexao() as con:
        linhas = con.execute(
            """
            SELECT p.id, p.criado_em, p.forma_pagamento, p.status, p.valor_total,
                   group_concat(i.quantidade || 'x ' || i.nome, ', ') AS itens
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            WHERE date(p.criado_em) = ?
            GROUP BY p.id
            ORDER BY p.id
            """,
            (dia,),
        ).fetchall()

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["Pedido", "Data/Hora", "Forma", "Status", "Valor", "Itens"])
        for linha in linhas:
            escritor.writerow(
                [
                    linha["id"],
                    linha["criado_em"],
                    linha["forma_pagamento"],
                    linha["status"],
                    _decimal(linha["valor_total"]),
                    linha["itens"],
                ]
            )
    return len(linhas)
