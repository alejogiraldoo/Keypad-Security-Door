# LIBRERIA PARA REALIZAR LA CONEXION CON ARDUINO
import serial # COMANDO PARA INSTALAR LA LIBRERIA : py -3.10 -m pip install pyserial
import time
# LIBRERIA PARA CREAR LA HOJA DE EXCEL
import xlsxwriter # pip install xlsxwriter
# LIBRERIA PARA CAPTURAR LA FECHA
from datetime import datetime
# LIBRERIA PARA CONVERTIR LA LATITUD Y LONGITUD A DIRECCION
from geopy.geocoders import Nominatim
# LIBRERIAS PARA DISEÑAR EL MAPA
import folium # COMANDO PARA INSTALAR LA LIBRERIA : py -3.10 -m pip install folium
from folium import plugins
import webbrowser


# ___________________CONEXION CON ARDUINO___________________
# PARAMETROS DEL PUERTO Y VELOCIDAD DE LOS DATOS
serialArduino = serial.Serial("COM3",115200)
# ESPERA UN SEGUNDO DESPUES DE CREAR EL OBJETO
time.sleep(1)
# ___________________HOJA EXCEL___________________
archivo = xlsxwriter.Workbook('localizacion.xlsx')
hoja = archivo.add_worksheet('hoja1')
hoja.write(0,0,"FECHA")
hoja.write(0,1,"LOCALIZACIÓN")
cantRegistros = 1
regisGuardados = 0
row = 1

# DISEÑO DEL MAPA
origin = "Medellín"
# CAPTURA DE COORDENADAS (LAT,LNG) DEL ORIGEN
geolocalizador = Nominatim(user_agent="Prueba")
locOrig = geolocalizador.geocode(origin)

# LAT Y LONG | ORIGEN
latOrig = locOrig.latitude
longtOrig = locOrig.longitude

# CREACION DEL MAPA
mapa = folium.Map(location=[latOrig,longtOrig], zoom_start=8)

while True:
    # BUSCAMOS ERRORES EN CASO DE DAR ERRORES DE EJECUCIÓN
    try:
        # OBTENEMOS LA INFORMACIÓN DEL PUERTO
        val = serialArduino.readline()
        # DECODIFICAMOS LA INFORMACIÓN DEL PUERTO
        cad = val.decode("ascii")
        pos = cad.index(",")
        # LAT Y LONG | ENTRADA
        lat = cad[:pos]
        longt = cad[pos+1:]
        # REALIZAMOS UNA VERIFICACIÓN PARA VALIDAR QUE LAS COORDENADAS FUERON ENVIADAS COMPLETAS
        if len(lat) >= 8 and len(longt) >= 8:
            # CONTAMOS LA CANTIDAD DE REGISTROS GUARDADOS
            regisGuardados += 1
            # CAPTURAMOS LA FECHA ACTUAL
            fecha = datetime.now()
            # CONVERTIMOS LAS COORDENADAS EN DIRECCIÓN
            geolocator = Nominatim(user_agent="ubicEntrada")
            location = geolocator.reverse(f"{lat},{longt}")
            datos = [str(fecha),location.address]
            # INSERTAMOS LOS DATOS EN LA HOJA DE EXCEL
            column = 0
            for dato in datos:
                hoja.write(row,column,dato)
                column += 1
            row += 1
            # IMPRIMIMOS LO QUE GUARDAMOS
            print(f"{lat} {longt}") #print(location.address)
            # UBICACION DEL BARRENDERO EN EL MAPA
            folium.Marker(location=[lat,longt], popup= "Entrada", icon=folium.Icon(color="blue", icon_color="white", icon='user')).add_to(mapa)
            
            # COMPARAMOS SI LOS REGISTROS GUARDADOS SON IGUAL A LOS REQUERIDOS
            if cantRegistros == regisGuardados:
                # GUARDAMOS LA CANTIDAD DE REGISTROS
                archivo.close()
                break
    except:
        print("ERROR AL ENVIAR LOS DATOS DESDE EL PUERTO...")
        pass

# CAPAS DEL MAPA
folium.TileLayer('Stamen Terrain').add_to(mapa)
folium.TileLayer('Cartodb Positron').add_to(mapa)
folium.TileLayer('CartoDB dark_matter').add_to(mapa)
folium.TileLayer('stamentoner').add_to(mapa)

folium.LayerControl(position="topleft").add_to(mapa)

mapa.save('Mapa de Ubicación.html')
webbrowser.open('Mapa de Ubicación.html')