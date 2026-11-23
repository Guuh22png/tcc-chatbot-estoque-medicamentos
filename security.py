import hashlib, hmac, os

def gerar_hash(senha: str) -> str:
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 100_000)
    return salt.hex() + "$" + h.hex()

def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        salt_hex, h_hex = armazenado.split("$")
    except ValueError:
        return False
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(salt_hex), 100_000)
    return hmac.compare_digest(h.hex(), h_hex)