# Prompt — Sistema de Pedidos para Cantina Escolar (Pix + Dinheiro)

Use este documento como especificação do projeto. Ele já inclui as decisões tomadas.

## 1. Contexto

Sistema **simples** para a cantina de uma escola, usado no balcão durante o recreio, com fila e pouco tempo por cliente.

- Um único computador (ou dois, sem rede), **offline**, sem servidor.
- 1 ou 2 operadores sem conhecimento técnico.
- Poucas dezenas de produtos (lanches, salgados, bebidas, doces) com preços baixos.
- O aluno paga por **Pix** (QR Code ou Copia e Cola) ou em **dinheiro**.
- Sem login, sem nota fiscal e sem integração bancária nesta versão.

## 2. Decisões tomadas

| Pergunta | Decisão |
|---|---|
| Aceitar dinheiro além do Pix? | **Sim.** Pedido em dinheiro nasce como PAGO, com cálculo de troco. |
| Reiniciar a numeração dos pedidos a cada dia? | **Não.** A numeração é contínua. |
| Estoque por quantidade? | **Opcional, por produto.** Sem quantidade, o controle é só manual (Disponível / ESGOTADO). |
| Fechamento do dia? | **Sim.** Totais por forma de pagamento, produtos vendidos e exportação CSV. |

## 3. Stack e restrições

- Python 3.10+, **PySide6**, **SQLite**, `qrcode[pil]`.
- Payload Pix (BR Code + CRC16) gerado localmente, sem biblioteca externa e sem API bancária.
- Código enxuto: poucos comentários, nomes claros, funções pequenas, um arquivo por responsabilidade.

## 4. Arquitetura

```
main.py            abre as 3 janelas
config.py          caminhos e constantes
db.py              conexão, criação das tabelas e migração
core/              regras de negócio, sem interface
  produtos.py      criar, editar, esgotar, remover, estoque
  pedidos.py       criar (Pix ou dinheiro), listar, pagar, cancelar
  recebedor.py     dados de quem recebe
  pix.py           payload BR Code + CRC16 + imagem do QR
  relatorios.py    fechamento do dia e exportação CSV
ui/                PySide6, uma janela ou diálogo por arquivo
```

Regras:
1. `core/` nunca importa `ui/`.
2. `ui/` nunca escreve SQL; sempre chama `core/`.
3. As janelas só se comunicam pelo banco, com atualização a cada 2 s (`QTimer`).
4. Um único `QApplication`.

## 5. Requisitos por janela

### 5.1 Admin
- **Produtos:** cadastrar (nome, preço, estoque opcional), editar, remover, alternar ESGOTADO.
- Estoque "Sem controle" é o padrão. Com quantidade informada, o produto passa a ser controlado.
- **Recebedor:** chave Pix, nome e cidade.

### 5.2 Pedidos (balcão)
- Lista de produtos e carrinho lado a lado; duplo clique adiciona.
- Produto ESGOTADO aparece em cinza e não pode ser adicionado.
- Produto com estoque mostra "(restam N)" e não permite passar da quantidade disponível.
- Se o produto esgotar ou o estoque diminuir com item no carrinho, o carrinho é ajustado com aviso.
- Dois botões de pagamento:
  - **Pagar com Pix:** gera o pedido PENDENTE e mostra QR Code, Copia e Cola e número do pedido.
  - **Pagar em dinheiro:** pede o valor recebido, calcula o troco e registra o pedido como PAGO.
- O número do pedido serve de senha para chamar o aluno.

### 5.3 Recebedor
- Tabela: pedido, valor, forma, status, hora. Filtro por status.
- Ações: marcar como PAGO, cancelar, ver QR Code (só Pix).
- Pedido novo: beep, aviso e linha destacada até ser clicada.
- **Fechamento do dia:** escolhe a data (padrão hoje) e mostra total vendido, Pix, dinheiro, cancelados, pendentes e produtos vendidos. Botão **Exportar CSV**.

## 6. Regras de negócio

- Valor do pedido calculado no `core`: soma de `preço × quantidade`.
- O pedido guarda nome e preço do momento da venda.
- Estados do produto: `DISPONIVEL`, `ESGOTADO`, `REMOVIDO`.
- Estados do pedido: `PENDENTE` → `PAGO` ou `CANCELADO`. Só pedido PENDENTE pode ser pago ou cancelado.
- Estoque controlado:
  - a venda baixa a quantidade; ao chegar a zero, o produto vira ESGOTADO sozinho;
  - cancelar um pedido devolve a quantidade; se estava zerado, volta a DISPONIVEL;
  - com estoque zerado, "Esgotado / Disponível" pede para informar a nova quantidade em Editar;
  - editar o estoque para um valor maior que zero libera o produto; para zero, esgota.
- O fechamento soma **apenas pedidos PAGOS** do dia; pendentes aparecem em aviso.
- CSV: separador `;`, vírgula decimal, codificação compatível com Excel em português.

## 7. Requisitos não funcionais

- Pedido comum em no máximo 3 ações.
- Botões e total grandes, cores claras por status.
- Confirmação ao remover produto; mensagens em português simples.
- Nada se perde se o programa fechar (tudo no SQLite); bancos antigos são migrados automaticamente.

## 8. Fora do escopo (versão 1)

Login e permissões, cartão, integração com API bancária, confirmação automática de pagamento, impressão, fiado, cancelamento de pedido já pago.

## 9. Critérios de aceite

1. Cadastro do recebedor e de produtos, com e sem estoque, funciona.
2. Marcar ESGOTADO bloqueia a venda em até 2 s, sem reiniciar.
3. Pedido Pix de 3 itens gera QR Code com o valor exato e CRC16 válido.
4. Pedido em dinheiro calcula o troco, entra como PAGO e não gera QR Code.
5. Vender a última unidade de um produto com estoque o marca como ESGOTADO.
6. Cancelar um pedido Pix pendente devolve o estoque.
7. O pedido aparece sozinho na janela Recebedor, com beep.
8. O fechamento do dia bate com os pedidos pagos e o CSV abre no Excel.
9. Fechar e abrir o programa mantém produtos e pedidos.

## 10. Próximas ideias

Cancelamento de venda em dinheiro com motivo, relatório por período, impressão da senha, backup automático do `pedidos.db`.
