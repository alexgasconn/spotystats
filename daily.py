import os
import json
from datetime import datetime, timedelta

def leer_archivo(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {archivo}")
        return []

def procesar_datos(files):
    artistas_diarios = {}

    for file_path in files:
        data = leer_archivo(file_path)

        for entry in data:
            endTime = entry["endTime"]
            artistName = entry["artistName"]
            msPlayed = entry["msPlayed"]

            fecha = datetime.strptime(endTime, "%Y-%m-%d %H:%M")
            fecha_diaria = fecha.date()

            if fecha_diaria not in artistas_diarios:
                artistas_diarios[fecha_diaria] = {}

            if artistName not in artistas_diarios[fecha_diaria]:
                artistas_diarios[fecha_diaria][artistName] = 0

            artistas_diarios[fecha_diaria][artistName] += msPlayed

    # Acumular los milisegundos para cada artista en cada día
    for fecha, artistas in artistas_diarios.items():
        for artista, ms_total in artistas.items():
            if fecha - timedelta(days=1) in artistas_diarios:
                ms_total_acumulado = artistas_diarios[fecha - timedelta(days=1)].get(artista, 0)
                artistas_diarios[fecha][artista] += ms_total_acumulado

    return artistas_diarios

PATH = r'C:\Users\usuario\OneDrive\Escritorio\VS files\spoty'
files = [os.path.join(PATH, f'StreamingHistory{i}.json') for i in range(3)]

resultados = procesar_datos(files)

# Puedes imprimir o manipular los resultados como desees
for fecha, artistas in resultados.items():
    print(f"Fecha: {fecha}")
    for artista, ms_total in artistas.items():
        print(f"  {artista}: {ms_total} ms")
