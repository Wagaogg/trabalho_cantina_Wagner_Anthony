import sys

from PySide6.QtWidgets import QApplication

import db
from core import recebedor
from ui.componentes import ESTILO
from ui.janela_admin import JanelaAdmin
from ui.janela_pedidos import JanelaPedidos
from ui.janela_recebedor import JanelaRecebedor


def main():
    db.init_db()

    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO)

    janela_recebedor = JanelaRecebedor()
    janela_pedidos = JanelaPedidos()
    janela_admin = JanelaAdmin()

    janela_recebedor.move(40, 60)
    janela_pedidos.move(700, 60)
    janela_admin.move(300, 200)

    for janela in (janela_recebedor, janela_pedidos, janela_admin):
        janela.show()

    if recebedor.obter() is None:
        janela_admin.abrir_aba_recebedor()
        janela_admin.raise_()
        janela_admin.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
