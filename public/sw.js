// Solo se conserva la pantalla sin conexión y los iconos. Nunca fotos, API ni HTML del armario.
const CACHE='mi-armario-public-v2';
const PUBLIC=['/offline.html','/offline.css','/icon-192.png','/icon-512.png','/icon-180.png'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(PUBLIC)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('mi-armario-public-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(url.origin!==self.location.origin||event.request.method!=='GET')return;
 if(event.request.mode==='navigate')event.respondWith(fetch(event.request).catch(()=>caches.match('/offline.html')));
 else if(PUBLIC.includes(url.pathname))event.respondWith(caches.match(event.request).then(hit=>hit||fetch(event.request)));
});
