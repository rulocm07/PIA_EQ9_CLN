"""Genera un hash PBKDF2 para .env. No sube ni registra el PIN en el proyecto."""
import getpass
import hashlib
import secrets

if __name__ == '__main__':
    pin=getpass.getpass('Elige un PIN de Administración (mínimo 6 caracteres): ')
    if len(pin)<6: raise SystemExit('Utiliza al menos 6 caracteres')
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256',pin.encode(),salt,250000)
    print("ADMIN_PIN_HASH='250000$"+salt.hex()+'$'+digest.hex()+"'")
    print('Guarda la línea anterior SOLO en .env o variables de entorno del despliegue.')
