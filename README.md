# Sistema de Pedidos — Cantina IFSP CJO

Trabalho Final — 3º Bimestre

Sistema desktop em **Python + PySide6 + SQLite** para resolver o tumulto na
cantina do IFSP CJO nos horários de maior demanda. Permite registrar pedidos
em um totem, controlar a fila de entrega, gerenciar pagamentos (Pix e dinheiro)
e acompanhar as receitas do dia.

---

## Contexto

Nos intervalos, a cantina do IFSP CJO fica sobrecarregada: alunos se
aglomeram no balcão, pedidos se misturam e o controle do que foi pago, do
que ainda está pendente e do que já foi entregue vira bagunça. O gestor
(Pablo) não tem como saber quanto vendeu no dia sem contar tudo no papel.

Este projeto propõe uma solução simples, **offline** e de baixo custo,
que organiza o fluxo da cantina em três telas:

- **Pedidos** — totem onde o operador monta o carrinho e escolhe a forma de pagamento.
- **Recebedor** — fila de pedidos, com status, beep de novo pedido e fechamento do dia.
- **Admin** — cadastro de produtos (com estoque opcional) e dados do recebedor Pix.

---

## Funcionalidades

### Tela de Pedidos (totem)
- Lista de produtos com preço; duplo clique adiciona ao carrinho.
- Produto esgotado aparece em cinza e não pode ser adicionado.
- Produto com estoque mostra "(restam N)" e bloqueia quantidade acima do disponível.
- Botões **Pagar com Pix** (gera QR Code) e **Pagar em dinheiro** (calcula troco).

### Tela do Recebedor
- Fila de pedidos com filtro por status (`PENDENTE`, `PAGO`, `CANCELADO`).
- Novo pedido dispara **beep** e destaca a linha até ser clicada.
- Marcar como PAGO, cancelar pedido e ver QR Code (só Pix).
- **Fechamento do dia**: totais por forma de pagamento, produtos vendidos e
  exportação em CSV (abre direto no Excel).

### Tela Admin
- **Produtos**: cadastrar, editar, remover e alternar ESGOTADO/DISPONÍVEL.
  Estoque é opcional — sem quantidade, o controle é manual.
- **Recebedor**: chave Pix, nome e cidade (usados para gerar o BR Code).

### Pagamento Pix
- Payload BR Code + CRC16 gerado **localmente**, sem API bancária.
- QR Code salvo em `assets/qrcodes/` e copia-e-cola disponível na tela.

---

## Como rodar

Requisitos: **Python 3.10+**.

```bash
pip install -r requirements.txt
python main.py