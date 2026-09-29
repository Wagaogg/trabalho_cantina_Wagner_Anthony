from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from ui.componentes import brl


class DialogoDinheiro(QDialog):
    def __init__(self, parent, total):
        super().__init__(parent)
        self.total = total
        self.setWindowTitle("Pagamento em dinheiro")

        titulo = QLabel(f"Total: {brl(total)}")
        titulo.setObjectName("total")

        self.recebido = QDoubleSpinBox()
        self.recebido.setPrefix("R$ ")
        self.recebido.setDecimals(2)
        self.recebido.setMaximum(100000)
        self.recebido.setValue(total)

        self.rotulo_troco = QLabel()
        self.rotulo_troco.setObjectName("total")

        formulario = QFormLayout()
        formulario.addRow("Valor recebido", self.recebido)

        self.botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.botoes.button(QDialogButtonBox.Ok).setText("Confirmar pagamento")
        self.botoes.accepted.connect(self.accept)
        self.botoes.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addLayout(formulario)
        layout.addWidget(self.rotulo_troco)
        layout.addWidget(self.botoes)

        self.recebido.valueChanged.connect(self.atualizar_troco)
        self.atualizar_troco()
        self.recebido.setFocus()
        self.recebido.selectAll()

    def atualizar_troco(self):
        diferenca = round(self.recebido.value() - self.total, 2)
        botao_ok = self.botoes.button(QDialogButtonBox.Ok)
        if diferenca < 0:
            self.rotulo_troco.setText(f"Faltam {brl(-diferenca)}")
            botao_ok.setEnabled(False)
        else:
            self.rotulo_troco.setText(f"Troco: {brl(diferenca)}")
            botao_ok.setEnabled(True)

    def troco(self):
        return max(round(self.recebido.value() - self.total, 2), 0.0)
