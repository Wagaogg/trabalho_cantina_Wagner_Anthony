from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import (
    FORMA_DINHEIRO,
    POLL_MS,
    STATUS_CANCELADO,
    STATUS_PAGO,
    STATUS_PENDENTE,
)
from core import pedidos
from ui.componentes import (
    COR_ALERTA,
    COR_NEUTRA,
    COR_OK,
    adicionar_linha,
    brl,
    cartao,
    celula,
    confirmar,
    criar_tabela,
    erro,
    id_selecionado,
    selecionar_id,
    titulo,
)
from ui.dialogo_fechamento import DialogoFechamento
from ui.dialogo_qr import DialogoQR

COR_STATUS = {
    STATUS_PENDENTE: COR_ALERTA,
    STATUS_PAGO: COR_OK,
    STATUS_CANCELADO: COR_NEUTRA,
}
FUNDO_NOVO = "#fef3c7"


class JanelaRecebedor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recebedor")
        self.resize(760, 600)

        self._assinatura = None
        self._ultimo_id = pedidos.ultimo_id()
        self._novos = set()

        self._montar_interface()
        self.atualizar()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar)
        self.timer.start(POLL_MS)

    def _montar_interface(self):
        self.filtro = QComboBox()
        self.filtro.addItems(["Todos", STATUS_PENDENTE, STATUS_PAGO, STATUS_CANCELADO])
        botao_fechamento = QPushButton("Fechamento do dia")

        topo = QHBoxLayout()
        topo.setSpacing(8)
        topo.addWidget(titulo("Pedidos"))
        topo.addStretch()
        topo.addWidget(QLabel("Filtrar:"))
        topo.addWidget(self.filtro)
        topo.addWidget(botao_fechamento)

        self.rotulo_aviso = QLabel()
        self.rotulo_aviso.setObjectName("aviso")
        self.rotulo_aviso.hide()

        self.tabela = criar_tabela(
            ["Pedido", "Valor", "Forma", "Status", "Hora"], coluna_esticada=1
        )

        botao_pago = QPushButton("Marcar como PAGO")
        botao_pago.setObjectName("primario")
        botao_cancelar = QPushButton("Cancelar pedido")
        botao_cancelar.setObjectName("perigo")
        botao_qr = QPushButton("Ver QR Code")

        botoes = QHBoxLayout()
        botoes.setSpacing(8)
        botoes.addWidget(botao_pago)
        botoes.addWidget(botao_qr)
        botoes.addStretch()
        botoes.addWidget(botao_cancelar)

        conteudo = QVBoxLayout()
        conteudo.setSpacing(10)
        conteudo.addLayout(topo)
        conteudo.addWidget(self.rotulo_aviso)
        conteudo.addWidget(self.tabela)
        conteudo.addLayout(botoes)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(cartao(conteudo))

        self.filtro.currentIndexChanged.connect(self.forcar_atualizacao)
        self.tabela.itemSelectionChanged.connect(self.ao_selecionar)
        botao_fechamento.clicked.connect(lambda: DialogoFechamento(self).exec())
        botao_pago.clicked.connect(self.marcar_pago)
        botao_cancelar.clicked.connect(self.cancelar_pedido)
        botao_qr.clicked.connect(self.ver_qr)

    def _status_filtrado(self):
        return None if self.filtro.currentIndex() == 0 else self.filtro.currentText()

    def forcar_atualizacao(self):
        self._assinatura = None
        self.atualizar()

    def atualizar(self):
        self._detectar_novos()

        lista = pedidos.listar(self._status_filtrado())
        assinatura = [(p["id"], p["status"]) for p in lista]
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura

        selecionado = id_selecionado(self.tabela)
        self.tabela.blockSignals(True)
        self.tabela.setRowCount(0)
        for pedido in lista:
            fundo = FUNDO_NOVO if pedido["id"] in self._novos else None
            forma = "Dinheiro" if pedido["forma_pagamento"] == FORMA_DINHEIRO else "Pix"
            adicionar_linha(
                self.tabela,
                pedido["id"],
                [
                    celula(f"#{pedido['id']}", fundo=fundo, negrito=True),
                    celula(brl(pedido["valor_total"]), direita=True, fundo=fundo),
                    celula(forma, fundo=fundo),
                    celula(
                        pedido["status"],
                        cor=COR_STATUS.get(pedido["status"]),
                        negrito=True,
                        fundo=fundo,
                    ),
                    celula(pedido["criado_em"][11:16], fundo=fundo),
                ],
            )
        if selecionado is not None:
            selecionar_id(self.tabela, selecionado)
        self.tabela.blockSignals(False)

    def _detectar_novos(self):
        maior = pedidos.ultimo_id()
        if maior <= self._ultimo_id:
            return
        self._novos.update(range(self._ultimo_id + 1, maior + 1))
        self._ultimo_id = maior
        self.rotulo_aviso.setText(f"Novo pedido #{maior}")
        self.rotulo_aviso.show()
        QApplication.beep()
        self._assinatura = None

    def ao_selecionar(self):
        pedido_id = id_selecionado(self.tabela)
        if pedido_id in self._novos:
            self._novos.discard(pedido_id)
            self.rotulo_aviso.clear()
            self.rotulo_aviso.hide()
            self.forcar_atualizacao()

    def marcar_pago(self):
        pedido_id = id_selecionado(self.tabela)
        if pedido_id is None:
            return
        try:
            pedidos.marcar_pago(pedido_id)
        except ValueError as e:
            erro(self, str(e))
            return
        self.forcar_atualizacao()

    def cancelar_pedido(self):
        pedido_id = id_selecionado(self.tabela)
        if pedido_id is None:
            return
        pedido = pedidos.obter(pedido_id)
        if pedido is None:
            return

        if pedido["status"] == STATUS_PAGO:
            if not confirmar(
                self,
                f"Cancelar o pedido #{pedido_id} já PAGO em DINHEIRO?\n\n"
                "O valor deverá ser devolvido ao aluno e o estoque será reposto.",
            ):
                return

        try:
            pedidos.cancelar(pedido_id)
        except ValueError as e:
            erro(self, str(e))
            return
        self.forcar_atualizacao()

    def ver_qr(self):
        pedido_id = id_selecionado(self.tabela)
        if pedido_id is None:
            return
        pedido = pedidos.obter(pedido_id)
        if not pedido["payload"]:
            erro(self, "Pedido pago em dinheiro não tem QR Code.")
            return
        DialogoQR(self, pedido).exec()