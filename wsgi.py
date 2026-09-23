"""Adaptador WSGI del mismo enrutador, para Gunicorn en alojamiento Linux."""
import io
from email.message import Message
from http import HTTPStatus
from types import SimpleNamespace
from server import Handler, init, PUBLIC_ORIGIN

if not PUBLIC_ORIGIN:
    raise RuntimeError('El modo alojamiento requiere PUBLIC_ORIGIN HTTPS y contraseña. Para modo local usa server.py.')

init()

class WSGIHandler(Handler):
    def __init__(self,environ):
        self.path=environ.get('PATH_INFO','/')
        self.headers=Message()
        for k,v in environ.items():
            if k.startswith('HTTP_'): self.headers[k[5:].replace('_','-')]=v
        for key in ('CONTENT_TYPE','CONTENT_LENGTH'):
            if environ.get(key): self.headers[key.replace('_','-')]=environ[key]
        self.rfile=environ['wsgi.input']
        self.wfile=io.BytesIO()
        self.connection=SimpleNamespace(settimeout=lambda _:None)
        self.response_headers=[]
        self.handle_request(environ['REQUEST_METHOD'])
    def send_response(self,status): self.status=status
    def send_header(self,key,value): self.response_headers.append((key,value))
    def end_headers(self): pass

def application(environ,start_response):
    request=WSGIHandler(environ)
    start_response(f'{request.status} {HTTPStatus(request.status).phrase}',request.response_headers)
    return [request.wfile.getvalue()]
