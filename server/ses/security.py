import secrets
from cryptography.fernet import Fernet

def sessionid():
    session_id = secrets.token_hex(50)

    return session_id

def csrfid():
    csrf_id = secrets.token_hex(55)

    return csrf_id


def generate_key():
    key = Fernet.generate_key()
    return key

def encrypt_token(token, key):
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(token.encode())
    return encrypted_token

def decrypt_token(encrypted_token, key):
    fernet = Fernet(key)
    decrypted_token = fernet.decrypt(encrypted_token)
    return decrypted_token.decode()

