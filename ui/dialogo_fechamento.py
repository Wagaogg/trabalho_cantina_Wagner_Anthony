from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core import relatorios
from ui.componentes import adicionar_linha, brl, celula, criar_tabela


class DialogoFechamento(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Fechamento do dia")
        self.resize(480, 560)

        self.campo_data = QDateEdit(QDate.currentDate())
        self.campo_data.setCalendarPopup(True)
        self.campo_data.setDisplayFormat("dd/MM/yyyy")

        topo = QHBoxLayout()
        topo.addWidget(QLabel("Dia:"))
        topo.addWidget(self.campo_data)
        topo.addStretch()

        self.rotulo_total = QLabel()
        self.rotulo_total.setObjectName("total")
        self.rotulo_detalhe = QLabel()
        self.rotulo_aviso = QLabel()
        self.rotulo_aviso.setObjectName("aviso")
        self.tabela = criar_tabela(["Produto", "Qtd", "Total"])

        botao_csv = QPushButton("Exportar CSV")
        botao_fechar = QPushButton("Fechar")
        botoes = QHBoxLayout()
        botoes.addWidget(botao_csv)
        botoes.addStretch()
        botoes.addWidget(botao_fechar)

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addWidget(self.rotulo_total)
        layout.addWidget(self.rotulo_detalhe)
        layout.addWidget(self.rotulo_aviso)
        layout.addWidget(QLabel("Produtos vendidos (pedidos pagos)"))
        layout.addWidget(self.tabela)
        layout.addLayout(botoes)

        self.campo_data.dateChanged.connect(self.carregar)
        botao_csv.clicked.connect(self.exportar)
        botao_fechar.clicked.connect(self.accept)

        self.carregar()

    def dia(self):
        return self.campo_data.date().toString("yyyy-MM-dd")

    def carregar(self):
        resumo = relatorios.fechamento(self.dia())
        self.rotulo_total.setText(f"Total vendido: {brl(resumo['total_geral'])}")
        self.rotulo_detalhe.setText(
            f"Pix: {brl(resumo['pix']['total'])}  ({resumo['pix']['pedidos']} pedidos)\n"
            f"Dinheiro: {brl(resumo['dinheiro']['total'])}  ({resumo['dinheiro']['pedidos']} pedidos)\n"
            f"Cancelados: {resumo['cancelados']}"
        )
        self.rotulo_aviso.setText(
            f"{resumo['pendentes']} pedido(s) ainda PENDENTE, fora do total."
            if resumo["pendentes"]
            else ""
        )

        self.tabela.setRowCount(0)
        for indice, produto in enumerate(resumo["produtos"]):
            adicionar_linha(
                self.tabela,
                indice,
                [
                    celula(produto["nome"]),
                    celula(produto["quantidade"], direita=True),
                    celula(brl(produto["total"]), direita=True),
                ],
            )

    def exportar(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar CSV", f"fechamento_{self.dia()}.csv", "CSV (*.csv)"
        )
        if not caminho:
            return
        total = relatorios.exportar_csv(self.dia(), caminho)
        QMessageBox.information(self, "Exportado", f"{total} pedido(s) salvos em:\n{caminho}")
