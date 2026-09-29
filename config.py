from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pedidos.db"
QR_DIR = BASE_DIR / "assets" / "qrcodes"

POLL_MS = 2000

STATUS_PENDENTE = "PENDENTE"
STATUS_PAGO = "PAGO"
STATUS_CANCELADO = "CANCELADO"

FORMA_PIX = "PIX"
FORMA_DINHEIRO = "DINHEIRO"
