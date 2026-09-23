"""Comprueba el adaptador de producción, autenticación y recursos PWA sin publicar."""
import hashlib,io,json,os,secrets,tempfile,unittest
from pathlib import Path
temp=tempfile.TemporaryDirectory()
password=secrets.token_urlsafe(18)
salt=secrets.token_bytes(16)
os.environ.update(PUBLIC_ORIGIN='https://armario.example',ARMARIO_DATA_DIR=temp.name,ARMARIO_PASSWORD_HASH=salt.hex()+':'+hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000).hex(),GEMINI_API_KEY='')
from wsgi import application

def call(path,method='GET',data=None,headers=None):
    raw=json.dumps(data).encode() if data is not None else b''
    env={'PATH_INFO':path,'REQUEST_METHOD':method,'wsgi.input':io.BytesIO(raw),'HTTP_HOST':'armario.example','CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw))}
    env.update(headers or {})
    result={}
    def start(status,h):result.update(status=int(status.split()[0]),headers=dict(h))
    result['body']=b''.join(application(env,start));return result

class Hosting(unittest.TestCase):
    def test_auth_session_and_pwa(self):
        self.assertEqual(call('/api/state')['status'],401)
        self.assertEqual(call('/photo/'+'a'*24)['status'],401)
        self.assertIn(b'loginForm',call('/')['body'])
        self.assertEqual(call('/api/login','POST',{'password':password},{'HTTP_ORIGIN':'https://evil.example'})['status'],403)
        self.assertEqual(call('/api/login','POST',{'password':'incorrecta'})['status'],401)
        login=call('/api/login','POST',{'password':password});self.assertEqual(login['status'],200)
        cookie=login['headers']['Set-Cookie'];self.assertIn('HttpOnly',cookie);self.assertIn('Secure',cookie);self.assertIn('SameSite=Strict',cookie)
        headers={'HTTP_COOKIE':cookie.split(';')[0]}
        state=json.loads(call('/api/state',headers=headers)['body']);self.assertTrue(state['hosted'])
        self.assertIn(b'outfitForm',call('/',headers=headers)['body'])
        headers['HTTP_X_ARMARIO_TOKEN']=state['token']
        self.assertEqual(call('/api/logout','POST',{},headers)['status'],200)
        self.assertEqual(call('/api/state',headers=headers)['status'],401)
        for path in ['/manifest.webmanifest','/sw.js','/offline.html','/offline.css','/icon-192.png','/icon-512.png','/icon-180.png']:
            self.assertEqual(call(path)['status'],200,path)
        manifest=json.loads(call('/manifest.webmanifest')['body']);self.assertEqual(manifest['display'],'standalone');self.assertEqual(manifest['scope'],'/')
        for path in ['/data/armario.sqlite3','/.env','/.env.hosting']:
            self.assertEqual(call(path)['status'],404)
        from PIL import Image
        for size in (180,192,512):
            with Image.open(io.BytesIO(call(f'/icon-{size}.png')['body'])) as im:self.assertEqual(im.size,(size,size))
        self.assertNotIn(password.encode(),call('/app.js')['body'])
    def test_rate_limit(self):
        from server import LOGIN_ATTEMPTS
        LOGIN_ATTEMPTS.clear()
        for _ in range(5):self.assertEqual(call('/api/login','POST',{'password':'wrong'})['status'],401)
        self.assertEqual(call('/api/login','POST',{'password':password})['status'],429)
    def test_reject_unknown_garments(self):
        from server import validate_outfit,Problem
        with self.assertRaises(Problem):validate_outfit({'name':'Incorrecto','items':['no-existe','otro'],'explanation':'Inventado'},[])

if __name__=='__main__':
    try:unittest.main(verbosity=2)
    finally:temp.cleanup()
