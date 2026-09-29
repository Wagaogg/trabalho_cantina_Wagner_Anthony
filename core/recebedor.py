from db import conexao


def salvar(chave_pix, nome, cidade):
    chave_pix, nome, cidade = (v.strip() for v in (chave_pix, nome, cidade))
    if not (chave_pix and nome and cidade):
        raise ValueError("Preencha chave Pix, nome e cidade.")
    with conexao() as con:
        con.execute(
            """
            INSERT INTO recebedor (id, chave_pix, nome, cidade)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                chave_pix = excluded.chave_pix,
                nome = excluded.nome,
                cidade = excluded.cidade
            """,
            (chave_pix, nome, cidade),
        )


def obter():
    with conexao() as con:
        linha = con.execute("SELECT * FROM recebedor WHERE id = 1").fetchone()
    return dict(linha) if linha else None
