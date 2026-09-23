# Mi Armario

App en español para guardar prendas y fotos, revisar sugerencias de Gemini, crear hasta tres conjuntos y guardar favoritos. Incluye tres prendas ficticias de ejemplo, con imágenes generadas, que puedes borrar.

## Ejecutar localmente

Necesitas Python 3.11 o posterior (recomendado 3.12). En la carpeta de la app:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py
```

En macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python server.py
```

Abre http://127.0.0.1:8765. No hay instalación de Node ni compilación de frontend.

## Configurar Gemini

1. Crea una clave en [Google AI Studio](https://aistudio.google.com/apikey).
2. Copia `.env.example` como `.env` en esta carpeta.
3. Edita el archivo localmente:

```dotenv
GEMINI_API_KEY=tu_clave_real
GEMINI_MODEL=gemini-2.5-flash-lite
PORT=8765
```

4. Reinicia el servidor y recarga la página. También puedes definir estas variables en el entorno del proceso; tienen prioridad sobre `.env`.
5. Al importar una foto, marca la autorización y pulsa «Sugerir datos con IA». Revisa los campos antes de guardar. Al crear conjuntos, selecciona Gemini y autoriza el envío de datos descriptivos.

La clave nunca se envía al navegador, no forma parte de las imágenes de Docker y está excluida del repositorio. No pegues la clave en mensajes ni subas `.env` a un servicio público.

Sin clave, siguen funcionando la importación, edición, eliminación, búsqueda, favoritos y combinaciones por reglas. Estas últimas están identificadas como **sin IA**; no analizan fotos ni preferencias libres. No se simulan respuestas de Gemini.

### Costes, límites y privacidad

Consulta realizada el 23 de septiembre de 2026. Gemini 2.5 Flash-Lite ofrece un nivel gratuito sujeto a disponibilidad y cuotas. En el nivel de pago estándar, Google publica **0,10 USD por millón de tokens de entrada de texto/imagen y 0,40 USD por millón de salida**. Como ejemplo aritmético, 2.000 tokens de entrada y 500 de salida costarían 0,0004 USD; una foto puede consumir otra cantidad. No incluye impuestos, hosting ni dominio. Esta app no usa búsquedas, caché de contexto de pago ni generación de imágenes de Gemini. [Precios oficiales](https://ai.google.dev/gemini-api/docs/pricing#gemini-2.5-flash-lite).

Los límites se aplican por proyecto y pueden considerar solicitudes/minuto, tokens/minuto y solicitudes/día. Consulta los límites vigentes de tu proyecto en AI Studio: no hay una cifra gratuita universal garantizada. Un error 429 se muestra en la interfaz; la app no reintenta automáticamente ni cambia a un modelo de pago. Activar facturación en Google puede producir cargos. [Límites oficiales](https://ai.google.dev/gemini-api/docs/rate-limits).

Google establece condiciones regionales y de uso: sus términos actuales indican servicios de pago cuando se ofrecen clientes API a usuarios del EEE, Suiza o Reino Unido, y restringen los servicios a desarrollo con fines profesionales o empresariales. Por tanto, **no se garantiza el uso gratuito de una app personal publicada en España**. Revisa la elegibilidad y las condiciones antes de activarla. Puedes usar toda la organización manual sin Gemini. [Condiciones de Gemini](https://ai.google.dev/gemini-api/terms).

En servicios gratuitos, los datos pueden usarse para mejorar productos y pasar revisión humana, con excepciones regionales descritas por Google; en EEE, Suiza y Reino Unido se aplican las condiciones de datos de los servicios de pago incluso a la cuota gratuita. No envíes fotos sensibles. La app pide autorización antes de enviar una foto; para conjuntos solo envía nombres, categorías, colores, temporadas, descripciones, etiquetas y preferencias.

## Datos y límites de esta versión

- Python + SQLite + HTML/CSS/JavaScript. Base de datos y fotos procesadas en `data/armario.sqlite3`; no dependen del almacenamiento del navegador.
- Una foto por prenda; hasta 10 fotos en una selección, revisadas de una en una. JPEG, PNG y WebP, máximo 8 MB y 25 megapíxeles. HEIC debe convertirse antes. Se eliminan metadatos y se reduce a 1.600 px como máximo.
- La generación admite hasta 300 prendas. El servidor valida los identificadores y exige un conjunto completo. Al eliminar una prenda se eliminan los conjuntos que la contienen, incluidos favoritos.
- Una sola persona/armario. El modo local escucha únicamente en 127.0.0.1; no es accesible desde el teléfono. Quien use tu misma sesión del ordenador puede acceder a él.
- La versión alojada usa una contraseña para un único propietario y varias sesiones/dispositivos. **No ofrece cuentas ni armarios separados para terceros.**
- Los datos no se cifran en disco por la app: utiliza cifrado de disco y controla el acceso al ordenador/servidor. Borrar registros no elimina copias de seguridad previas.
- Las ediciones simultáneas de la misma prenda se resuelven conservando la última guardada.

## PWA y alojamiento

Consulta **PUBLICAR.md** para Docker, dominio, HTTPS, contraseña, almacenamiento persistente, copias de seguridad e instalación en Android/iPhone. No se ha publicado ni contratado ningún servicio.

La PWA necesita conexión para leer y modificar el armario. Sin conexión muestra una pantalla informativa y no cachea fotos ni datos privados. No incluye sincronización offline ni subidas pendientes.

## Verificación

```sh
python test_app.py
python test_hosting.py
```

Las pruebas crean bases de datos temporales: no borran tu colección. Comprueban subida, edición, generación por reglas, favoritos, persistencia tras reiniciar, eliminación y limpieza de referencias; rechazos de archivos inválidos, accesos desde otros orígenes y rutas privadas; eliminación de metadatos; sesión de alojamiento, cierre de sesión, límite de intentos y recursos PWA.

La llamada real a Gemini necesita tu clave y no se ha ejecutado. El despliegue Docker/HTTPS y la instalación en dispositivos físicos deben verificarse en el alojamiento final; las pruebas locales no sustituyen esas comprobaciones.
