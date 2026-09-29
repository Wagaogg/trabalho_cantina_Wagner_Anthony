import unicodedata

import qrcode

from config import QR_DIR


def _tlv(codigo, valor):
    return f"{codigo}{len(valor):02d}{valor}"


def _ascii(texto, limite):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()[:limite]


def _crc16(texto):
    crc = 0xFFFF
    for byte in texto.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return f"{crc:04X}"


def gerar_payload(chave, nome, cidade, valor, txid):
    conta = _tlv("00", "br.gov.bcb.pix") + _tlv("01", chave)
    corpo = (
        _tlv("00", "01")
        + _tlv("01", "12")
        + _tlv("26", conta)
        + _tlv("52", "0000")
        + _tlv("53", "986")
        + _tlv("54", f"{valor:.2f}")
        + _tlv("58", "BR")
        + _tlv("59", _ascii(nome, 25))
        + _tlv("60", _ascii(cidade, 15))
        + _tlv("62", _tlv("05", txid))
        + "6304"
    )
    return corpo + _crc16(corpo)


def salvar_qrcode(payload, nome_arquivo):
    QR_DIR.mkdir(parents=True, exist_ok=True)
    caminho = QR_DIR / f"{nome_arquivo}.png"
    qrcode.make(payload).save(caminho)
    return caminho
