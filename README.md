# Proyecto ESP32 – Sensor DHT22 → Flask → Google Sheets

Sistema de monitoreo de temperatura y humedad: un **ESP32** con sensor **DHT22** mide los datos, los envía por WiFi a un **servidor Flask** local, y este los guarda automáticamente en una hoja de **Google Sheets**.

## Arquitectura

```
[ESP32 + DHT22] --WiFi (HTTP POST /datos)--> [Servidor Flask (PC)] --API-- > [Google Sheets]
```

Cada 60 segundos el ESP32 mide temperatura y humedad, y envía un JSON `{"temp": .., "hum": ..}` por HTTP a la PC, que a su vez agrega una fila nueva en el Sheet.

## Requisitos de hardware

- Placa **ESP32**
- Sensor **DHT22** conectado al pin **GPIO25**
- Cable USB para flashear y alimentar el ESP32
- PC y ESP32 conectados a la **misma red WiFi** (2.4GHz — el ESP32 no soporta 5GHz)

## Requisitos de software

- Python 3.x instalado en la PC
- [esptool](https://github.com/espressif/esptool) y [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) para flashear/subir código
- Cuenta de Google Cloud con **Google Sheets API** y **Google Drive API** habilitadas
- Una hoja de cálculo de Google Sheets llamada `esp32_datos`

## Estructura del proyecto

```
proyecto esp32/
├── esp32_codigo/
│   ├── boot.py          # Se ejecuta al arrancar el ESP32 (vacío, opcional)
│   └── main.py           # Código principal: WiFi + sensor + envío HTTP
├── server.py              # Servidor Flask: recibe datos y los guarda en Sheets
├── credenciales.json      # Llave de cuenta de servicio de Google (NO subir a git)
├── micropython.bin        # Firmware de MicroPython para flashear el ESP32
└── requirements.txt       # Dependencias
```

---

## Parte 1 — Configurar Google Sheets

1. Entra a [Google Cloud Console](https://console.cloud.google.com/) y crea un proyecto.
2. Habilita las APIs: **Google Sheets API** y **Google Drive API**.
3. Ve a **Credenciales → Crear credenciales → Cuenta de servicio**.
4. Genera una clave en formato **JSON** y descárgala. Renómbrala `credenciales.json` y colócala en la raíz del proyecto.
5. Abre el archivo `credenciales.json` y copia el valor del campo `client_email` (algo como `xxxx@xxxx.iam.gserviceaccount.com`).
6. Crea una hoja de cálculo en Google Sheets llamada exactamente `esp32_datos`.
7. Compártela (botón "Compartir") con el `client_email` del paso 5, dándole permiso de **Editor**.

> ⚠️ `credenciales.json` da acceso completo a esa hoja de cálculo. No lo subas a repositorios públicos ni lo compartas.

## Parte 2 — Preparar el entorno en la PC

### 1. Crear el entorno virtual

```bash
cd "proyecto esp32"
python -m venv .venv
```

Activarlo:

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependencias

Contenido de `requirements.txt`:

```
flask
gspread
oauth2client
esptool
mpremote
```

Instalar:

```bash
pip install -r requirements.txt
```

### 3. Verificar tu IP local

El ESP32 necesita saber la IP de tu PC en la red local:

```bash
# Windows
ipconfig
# Linux/Mac
ifconfig
```

Anota la dirección IPv4 (ej. `192.168.40.14`).

## Parte 3 — Flashear el ESP32

### 1. Identificar el puerto serial

- Windows: Administrador de dispositivos → Puertos (COM y LPT) → ej. `COM3`
- Linux: normalmente `/dev/ttyUSB0`
- Mac: `/dev/tty.usbserial-XXXX`

### 2. Borrar la flash (recomendado antes de flashear)

```bash
esptool --port COM3 erase_flash
```

### 3. Flashear el firmware de MicroPython

```bash
esptool --port COM3 --baud 460800 write-flash -z 0x1000 micropython.bin
```

Espera a que la barra de progreso llegue al 100%.

## Parte 4 — Configurar y subir el código del ESP32

### 1. Editar `esp32_codigo/main.py`

Ajusta estos valores con los tuyos:

```python
ssid = "TU_WIFI"
password = "TU_PASSWORD"
...
url = "http://TU_IP_LOCAL:5000/datos"   # la IP que anotaste en la Parte 2, paso 3
```

### 2. Subir los archivos al ESP32

```bash
mpremote connect COM3 fs cp esp32_codigo/boot.py :boot.py
mpremote connect COM3 fs cp esp32_codigo/main.py :main.py
mpremote connect COM3 reset
```

### 3. Ver los logs en vivo (opcional, para depurar)

```bash
mpremote connect COM3
```

Deberías ver:

```
Conectando al WiFi...
Conectado: 192.168.x.x
Enviado: {'temp': 24.5, 'hum': 60}
```

Salir de la consola con `Ctrl+]`.

## Parte 5 — Correr el servidor Flask

Con el `.venv` activado:

```bash
python server.py
```

Deberías ver algo como:

```
Running on http://0.0.0.0:5000
Running on http://192.168.40.14:5000
```

Prueba en el navegador: `http://TU_IP_LOCAL:5000/` → debe responder **"Servidor ESP32 activo 🚀"**.

---

## Solución de problemas

### Error `ECONNABORTED` en el ESP32

El ESP32 se conecta al WiFi pero no logra llegar al servidor Flask. Causas comunes:

1. **El servidor no está corriendo** → ejecuta `python server.py`.
2. **IP incorrecta** en `main.py` → verifica con `ipconfig`/`ifconfig`.
3. **Red WiFi marcada como "Pública"** en Windows → cámbiala a **Privada** (Configuración de red → Propiedades del WiFi).
4. **Antivirus/firewall de terceros** (Norton, McAfee, etc.) bloqueando conexiones entrantes → dentro de esa app, marca la red como privada/confiable y permite `python.exe` / el puerto 5000.
5. **Firewall nativo de Windows** → Panel de control → Firewall de Windows Defender → permitir `python.exe` en redes privadas, o crear una regla de entrada para el puerto TCP 5000.

### El ESP32 no conecta al WiFi

- Verifica que la red sea de **2.4GHz** (el ESP32 no soporta 5GHz).
- Revisa que el SSID y password en `main.py` sean exactos (sensible a mayúsculas).

### No llegan filas al Google Sheet

- Confirma que el Sheet se llame exactamente `esp32_datos`.
- Confirma que esté compartido con el `client_email` de `credenciales.json` con permiso de Editor.
- Revisa la consola de `server.py`: si el `POST /datos` responde `200`, el problema es de permisos en Sheets, no de conexión.

## Notas de seguridad

- No subas `credenciales.json` ni el WiFi/password de `main.py` a repositorios públicos.
- Este servidor Flask usa el servidor de desarrollo integrado (no apto para producción). Para uso real, usar un servidor WSGI (gunicorn, waitress, etc.).

## Checklist rápido para replicar el proyecto

- [ ] Google Cloud: APIs habilitadas + cuenta de servicio + `credenciales.json`
- [ ] Sheet `esp32_datos` creado y compartido con la cuenta de servicio
- [ ] `.venv` creado y `requirements.txt` instalado
- [ ] IP local de la PC anotada
- [ ] ESP32 flasheado con `micropython.bin`
- [ ] `main.py` editado con WiFi e IP correctos, y subido al ESP32
- [ ] Red WiFi marcada como privada (Windows + antivirus si aplica)
- [ ] `python server.py` corriendo sin errores
- [ ] ESP32 imprime "Enviado: {...}" cada 60s
- [ ] Filas nuevas aparecen en el Google Sheet
