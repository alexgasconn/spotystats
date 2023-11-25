# app/routes.py
from flask import render_template
from app import app
from spoty_stats import calcular_tiempo_reproduccion, mostrar_resultados
import os

@app.route('/')
def index():
    # Ruta de los archivos
    directorio = r'C:\Users\usuario\OneDrive\Escritorio\VS files\spoty'

    # Obtener la lista de archivos en la ruta especificada
    archivos = [os.path.join(directorio, f'StreamingHistory{i}.json') for i in range(3)]

    # Calcular el tiempo total de reproducción y el número de reproducciones por canción
    tiempo_por_cancion = calcular_tiempo_reproduccion(archivos)

    # Mostrar los resultados y guardar en CSV
    mostrar_resultados(tiempo_por_cancion)

    # Lee el CSV recién creado y devuelve sus contenidos como texto para mostrar en la interfaz web
    with open('C:\\Users\\usuario\\OneDrive\\Escritorio\\VS files\\spoty\\stats.csv', 'r', encoding='latin1') as csv_file:
        csv_contents = csv_file.read()

    return render_template('index.html', csv_contents=csv_contents)
