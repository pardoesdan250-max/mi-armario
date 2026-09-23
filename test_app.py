"""Pruebas de integración reales contra un servidor aislado; no llama a Gemini."""
import base64, io, json, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from PIL import Image

ROOT=Path(__file__).resolve().parent
class Flows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        env=dict(os.environ,ARMARIO_DATA_DIR=cls.temp.name,PORT='8766',GEMINI_API_KEY='')
        cls.env=env
        cls.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py')],env=env,stdout=subprocess.DEVNULL)
        for _ in range(60):
            try:
                cls.state=cls.req('/api/state');break
            except Exception: time.sleep(.1)
        else: raise RuntimeError('Servidor no disponible')
        cls.token=cls.state['token']
    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate();cls.proc.wait();cls.temp.cleanup()
    @classmethod
    def req(cls,path,method='GET',body=None,headers=None):
        h={'Content-Type':'application/json','X-Armario-Token':getattr(cls,'token','')};h.update(headers or {})
        r=Request('http://127.0.0.1:8766'+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers=h)
        with urlopen(r,timeout=10) as res:
            data=res.read()
            return json.loads(data) if res.headers['Content-Type']=='application/json' else data
    def test_complete_flow(self):
        image=base64.b64encode((ROOT/'examples/shirt.png').read_bytes()).decode()
        data=dict(name='Prueba subida',category='parte superior',color='blanco',season='todo el año',tags='diario',description='',photo=image)
        added=self.req('/api/garments','POST',data)
        data['name']='Nombre corregido'; data['color']='blanco roto'
        self.req('/api/garments/'+added['id'],'PUT',data)
        state=self.req('/api/state');self.assertEqual(next(g for g in state['garments'] if g['id']==added['id'])['name'],'Nombre corregido')
        outfits=self.req('/api/outfits','POST',dict(mode='rules',occasion='diario',weather='templado',preferences=''))['outfits']
        ids={g['id'] for g in state['garments']}
        self.assertTrue(all(set(o['items'])<=ids for o in outfits))
        outfit=next(o for o in outfits if added['id'] in o['items'])
        self.req('/api/favorites/'+outfit['id'],'POST',{})
        self.assertIn(outfit['id'],[o['id'] for o in self.req('/api/state')['favorites']])
        # Un reinicio real conserva datos y favoritos; rota el token de sesión.
        self.__class__.proc.terminate();self.__class__.proc.wait()
        self.__class__.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py')],env=self.env,stdout=subprocess.DEVNULL)
        for _ in range(60):
            try: state=self.req('/api/state');break
            except Exception:time.sleep(.1)
        self.__class__.token=state['token']
        self.assertIn(outfit['id'],[o['id'] for o in state['favorites']])
        self.req('/api/garments/'+added['id'],'DELETE')
        state=self.req('/api/state');self.assertNotIn(added['id'],[g['id'] for g in state['garments']]);self.assertNotIn(outfit['id'],[o['id'] for o in state['favorites']])
        with self.assertRaises(HTTPError) as e:self.req('/photo/'+added['id'])
        self.assertEqual(e.exception.code,404)
    def test_security_and_validation(self):
        for headers in [{'Host':'evil.example'},{'Origin':'https://evil.example'},{'Sec-Fetch-Site':'cross-site'}]:
            with self.assertRaises(HTTPError) as e:self.req('/api/state',headers=headers)
            self.assertEqual(e.exception.code,403)
        with self.assertRaises(HTTPError) as e:self.req('/api/garments','POST',{},headers={'X-Armario-Token':'bad'})
        self.assertEqual(e.exception.code,403)
        for path in ['/.env','/data/armario.sqlite3','/../server.py']:
            with self.assertRaises(HTTPError) as e:self.req(path)
            self.assertEqual(e.exception.code,404)
        info=dict(name='Test',category='parte superior',color='blanco',season='todo el año',description='',tags='')
        for raw in [b'<svg><script>alert(1)</script></svg>',b'not a photo',b'x'*(8*1024*1024+1)]:
            with self.assertRaises(HTTPError) as e:self.req('/api/garments','POST',dict(info,photo=base64.b64encode(raw).decode()))
            self.assertIn(e.exception.code,[400,413])
        with self.assertRaises(HTTPError) as e:self.req('/api/classify','POST',dict(photo=base64.b64encode((ROOT/'examples/shirt.png').read_bytes()).decode(),consent=True))
        self.assertEqual(e.exception.code,503)
        with self.assertRaises(HTTPError) as e:self.req('/api/favorites/'+'0'*24,'POST',{})
        self.assertEqual(e.exception.code,404)
    def test_image_metadata_removed(self):
        im=Image.new('RGB',(120,120),'white');exif=Image.Exif();exif[270]='PRIVATE';out=io.BytesIO();im.save(out,'JPEG',exif=exif)
        g=self.req('/api/garments','POST',dict(name='Metadatos',category='accesorio',color='blanco',season='todo el año',tags='',description='',photo=base64.b64encode(out.getvalue()).decode()))
        with Image.open(io.BytesIO(self.req('/photo/'+g['id']))) as cleaned:self.assertFalse(cleaned.getexif())
        self.req('/api/garments/'+g['id'],'DELETE')
    def test_delete_examples_persists(self):
        self.req('/api/examples','DELETE');self.assertFalse(any(g.get('example') for g in self.req('/api/state')['garments']))

if __name__=='__main__':unittest.main(verbosity=2)
