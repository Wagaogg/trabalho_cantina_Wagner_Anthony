from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import FORMA_DINHEIRO, FORMA_PIX, POLL_MS
from core import pedidos, produtos
from ui.componentes import (
    adicionar_linha,
    brl,
    cartao,
    celula,
    criar_tabela,
    erro,
    id_selecionado,
    selecionar_id,
    subtitulo,
    titulo,
)
from ui.dialogo_dinheiro import DialogoDinheiro
from ui.dialogo_qr import DialogoQR


class JanelaPedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pedidos")
        self.resize(920, 620)

        self.carrinho = {}
        self.catalogo = {}
        self._assinatura = None

        self._montar_interface()
        self.carregar_produtos()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.carregar_produtos)
        self.timer.start(POLL_MS)

    def _montar_interface(self):
        # ----- Coluna esquerda: produtos -----
        self.lista = QListWidget()
        self.lista.itemDoubleClicked.connect(self.adicionar)

        coluna_produtos = QVBoxLayout()
        coluna_produtos.setSpacing(8)
        coluna_produtos.addWidget(titulo("Produtos"))
        coluna_produtos.addWidget(QLabel("Duplo clique para adicionar ao carrinho"))
        coluna_produtos.addWidget(self.lista)
        cartao_produtos = cartao(coluna_produtos)

        # ----- Coluna direita: carrinho -----
        self.tabela = criar_tabela(["Produto", "Qtd", "Subtotal"])

        botao_menos = QPushButton("−")
        botao_mais = QPushButton("+")
        botao_tirar = QPushButton("Tirar")
        botao_limpar = QPushButton("Limpar")
        linha_botoes = QHBoxLayout()
        linha_botoes.setSpacing(6)
        for botao in (botao_menos, botao_mais, botao_tirar):
            linha_botoes.addWidget(botao)
        linha_botoes.addStretch()
        linha_botoes.addWidget(botao_limpar)

        self.rotulo_total = QLabel()
        self.rotulo_total.setObjectName("total")
        self.rotulo_total.setAlignment(Qt.AlignRight)

        self.rotulo_aviso = QLabel()
        self.rotulo_aviso.setObjectName("aviso")
        self.rotulo_aviso.setWordWrap(True)
        self.rotulo_aviso.hide()

        botao_pix = QPushButton("Pagar com Pix")
        botao_pix.setObjectName("primario")
        botao_dinheiro = QPushButton("Pagar em dinheiro")
        botao_dinheiro.setObjectName("dinheiro")
        linha_pagamento = QHBoxLayout()
        linha_pagamento.setSpacing(8)
        linha_pagamento.addWidget(botao_pix)
        linha_pagamento.addWidget(botao_dinheiro)

        coluna_carrinho = QVBoxLayout()
        coluna_carrinho.setSpacing(8)
        coluna_carrinho.addWidget(titulo("Carrinho"))
        coluna_carrinho.addWidget(self.tabela)
        coluna_carrinho.addLayout(linha_botoes)
        coluna_carrinho.addWidget(self.rotulo_total)
        coluna_carrinho.addWidget(self.rotulo_aviso)
        coluna_carrinho.addLayout(linha_pagamento)
        cartao_carrinho = cartao(coluna_carrinho)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        layout.addWidget(cartao_produtos, 1)
        layout.addWidget(cartao_carrinho, 1)

        botao_menos.clicked.connect(lambda: self.alterar_quantidade(-1))
        botao_mais.clicked.connect(lambda: self.alterar_quantidade(+1))
        botao_tirar.clicked.connect(self.tirar)
        botao_limpar.clicked.connect(self.limpar)
        botao_pix.clicked.connect(lambda: self.finalizar(FORMA_PIX))
        botao_dinheiro.clicked.connect(lambda: self.finalizar(FORMA_DINHEIRO))

    def carregar_produtos(self):
        lista = produtos.listar()
        assinatura = [
            (p["id"], p["nome"], p["preco"], p["estado"], p["estoque"]) for p in lista
        ]
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura
        self.catalogo = {p["id"]: p for p in lista}

        self.lista.clear()
        for produto in lista:
            esgotado = produto["estado"] == produtos.ESGOTADO
            texto = f"{produto['nome']}   —   {brl(produto['preco'])}"
            if esgotado:
                texto += "   [ESGOTADO]"
            elif produto["estoque"] is not None:
                texto += f"   (restam {produto['estoque']})"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, produto["id"])
            if esgotado:
                item.setFlags(Qt.NoItemFlags)
                item.setForeground(QColor("#9ca3af"))
            self.lista.addItem(item)

        self._ajustar_carrinho()
        self.atualizar_carrinho()

    def _ajustar_carrinho(self):
        avisos = []
        for pid in list(self.carrinho):
            produto = self.catalogo.get(pid)
            if produto is None or produto["estado"] != produtos.DISPONIVEL:
                nome = produto["nome"] if produto else f"#{pid}"
                avisos.append(f"{nome} saiu do carrinho (indisponível)")
                del self.carrinho[pid]
            elif produto["estoque"] is not None and self.carrinho[pid] > produto["estoque"]:
                self.carrinho[pid] = produto["estoque"]
                avisos.append(f"{produto['nome']}: só restam {produto['estoque']}")
        if avisos:
            self._mostrar_aviso(" | ".join(avisos))

    def _mostrar_aviso(self, texto):
        if texto:
            self.rotulo_aviso.setText(texto)
            self.rotulo_aviso.show()
        else:
            self.rotulo_aviso.clear()
            self.rotulo_aviso.hide()

    def _cabe_no_estoque(self, produto, quantidade):
        estoque = produto["estoque"]
        if estoque is not None and quantidade > estoque:
            self._mostrar_aviso(f"Só restam {estoque} de {produto['nome']}.")
            return False
        return True

    def total_carrinho(self):
        return sum(self.catalogo[pid]["preco"] * q for pid, q in self.carrinho.items())

    def atualizar_carrinho(self, manter_id=None):
        self.tabela.setRowCount(0)
        for pid, quantidade in self.carrinho.items():
            produto = self.catalogo[pid]
            adicionar_linha(
                self.tabela,
                pid,
                [
                    celula(produto["nome"]),
                    celula(quantidade, direita=True),
                    celula(brl(produto["preco"] * quantidade), direita=True),
                ],
            )
        self.rotulo_total.setText(f"Total: {brl(self.total_carrinho())}")
        if manter_id is not None:
            selecionar_id(self.tabela, manter_id)

    def adicionar(self, item):
        produto_id = item.data(Qt.UserRole)
        quantidade = self.carrinho.get(produto_id, 0) + 1
        if not self._cabe_no_estoque(self.catalogo[produto_id], quantidade):
            return
        self.carrinho[produto_id] = quantidade
        self._mostrar_aviso("")
        self.atualizar_carrinho(produto_id)

    def alterar_quantidade(self, delta):
        produto_id = id_selecionado(self.tabela)
        if produto_id is None:
            return
        nova = self.carrinho[produto_id] + delta
        if nova <= 0:
            del self.carrinho[produto_id]
            self.atualizar_carrinho()
            return
        if delta > 0 and not self._cabe_no_estoque(self.catalogo[produto_id], nova):
            return
        self.carrinho[produto_id] = nova
        self.atualizar_carrinho(produto_id)

    def tirar(self):
        produto_id = id_selecionado(self.tabela)
        if produto_id is not None:
            del self.carrinho[produto_id]
            self.atualizar_carrinho()

    def limpar(self):
        self.carrinho.clear()
        self._mostrar_aviso("")
        self.atualizar_carrinho()

    def finalizar(self, forma):
        itens = list(self.carrinho.items())
        if not itens:
            erro(self, "O carrinho está vazio.")
            return

        troco = 0.0
        if forma == FORMA_DINHEIRO:
            dialogo = DialogoDinheiro(self, self.total_carrinho())
            if dialogo.exec() != QDialog.Accepted:
                return
            troco = dialogo.troco()

        try:
            pedido = pedidos.criar(itens, forma)
        except ValueError as e:
            erro(self, str(e))
            return

        self.limpar()
        self._assinatura = None
        self.carregar_produtos()

        if forma == FORMA_PIX:
            DialogoQR(self, pedido).exec()
        else:
            QMessageBox.information(
                self,
                f"Pedido #{pedido['id']}",
                f"Pedido #{pedido['id']} pago em dinheiro.\nTroco: {brl(troco)}",
            )