"""Genera un hash; nunca guarda ni imprime la contraseña."""
import getpass,hashlib,secrets
password=getpass.getpass('Contraseña del armario (mínimo 12 caracteres): ')
if len(password)<12: raise SystemExit('Usa al menos 12 caracteres.')
if password!=getpass.getpass('Repite la contraseña: '): raise SystemExit('No coinciden.')
salt=secrets.token_bytes(16)
print('ARMARIO_PASSWORD_HASH='+salt.hex()+':'+hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000).hex())
