"""Copia consistente de SQLite (incluye fotos). Destino explícito fuera del servidor web."""
import os,sqlite3,sys
from pathlib import Path
root=Path(__file__).resolve().parent
source=Path(os.environ.get('ARMARIO_DATA_DIR',str(root/'data')))/'armario.sqlite3'
if len(sys.argv)!=2: raise SystemExit('Uso: python backup.py ruta/de/copia.sqlite3')
target=Path(sys.argv[1]).resolve()
if source.resolve()==target: raise SystemExit('El destino no puede ser la base de datos original.')
if not source.exists(): raise SystemExit('No existe la base de datos.')
target.parent.mkdir(parents=True,exist_ok=True)
src=sqlite3.connect(source);dst=sqlite3.connect(target)
try:
    src.backup(dst)
    if os.name!='nt':os.chmod(target,0o600)
finally:dst.close();src.close()
print('Copia guardada:',target)
