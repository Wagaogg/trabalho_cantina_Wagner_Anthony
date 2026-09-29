from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

ESTILO = """
* {
    font-family: 'Segoe UI', 'Inter', 'Noto Sans', 'DejaVu Sans', sans-serif;
    font-size: 14px;
}

QMainWindow, QDialog, QWidget {
    background: #eef1f6;
    color: #111827;
}

/* ---------------- Botões ---------------- */
QPushButton {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid #d5dae2;
    background: #ffffff;
    color: #1f2937;
    font-weight: 500;
}
QPushButton:hover { background: #f4f6fb; border-color: #c3cad6; }
QPushButton:pressed { background: #e6ebf3; border-color: #b4bdcc; }
QPushButton:disabled {
    color: #a0a8b4;
    background: #f3f5f8;
    border-color: #e2e6ec;
}

QPushButton#primario {
    background: #16a34a;
    color: white;
    font-weight: 700;
    border: none;
    padding: 13px 20px;
    border-radius: 8px;
}
QPushButton#primario:hover { background: #15803d; }
QPushButton#primario:pressed { background: #166534; }
QPushButton#primario:disabled { background: #a7d4b6; color: #f0fdf4; }

QPushButton#dinheiro {
    background: #2563eb;
    color: white;
    font-weight: 700;
    border: none;
    padding: 13px 20px;
    border-radius: 8px;
}
QPushButton#dinheiro:hover { background: #1d4ed8; }
QPushButton#dinheiro:pressed { background: #1e40af; }

QPushButton#perigo {
    color: #b91c1c;
    border: 1px solid #f0c2c2;
    background: #fff5f5;
    font-weight: 600;
}
QPushButton#perigo:hover { background: #ffe7e7; border-color: #e79a9a; }
QPushButton#perigo:pressed { background: #ffd5d5; }

/* ---------------- Rótulos ---------------- */
QLabel { background: transparent; }

QLabel#titulo {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    padding: 2px 0;
}
QLabel#subtitulo {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QLabel#total {
    font-size: 32px;
    font-weight: 800;
    color: #15803d;
    padding: 4px 0;
}
QLabel#aviso {
    color: #b45309;
    font-weight: 600;
    background: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 8px 12px;
}
QLabel#dica {
    color: #64748b;
    font-style: italic;
    font-size: 13px;
}

/* ---------------- Cartões ---------------- */
QFrame#cartao {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

/* ---------------- Campos ---------------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
    padding: 8px 12px;
    border: 1px solid #d5dae2;
    border-radius: 8px;
    background: #ffffff;
    color: #111827;
    min-height: 24px;
    selection-background-color: #bbf7d0;
    selection-color: #14532d;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {
    border: 2px solid #16a34a;
    padding: 7px 11px;
}
QLineEdit::placeholder { color: #94a3b8; }

QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #d5dae2;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #dcfce7;
    selection-color: #14532d;
    outline: none;
}

/* ---------------- Lista de produtos ---------------- */
QListWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 6px;
    outline: none;
}
QListWidget::item {
    padding: 10px 12px;
    border-radius: 6px;
    color: #1f2937;
}
QListWidget::item:hover { background: #f1f5f9; }
QListWidget::item:selected {
    background: #dcfce7;
    color: #14532d;
    font-weight: 600;
}

/* ---------------- Tabelas ---------------- */
QTableWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: transparent;
    alternate-background-color: #fafbfd;
    selection-background-color: #dcfce7;
    selection-color: #14532d;
    outline: none;
    padding: 4px;
}
QTableWidget::item {
    padding: 8px 10px;
    border: none;
}
QTableWidget::item:selected {
    background: #dcfce7;
    color: #14532d;
}
QHeaderView { background: transparent; }
QHeaderView::section {
    background: #f1f5f9;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.5px;
}
QHeaderView::section:first { border-top-left-radius: 10px; }
QHeaderView::section:last  { border-top-right-radius: 10px; }

/* ---------------- Abas ---------------- */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: #ffffff;
    top: -1px;
    padding: 8px;
}
QTabBar::tab {
    padding: 10px 22px;
    background: #e2e8f0;
    border: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 4px;
    color: #475569;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #16a34a;
}
QTabBar::tab:hover:!selected { background: #cbd5e1; }

/* ---------------- Scroll ---------------- */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #94a3b8; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 4px;
}
QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #94a3b8; }

/* ---------------- Diálogos ---------------- */
QDialog QLabel { color: #1f2937; }
QMessageBox { background: #ffffff; }
QMessageBox QLabel { color: #1f2937; font-size: 14px; }
"""

