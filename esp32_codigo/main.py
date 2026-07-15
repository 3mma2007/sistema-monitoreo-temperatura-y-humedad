import network
import time
import dht #permite controlar sensores dht (DHT22 en mi caso)  DHT = digital humidity and temperature (humedad y temperatura digital)
from machine import Pin
import urequests


#WiFi  
ssid = "FLIA ESCOBAR"  #nombre de la red   SSID = service set identifier (nombre publico de la red wifi)
password = "Josue2311" #contraseña de la red


#https://www.profetolocka.com.ar/2020/12/15/micropython-conectar-con-una-red-wifi/
wifi = network.WLAN(network.STA_IF)  #network.STA_IF para conectarse a una red WiFi existente  WLAN = wireless local area network
wifi.active(True) #activar la interfaz wifi 
wifi.connect(ssid, password) #conectarse a la red WiFi con el nombre y contraseña especificados


while not wifi.isconnected():  #Mientras no esté conectado a la red WiFi
    print("Conectando al WiFi...")
    time.sleep(1)

print("Conectado:")  #cuando se conecta imprime la dirección IP asignada al ESP32 por el router
print("Dirección IP:", wifi.ifconfig()[0])
print("Máscara de subred:", wifi.ifconfig()[1])
print("Puerta de enlace:", wifi.ifconfig()[2])
print("Servidor DNS:", wifi.ifconfig()[3])
#ifconfig() devuelve una tupla con la dirección IP, máscara de subred, puerta de enlace y servidor DNS. [0] para obtener solo la dirección IP


#Sensor
pin_sensor = Pin(25) #crear un objeto pin_sensor de tipo Pin conectado al pin 25 del ESP32
#PIN 25 = Es un GPIO (General Purpose Input/Output) del ESP32 
sensor = dht.DHT22(pin_sensor) #crear un objeto sensor de tipo DHT22 conectado al pin especificado
#sensor = dht.DHT22(Pin(25)) 


#Servidor Flask
url = "http://192.168.40.14:5000/datos"

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        data = {"temp": temp, "hum": hum}
        r = urequests.post(url, json=data)
        r.close()

        print("Enviado:", data)

    except Exception as e:
        print("Error:", e)

    time.sleep(60)
