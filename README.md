# Mi Armario

Armario digital en español, adaptable a móvil y preparado como PWA para Android y iPhone.

- Guarda fotos y datos de tus prendas y edítalos cuando quieras.
- Crea conjuntos con prendas existentes y guarda favoritos.
- Usa Gemini opcionalmente para clasificar fotos y sugerir conjuntos.
- Sin clave, organiza el armario y combina mediante reglas identificadas como sin IA.
- SQLite persistente, validación de imágenes y eliminación de metadatos.

## Empezar

Requiere Python 3.11 o posterior.

```sh
python -m pip install -r requirements.txt
python server.py
```

Abre http://127.0.0.1:8765. Esta versión local escucha solo en tu ordenador.

Lee [las instrucciones](INSTRUCCIONES.md) para configurar Gemini y conocer costes, límites y privacidad. Consulta [la guía de publicación](PUBLICAR.md) para Docker, HTTPS, contraseña, copias e instalación móvil.

## Alcance

Una sola persona y un solo armario. El alojamiento preparado permite acceder desde varios dispositivos con la misma contraseña; no proporciona cuentas independientes. La PWA necesita conexión para consultar y modificar prendas.

Las imágenes incluidas representan prendas ficticias de ejemplo y fueron generadas con IA. No se incluyen datos personales ni claves.

## Pruebas

```sh
python test_app.py
python test_hosting.py
```

No se ha verificado una llamada real a Gemini ni la instalación en teléfonos físicos. El alojamiento Docker/HTTPS debe verificarse en el servidor final.