COR_OK = "#16a34a"
COR_ALERTA = "#b45309"
COR_ERRO = "#dc2626"
COR_NEUTRA = "#64748b"


# ---------------------------------------------------------------------------
# Helpers de formatação
# ---------------------------------------------------------------------------
def brl(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# Helpers de layout
# ---------------------------------------------------------------------------
def titulo(texto):
    label = QLabel(texto)
    label.setObjectName("titulo")
    return label


def subtitulo(texto):
    label = QLabel(texto)
    label.setObjectName("subtitulo")
    return label


def cartao(*widgets_ou_layouts):
    """Devolve um QFrame branco com cantos arredondados pra agrupar conteúdo."""
    frame = QFrame()
    frame.setObjectName("cartao")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)
    for item in widgets_ou_layouts:
        if hasattr(item, "addWidget"):
            layout.addLayout(item)
        else:
            layout.addWidget(item)
    return frame


# ---------------------------------------------------------------------------
# Helpers de tabela
# ---------------------------------------------------------------------------
def criar_tabela(colunas, coluna_esticada=0):
    tabela = QTableWidget(0, len(colunas))
    tabela.setHorizontalHeaderLabels(colunas)
    tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
    tabela.setSelectionMode(QAbstractItemView.SingleSelection)
    tabela.setAlternatingRowColors(True)
    tabela.verticalHeader().setVisible(False)
    tabela.setShowGrid(False)
    tabela.setFocusPolicy(Qt.NoFocus)
    cabecalho = tabela.horizontalHeader()
    cabecalho.setSectionResizeMode(QHeaderView.ResizeToContents)
    cabecalho.setSectionResizeMode(coluna_esticada, QHeaderView.Stretch)
    cabecalho.setHighlightSections(False)
    return tabela


def celula(texto, cor=None, direita=False, negrito=False, fundo=None):
    item = QTableWidgetItem(str(texto))
    if cor:
        item.setForeground(QColor(cor))
    if fundo:
        item.setBackground(QColor(fundo))
    if direita:
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    else:
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    if negrito:
        fonte = item.font()
        fonte.setBold(True)
        item.setFont(fonte)
    return item


def adicionar_linha(tabela, identificador, celulas):
    linha = tabela.rowCount()
    tabela.insertRow(linha)
    for coluna, item in enumerate(celulas):
        tabela.setItem(linha, coluna, item)
    tabela.item(linha, 0).setData(Qt.UserRole, identificador)


def id_selecionado(tabela):
    linhas = tabela.selectionModel().selectedRows()
    if not linhas:
        return None
    return tabela.item(linhas[0].row(), 0).data(Qt.UserRole)


def selecionar_id(tabela, identificador):
    for linha in range(tabela.rowCount()):
        if tabela.item(linha, 0).data(Qt.UserRole) == identificador:
            tabela.selectRow(linha)
            return


# ---------------------------------------------------------------------------
# Helpers de diálogo
# ---------------------------------------------------------------------------
def erro(parent, mensagem):
    QMessageBox.warning(parent, "Atenção", mensagem)


def confirmar(parent, mensagem):
    resposta = QMessageBox.question(parent, "Confirmar", mensagem)
    return resposta == QMessageBox.Yes