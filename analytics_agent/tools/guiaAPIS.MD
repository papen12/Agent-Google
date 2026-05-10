Guía completa: Configurar Google Sheets API en Google Cloud

PARTE 1 — Google Cloud Console
Paso 1 — Crear un proyecto

Ve a https://console.cloud.google.com e inicia sesión con tu cuenta Google.
En la barra superior, haz clic en el selector de proyecto (junto al logo de Google Cloud).
Clic en "Nuevo proyecto".
Ponle un nombre, por ejemplo: incaicos-v-agent.
Clic en Crear y espera unos segundos a que se genere.


Paso 2 — Activar Google Sheets API y Google Drive API

En el menú lateral izquierdo ve a APIs y servicios → Biblioteca.
Busca Google Sheets API → selecciona el resultado → clic en Habilitar.
Regresa a Biblioteca, busca Google Drive API → clic en Habilitar.


Ambas son obligatorias. Sheets API permite leer/escribir celdas. Drive API permite crear archivos y compartirlos.


Paso 3 — Crear una Service Account

Ve a APIs y servicios → Credenciales.
Clic en "+ Crear credenciales" → Service account.
En "Nombre de la cuenta de servicio" escribe: incaicos-sheets-bot.
Clic en Crear y continuar.
En el campo "Rol" selecciona Básico → Editor.
Clic en Continuar → Listo.


La Service Account es la identidad con la que tu agente se autentica ante Google. Funciona como un usuario robot independiente de tu cuenta personal.


Paso 4 — Descargar las credenciales JSON

En la lista de Service Accounts, haz clic en el email de la cuenta que acabas de crear.
Ve a la pestaña "Claves".
Clic en "Agregar clave" → "Crear clave nueva".
Selecciona formato JSON → clic en Crear.
El archivo se descarga automáticamente. Renómbralo a credentials.json.
Colócalo en la carpeta raíz de tu proyecto.


⚠️ NUNCA subas este archivo a GitHub. Contiene una clave privada que da acceso total a tu proyecto. Agrégalo a .gitignore de inmediato.

# .gitignore
credentials.json
*.json

Paso 5 — Copiar el email de la Service Account

Abre el archivo credentials.json con cualquier editor de texto.
Busca el campo "client_email". Tendrá un formato así:

incaicos-sheets-bot@incaicos-v-agent.iam.gserviceaccount.com

Copia ese email y guárdalo. Lo necesitarás para compartir los sheets con los analistas.


PARTE 2 — Configuración del proyecto Python
Paso 6 — Instalar dependencias
bashpip install gspread google-auth google-auth-oauthlib

Paso 7 — Script de prueba para verificar la conexión
Antes de tocar el agente, verifica que las credenciales funcionan correctamente:
pythonimport gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

# Crear un sheet de prueba
spreadsheet = client.create("TEST - Verificación de conexión")
spreadsheet.share("", perm_type="anyone", role="reader")

print("✅ Conexión exitosa")
print("URL del sheet:", spreadsheet.url)

# Limpiar: eliminar el sheet de prueba
client.del_spreadsheet(spreadsheet.id)
print("🗑️ Sheet de prueba eliminado")
Ejecuta con:
bashpython test_connection.py
Si ves ✅ Conexión exitosa y una URL, todo está funcionando.

Paso 8 — Usar variable de entorno para la ruta de credenciales
En vez de hardcodear la ruta del archivo, usa una variable de entorno. Esto es más seguro y flexible entre entornos (local, producción, etc.):
pythonimport os

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
Crea un archivo .env en la raíz del proyecto:
GOOGLE_CREDENTIALS_PATH=credentials.json

PARTE 3 — Errores comunes y sus soluciones
Error: FileNotFoundError: credentials.json
→ El archivo no está en el directorio desde donde ejecutas el script. Verifica la ruta o usa la variable de entorno del Paso 8.
Error: APIError: 403 Google Sheets API has not been enabled
→ Olvidaste habilitar alguna de las dos APIs en el Paso 2. Ve a la Biblioteca y verifica que ambas estén activas.
Error: SpreadsheetNotFound o el analista no puede abrir el link
→ La Service Account crea el archivo en su propio Drive, no en el tuyo. Debes compartirlo explícitamente con el email del analista:
pythonspreadsheet.share("analista@empresa.com", perm_type="user", role="writer")
Error: quota exceeded
→ Google Sheets permite 300 escrituras por minuto por proyecto. Si escribes muchas celdas, agrupa los datos en una sola llamada a worksheet.update() en vez de escribir celda por celda.

Estructura final del proyecto
incaicos_v/
├── agent.py
├── generate_sheets_report.py
├── test_connection.py
├── credentials.json        ← NO subir a Git
├── .env
└── .gitignore              ← incluir credentials.json aquí

Resumen de los 3 puntos críticos

Activar ambas APIs (Sheets + Drive). Sin Drive la Service Account no puede crear archivos.
Nunca commitear credentials.json. Si se expone, cualquiera puede usar tu cuota y tus datos.
Compartir el sheet explícitamente. La Service Account es un usuario independiente; crea los archivos en su propio Drive, no en el tuyo.