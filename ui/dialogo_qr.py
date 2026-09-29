from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout

from core import pix
from ui.componentes import brl


class DialogoQR(QDialog):
    def __init__(self, parent, pedido):
        super().__init__(parent)
        self.payload = pedido["payload"]
        self.setWindowTitle(f"Pedido #{pedido['id']}")

        caminho = pix.salvar_qrcode(self.payload, f"pedido_{pedido['id']}")
        imagem = QLabel()
        imagem.setPixmap(
            QPixmap(str(caminho)).scaled(
                320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        imagem.setAlignment(Qt.AlignCenter)

        titulo = QLabel(f"Pedido #{pedido['id']}  —  {brl(pedido['valor_total'])}")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)

        self.botao_copiar = QPushButton("Copiar código Pix (Copia e Cola)")
        self.botao_copiar.clicked.connect(self.copiar)
        botao_fechar = QPushButton("Fechar")
        botao_fechar.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addWidget(imagem)
        layout.addWidget(self.botao_copiar)
        layout.addWidget(botao_fechar)

    def copiar(self):
        QApplication.clipboard().setText(self.payload)
        self.botao_copiar.setText("Copiado!")
