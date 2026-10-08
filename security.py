import hashlib
import hmac
import os
import secrets
import threading

_ITERATIONS = 100_000
_tokens = {}
_verrou = threading.Lock()


def hash_mot_de_passe(mot_de_passe):
    sel = secrets.token_hex(16)
    empreinte = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode(), bytes.fromhex(sel), _ITERATIONS
    ).hex()
    return f"{sel}:{empreinte}"


def verifier_mot_de_passe(mot_de_passe, stocke):
    try:
        sel, empreinte = stocke.split(":", 1)
    except ValueError:
        return False
    calcule = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode(), bytes.fromhex(sel), _ITERATIONS
    ).hex()
    return hmac.compare_digest(calcule, empreinte)


def creer_token(email):
    token = secrets.token_hex(24)
    with _verrou:
        _tokens[token] = email
    return token


def email_par_token(token):
    with _verrou:
        return _tokens.get(token)


# Mots de passe de démonstration hashes (pré-calculés, salt aléatoire par défaut)
def demarrer():
    os.environ.setdefault("GMAO_API_KEY", "gmao-dev-key")
    os.environ.setdefault("GMAO_API_URL", "http://127.0.0.1:8000")