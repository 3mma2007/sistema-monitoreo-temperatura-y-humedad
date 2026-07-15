import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

scope = [  #alcance o permisos que necesita la aplicación (acceso a Google Sheets y Google Drive)
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credenciales.json", scope
)
client = gspread.authorize(creds)
sheet = client.open("esp32_datos").sheet1

@app.route("/datos", methods=["POST"])
def recibir():
    d = request.get_json()

    if not d or "temp" not in d or "hum" not in d:
        return "Datos inválidos", 400
    
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        d["temp"],
        d["hum"]
    ])
    return "OK", 200



@app.route("/")
def home():
    return "Servidor ESP32 activo 🚀"


app.run(host="0.0.0.0", port=5000)

