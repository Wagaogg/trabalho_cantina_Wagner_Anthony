from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core import produtos, recebedor
from ui.componentes import (
    COR_ERRO,
    COR_OK,
    adicionar_linha,
    brl,
    celula,
    confirmar,
    criar_tabela,
    erro,
    id_selecionado,
    selecionar_id,
)


def criar_campo_preco(valor=0.0):
    campo = QDoubleSpinBox()
    campo.setPrefix("R$ ")
    campo.setDecimals(2)
    campo.setMaximum(100000)
    campo.setValue(valor)
    return campo


def criar_campo_estoque(valor=None):
    campo = QSpinBox()
    campo.setRange(-1, 100000)
    campo.setPrefix("Estoque: ")
    campo.setSpecialValueText("Sem controle de estoque")
    campo.setValue(-1 if valor is None else valor)
    return campo


def ler_estoque(campo):
    valor = campo.value()
    return None if valor < 0 else valor


class DialogoProduto(QDialog):
    def __init__(self, parent, nome, preco, estoque):
        super().__init__(parent)
        self.setWindowTitle("Editar produto")
        self.campo_nome = QLineEdit(nome)
        self.campo_preco = criar_campo_preco(preco)
        self.campo_estoque = criar_campo_estoque(estoque)

        formulario = QFormLayout()
        formulario.addRow("Nome", self.campo_nome)
        formulario.addRow("Preço", self.campo_preco)
        formulario.addRow("Estoque", self.campo_estoque)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botoes)

    def dados(self):
        return (
            self.campo_nome.text(),
            self.campo_preco.value(),
            ler_estoque(self.campo_estoque),
        )


class AbaProdutos(QWidget):
    def __init__(self):
        super().__init__()

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("Nome do produto")
        self.campo_preco = criar_campo_preco()
        self.campo_estoque = criar_campo_estoque()
        botao_cadastrar = QPushButton("Cadastrar")
        botao_cadastrar.setObjectName("primario")

        linha_form = QHBoxLayout()
        linha_form.addWidget(self.campo_nome, 1)
        linha_form.addWidget(self.campo_preco)
        linha_form.addWidget(self.campo_estoque)
        linha_form.addWidget(botao_cadastrar)

        self.tabela = criar_tabela(["Produto", "Preço", "Estoque", "Estado"])

        botao_editar = QPushButton("Editar")
        botao_esgotado = QPushButton("Esgotado / Disponível")
        botao_remover = QPushButton("Remover")
        botao_remover.setObjectName("perigo")

        linha_botoes = QHBoxLayout()
        linha_botoes.addWidget(botao_editar)
        linha_botoes.addWidget(botao_esgotado)
        linha_botoes.addStretch()
        linha_botoes.addWidget(botao_remover)

        layout = QVBoxLayout(self)
        layout.addLayout(linha_form)
        layout.addWidget(self.tabela)
        layout.addLayout(linha_botoes)

        botao_cadastrar.clicked.connect(self.cadastrar)
        self.campo_nome.returnPressed.connect(self.cadastrar)
        botao_editar.clicked.connect(self.editar)
        botao_esgotado.clicked.connect(self.alternar_esgotado)
        botao_remover.clicked.connect(self.remover)
        self.tabela.doubleClicked.connect(self.editar)

        self.carregar()

    def carregar(self, manter_id=None):
        self.tabela.setRowCount(0)
        for produto in produtos.listar():
            esgotado = produto["estado"] == produtos.ESGOTADO
            estoque = "—" if produto["estoque"] is None else produto["estoque"]
            adicionar_linha(
                self.tabela,
                produto["id"],
                [
                    celula(produto["nome"]),
                    celula(brl(produto["preco"]), direita=True),
                    celula(estoque, direita=True),
                    celula(
                        "ESGOTADO" if esgotado else "Disponível",
                        cor=COR_ERRO if esgotado else COR_OK,
                        negrito=True,
                    ),
                ],
            )
        if manter_id is not None:
            selecionar_id(self.tabela, manter_id)

    def cadastrar(self):
        try:
            produtos.criar(
                self.campo_nome.text(),
                self.campo_preco.value(),
                ler_estoque(self.campo_estoque),
            )
        except ValueError as e:
            erro(self, str(e))
            return
        self.campo_nome.clear()
        self.campo_preco.setValue(0)
        self.campo_estoque.setValue(-1)
        self.campo_nome.setFocus()
        self.carregar()

    def editar(self):
        produto_id = id_selecionado(self.tabela)
        if produto_id is None:
            return
        produto = produtos.obter(produto_id)
        dialogo = DialogoProduto(
            self, produto["nome"], produto["preco"], produto["estoque"]
        )
        if dialogo.exec() != QDialog.Accepted:
            return
        try:
            produtos.atualizar(produto_id, *dialogo.dados())
        except ValueError as e:
            erro(self, str(e))
            return
        self.carregar(produto_id)

    def alternar_esgotado(self):
        produto_id = id_selecionado(self.tabela)
        if produto_id is None:
            return
        try:
            produtos.alternar_esgotado(produto_id)
        except ValueError as e:
            erro(self, str(e))
            return
        self.carregar(produto_id)

    def remover(self):
        produto_id = id_selecionado(self.tabela)
        if produto_id is None:
            return
        produto = produtos.obter(produto_id)
        if confirmar(self, f"Remover '{produto['nome']}' da lista?"):
            produtos.remover(produto_id)
            self.carregar()


class AbaRecebedor(QWidget):
    def __init__(self):
        super().__init__()
        self.campo_chave = QLineEdit()
        self.campo_chave.setPlaceholderText("CPF, CNPJ, e-mail, telefone ou chave aleatória")
        self.campo_nome = QLineEdit()
        self.campo_cidade = QLineEdit()
        botao_salvar = QPushButton("Salvar")
        botao_salvar.setObjectName("primario")

        formulario = QFormLayout()
        formulario.addRow("Chave Pix", self.campo_chave)
        formulario.addRow("Nome do recebedor", self.campo_nome)
        formulario.addRow("Cidade", self.campo_cidade)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botao_salvar)
        layout.addStretch()

        botao_salvar.clicked.connect(self.salvar)
        self.carregar()

    def carregar(self):
        dados = recebedor.obter()
        if dados:
            self.campo_chave.setText(dados["chave_pix"])
            self.campo_nome.setText(dados["nome"])
            self.campo_cidade.setText(dados["cidade"])

    def salvar(self):
        try:
            recebedor.salvar(
                self.campo_chave.text(),
                self.campo_nome.text(),
                self.campo_cidade.text(),
            )
        except ValueError as e:
            erro(self, str(e))
            return
        for campo in (self.campo_chave, self.campo_nome, self.campo_cidade):
            campo.setStyleSheet(f"border: 1px solid {COR_OK};")


class JanelaAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin")
        self.resize(680, 480)

        self.abas = QTabWidget()
        self.abas.addTab(AbaProdutos(), "Produtos")
        self.abas.addTab(AbaRecebedor(), "Recebedor")

        layout = QVBoxLayout(self)
        layout.addWidget(self.abas)

    def abrir_aba_recebedor(self):
        self.abas.setCurrentIndex(1)
