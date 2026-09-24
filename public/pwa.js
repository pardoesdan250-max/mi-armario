let installEvent;
const installButton=document.querySelector('#installApp');
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();installEvent=event;if(installButton)installButton.hidden=false});
installButton?.addEventListener('click',async()=>{if(!installEvent)return;await installEvent.prompt();await installEvent.userChoice;installEvent=null;installButton.hidden=true});
window.addEventListener('appinstalled',()=>{installEvent=null;if(installButton)installButton.hidden=true});
if('serviceWorker' in navigator&&window.isSecureContext){navigator.serviceWorker.register('/sw.js',{scope:'/'}).catch(()=>{const status=document.querySelector('#pwaStatus');if(status)status.textContent='No se pudo preparar la pantalla sin conexión. Puedes seguir usando la web.'})}
const connectivity=document.querySelector('#connectivity');
function onlineStatus(){if(connectivity){connectivity.hidden=navigator.onLine;connectivity.textContent='Sin conexión. No se guardarán cambios hasta que vuelva la conexión con el servidor.'}}
window.addEventListener('online',onlineStatus);window.addEventListener('offline',onlineStatus);onlineStatus();
