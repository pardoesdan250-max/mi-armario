# Publicar Mi Armario e instalarlo en Android y iPhone

Esta preparación es para **un único propietario**, con un solo armario accesible desde sus dispositivos. La contraseña da acceso a todas las prendas. No compartas la instalación con terceros como si cada uno tuviera su propia cuenta: antes haría falta implementar usuarios, propiedad de registros, autorización por usuario y recuperación de cuentas.

No se ha desplegado la app ni contratado alojamiento. La publicación necesita un servidor Linux permanente con Docker Compose, un dominio o subdominio, disco persistente y acceso a los puertos 80/443. Un alojamiento estático no puede ejecutar esta app. El coste depende del servidor, dominio, almacenamiento y copias elegidos; Gemini se factura por separado si activas un plan de pago.

## 1. Preparar el servidor y el dominio

1. Instala Docker Engine y el complemento Compose siguiendo la [documentación oficial](https://docs.docker.com/engine/install/).
2. Crea un registro DNS **A** para `armario.tudominio.com` que apunte a la IP pública del servidor. Si añades AAAA, debe apuntar a una IPv6 que funcione.
3. Permite TCP 80 y 443 en el cortafuegos; UDP 443 es opcional. Limita SSH a tus IP si es posible. **No abras el puerto 8000 ni 8765 al exterior.**
4. Copia esta carpeta al servidor, por ejemplo a `/opt/mi-armario`. Excluye `.env`, `data`, `.venv`, `__pycache__` y copias privadas. No uses un repositorio público para transferir secretos o tu base de datos.

## 2. Configurar el acceso privado

En la carpeta del servidor:

```sh
cp .env.hosting.example .env.hosting
python3 make_password.py
```

Introduce una contraseña larga y única dos veces. El programa imprime una línea `ARMARIO_PASSWORD_HASH=...`; copia su valor en `.env.hosting`. La contraseña no se imprime ni se guarda. Si el servidor no tiene Python, genera el hash en tu ordenador y transfiere únicamente el hash.

Edita `.env.hosting`:

```dotenv
DOMAIN=armario.tudominio.com
ARMARIO_PASSWORD_HASH=el_hash_generado
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
```

`DOMAIN` no lleva `https://`, puerto ni barra final. Puedes dejar Gemini vacío. Guarda el archivo fuera de Git y limita su acceso:

```sh
chmod 600 .env.hosting
```

Las contraseñas se verifican con PBKDF2-SHA256 y sal aleatoria. La cookie tiene `Secure`, `HttpOnly`, `SameSite=Strict` y caduca a los siete días. Hay un límite global de cinco intentos por minuto. Reiniciar el servidor invalida todas las sesiones. No hay recuperación por email: para cambiar la contraseña, genera otro hash y recrea el contenedor.

## 3. Iniciar el alojamiento

```sh
docker compose --env-file .env.hosting up -d --build
docker compose --env-file .env.hosting ps
docker compose --env-file .env.hosting logs --tail=80 app caddy
```

Abre **https://armario.tudominio.com**. Caddy obtiene y renueva el certificado HTTPS automáticamente si el DNS y los puertos están correctos. Gunicorn ejecuta la app dentro de la red privada de Docker; su puerto no se publica. [HTTPS automático de Caddy](https://caddyserver.com/docs/automatic-https).

La imagen se ejecuta con un usuario sin privilegios. El volumen `armario_data` conserva SQLite y fotos aunque recrees el contenedor. `restart: unless-stopped` recupera los servicios tras reiniciar el servidor, siempre que Docker arranque automáticamente.

Mantén **un worker de Gunicorn** y una réplica de la app: las sesiones y el token de protección se mantienen en memoria del proceso. Los cuatro hilos atienden peticiones concurrentes. Escalar a varios procesos requeriría almacenamiento compartido de sesiones y controles adicionales.

No uses `python server.py` como servidor público: es el modo local. No quites el requisito de contraseña ni el HTTPS. El arranque alojado rechaza una contraseña hash vacía o mal formada.

## 4. Verificar antes de usar tus fotos

1. En una ventana privada, abre la URL: debe aparecer la contraseña y nunca las prendas.
2. Sin iniciar sesión, `/api/state` debe responder 401. Las fotos también deben requerir sesión. `/.env`, `/.env.hosting` y `/data/armario.sqlite3` deben responder 404.
3. Entra, sube una prenda de prueba, edítala, crea un conjunto, guárdalo como favorito y recarga.
4. Reinicia la app con `docker compose --env-file .env.hosting restart app`. Vuelve a entrar y confirma que los datos siguen ahí.
5. Comprueba el acceso desde Android y iPhone mediante la URL HTTPS y realiza la instalación indicada abajo.
6. Abre la app instalada, desconecta la red y vuelve a abrirla: debe aparecer la pantalla sin conexión. No se muestran fotos privadas cacheadas. Reconecta y pulsa «Volver a intentar».
7. En «Privacidad e IA», pulsa «Cerrar sesión». Comprueba que el armario vuelve a requerir contraseña.

## 5. Instalar como app

### Android

Abre la URL HTTPS en Chrome. En «Privacidad e IA», pulsa **Instalar Mi Armario** si aparece. Si no, abre el menú del navegador y selecciona **Instalar aplicación** o **Añadir a pantalla de inicio**. El texto depende de la versión del navegador. La instalación se completa desde el aviso del sistema.

### iPhone

Abre la URL HTTPS en Safari. Pulsa **Compartir → Añadir a pantalla de inicio**. Activa **Abrir como app web** si aparece y pulsa **Añadir**. Abre el icono y, si se solicita, introduce de nuevo la contraseña.

En iOS no se usa el botón programático de instalación de Android. El manifiesto y los iconos permiten abrir la app de forma independiente; HTTPS es necesario fuera de localhost. [Requisitos PWA](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable), [guía de Apple](https://support.apple.com/guide/iphone/bookmark-a-website-iph42ab2f3a7/ios).

La dirección `127.0.0.1` de tu ordenador no sirve desde el teléfono: en cada dispositivo apunta a ese mismo dispositivo. Usa la dirección HTTPS del alojamiento.

## 6. Copias de seguridad y migración

Todas las fotos y registros están en un solo SQLite. Para obtener una copia consistente mientras está en uso:

```sh
docker compose --env-file .env.hosting exec app python backup.py /data/backup.sqlite3
mkdir -p backups
docker compose --env-file .env.hosting cp app:/data/backup.sqlite3 backups/armario.sqlite3
chmod 600 backups/armario.sqlite3
```

Guarda una copia fechada y cifrada fuera del servidor. Programa copias periódicas en tu sistema de alojamiento y prueba una restauración. La copia contiene fotos privadas y prendas borradas después de hacerla. No está cifrada por la app.

Para migrar desde tu ordenador, detén el servidor local y copia `data/armario.sqlite3` de forma privada al servidor. Para restaurar una copia, detén primero la app, conserva una copia del estado actual y sustituye el archivo del volumen:

```sh
docker compose --env-file .env.hosting stop app
docker compose --env-file .env.hosting cp backups/armario.sqlite3 app:/data/armario.sqlite3
docker compose --env-file .env.hosting run --rm --user root app chown 10001:10001 /data/armario.sqlite3
docker compose --env-file .env.hosting start app
```

El archivo reemplaza el armario completo. Comprueba prendas y favoritos tras restaurar. No ejecutes `docker compose down -v`: borraría los volúmenes persistentes.

## 7. Actualizaciones y operación

Haz una copia antes de actualizar. Copia los nuevos archivos de código sin sobrescribir `.env.hosting` y ejecuta:

```sh
docker compose --env-file .env.hosting up -d --build
```

Si actualizas la pantalla offline o los iconos, cambia también la versión de caché en `public/sw.js`. La app usa la red para el contenido principal y no mantiene una copia antigua del armario. Reabre la PWA para cargar los cambios.

Mantén Docker, el sistema y las dependencias actualizados. Comprueba espacio libre, disponibilidad, copias y renovación de certificados. El paquete de Docker y el certificado final no se han ejecutado aquí; las pruebas locales verifican el mismo enrutador WSGI, la autenticación y los recursos PWA.
