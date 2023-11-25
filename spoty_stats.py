import os
import json
import pandas as pd
from datetime import datetime, timedelta


def leer_archivo(archivo):
    try:
        with open(archivo, 'r', encoding='latin1') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {archivo}")
        return []

def calcular_tiempo_reproduccion(archivos):
    tiempo_por_cancion = {}

    for archivo in archivos:
        data = leer_archivo(archivo)

        for registro in data:
            artist_name = registro['artistName']
            track_name = registro['trackName']
            track_name = track_name.replace(",", ";")
            ms_played = registro['msPlayed']
            end_time = datetime.strptime(registro['endTime'], "%Y-%m-%d %H:%M")

            key = f"{artist_name} - {track_name}"

            if key in tiempo_por_cancion:
                tiempo_por_cancion[key]['ms_played'] += ms_played
                tiempo_por_cancion[key]['reproducciones'] += 1
                tiempo_por_cancion[key]['last_played'] = end_time
            else:
                tiempo_por_cancion[key] = {
                    'artist': artist_name,
                    'title': track_name,
                    'ms_played': ms_played,
                    'reproducciones': 1,
                    'first_played': end_time,
                    'last_played': end_time
                }

    return tiempo_por_cancion

def mostrar_resultados(tiempo_por_cancion):
    # Ordenar los resultados por la duración total de reproducción de mayor a menor
    resultados_ordenados = sorted(tiempo_por_cancion.items(), key=lambda x: x[1]['ms_played'], reverse=True)

    # Crear un DataFrame con los resultados
    df = pd.DataFrame(resultados_ordenados, columns=['Cancion', 'Datos'])

    # Crear un nuevo DataFrame para las columnas 'Artista' y 'Título'
    df_artist_title = pd.DataFrame(df['Datos'].tolist(), index=df.index)

    # Concatenar los DataFrames
    df = pd.concat([df, df_artist_title], axis=1)

    # Calcular minutos, duración y formato de la fecha
    df['Minutos'] = df['Datos'].apply(lambda x: x['ms_played'] / (1000 * 60))
    df['Duracion'] = df['Datos'].apply(lambda x: str(timedelta(milliseconds=x['ms_played'])).split(".")[0])
    df['Milisegundos'] = df['Datos'].apply(lambda x: x['ms_played'])
    df['Reproducciones'] = df['Datos'].apply(lambda x: x['reproducciones'])
    df['Primera reproduccion'] = df['Datos'].apply(lambda x: x['first_played'].strftime("%Y-%m-%d %H:%M"))
    df['Última reproduccion'] = df['Datos'].apply(lambda x: x['last_played'].strftime("%Y-%m-%d %H:%M"))

    # Eliminar filas con menos de 20 segundos 
    df = df[df['Milisegundos'] > 20000]

    # Eliminar columnas no deseadas
    # df = df[['artist', 'title', 'Minutos', 'Duración', 'Milisegundos', 'Reproducciones', 'Primera reproducción', 'Última reproducción']]
    df = df[['artist', 'title', 'Duracion', 'Milisegundos', 'Reproducciones', 'Primera reproduccion', 'Última reproduccion']]

    # Mostrar el DataFrame
    print(df)

    # Guardar el DataFrame como un archivo CSV
    df.to_csv(os.path.join('C:\\Users\\usuario\\OneDrive\\Escritorio\\VS files\\spoty', 'stats.csv'), index=False, sep=';', encoding='latin1')


if __name__ == "__main__":
    # Ruta de los archivos
    directorio = r'C:\Users\usuario\OneDrive\Escritorio\VS files\spoty'

    # Obtener la lista de archivos en la ruta especificada
    archivos = [os.path.join(directorio, f'StreamingHistory{i}.json') for i in range(3)]

    # Calcular el tiempo total de reproducción y el número de reproducciones por canción
    tiempo_por_cancion = calcular_tiempo_reproduccion(archivos)

    # Mostrar los resultados y guardar en CSV
    mostrar_resultados(tiempo_por_cancion)
