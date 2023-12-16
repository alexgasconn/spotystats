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
    tiempo_por_artista_mensual = {}

    for archivo in archivos:
        data = leer_archivo(archivo)

        for registro in data:
            artist_name = registro['artistName']
            track_name = registro['trackName']
            track_name = track_name.replace(",", ";")
            ms_played = registro['msPlayed']
            end_time = datetime.strptime(registro['endTime'], "%Y-%m-%d %H:%M")

            key_cancion = f"{artist_name} - {track_name}"
            key_artista = artist_name

            if key_cancion in tiempo_por_cancion:
                tiempo_por_cancion[key_cancion]['ms_played'] += ms_played
                tiempo_por_cancion[key_cancion]['reproducciones'] += 1
                tiempo_por_cancion[key_cancion]['last_played'] = end_time
            else:
                tiempo_por_cancion[key_cancion] = {
                    'artist': artist_name,
                    'title': track_name,
                    'ms_played': ms_played,
                    'reproducciones': 1,
                    'first_played': end_time,
                    'last_played': end_time
                }

            # Agrupar por artista y mes
            key_artista_mensual = f"{artist_name}_{end_time.strftime('%Y-%m')}"
            if key_artista_mensual in tiempo_por_artista_mensual:
                tiempo_por_artista_mensual[key_artista_mensual]['ms_played'] += ms_played
                tiempo_por_artista_mensual[key_artista_mensual]['reproducciones'] += 1
                tiempo_por_artista_mensual[key_artista_mensual]['last_played'] = end_time
            else:
                tiempo_por_artista_mensual[key_artista_mensual] = {
                    'artist': artist_name,
                    'ms_played': ms_played,
                    'reproducciones': 1,
                    'first_played': end_time,
                    'last_played': end_time
                }

    return tiempo_por_cancion, tiempo_por_artista_mensual

def mostrar_resultados(tiempo_por_cancion, tiempo_por_artista_mensual):
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
    df = df[['artist', 'title', 'Duracion', 'Milisegundos', 'Reproducciones', 'Primera reproduccion', 'Última reproduccion']]

    # Mostrar el DataFrame
    print(df)

    # Guardar el DataFrame como un archivo CSV
    df.to_csv(os.path.join('C:\\Users\\usuario\\OneDrive\\Escritorio\\VS files\\spoty', 'stats_canciones.csv'), index=False, sep=';', encoding='latin1')

    # Crear un DataFrame para los datos mensuales de artistas
    df_artista_mensual = pd.DataFrame(tiempo_por_artista_mensual.items(), columns=['Artista_Mes', 'Datos'])
    df_artista_mensual[['artist', 'mes']] = df_artista_mensual['Artista_Mes'].str.split('_', expand=True)

    # Crear un nuevo DataFrame para las columnas 'Artista' y 'Mes'
    df_artista_mensual_data = pd.DataFrame(df_artista_mensual['Datos'].tolist(), index=df_artista_mensual.index)

    # Concatenar los DataFrames
    df_artista_mensual = pd.concat([df_artista_mensual, df_artista_mensual_data], axis=1)

    # Calcular minutos, duración y formato de la fecha
    df_artista_mensual['Minutos'] = df_artista_mensual['Datos'].apply(lambda x: x['ms_played'] / (1000 * 60))
    df_artista_mensual['Duracion'] = df_artista_mensual['Datos'].apply(lambda x: str(timedelta(milliseconds=x['ms_played'])).split(".")[0])
    df_artista_mensual['Milisegundos'] = df_artista_mensual['Datos'].apply(lambda x: x['ms_played'])
    df_artista_mensual['Reproducciones'] = df_artista_mensual['Datos'].apply(lambda x: x['reproducciones'])
    df_artista_mensual['Primera reproduccion'] = df_artista_mensual['Datos'].apply(lambda x: x['first_played'].strftime("%Y-%m-%d %H:%M"))
    df_artista_mensual['Última reproduccion'] = df_artista_mensual['Datos'].apply(lambda x: x['last_played'].strftime("%Y-%m-%d %H:%M"))

    # Eliminar columnas no deseadas
    df_artista_mensual = df_artista_mensual[['artist', 'mes', 'Duracion', 'Milisegundos', 'Reproducciones']]

    # Mostrar el DataFrame
    print(df_artista_mensual)

    # Guardar el DataFrame como un archivo CSV
    df_artista_mensual.to_csv(os.path.join('C:\\Users\\usuario\\OneDrive\\Escritorio\\VS files\\spoty', 'stats_artistas_mensuales.csv'), index=False, sep=';', encoding='latin1')


if __name__ == "__main__":
    # Ruta de los archivos
    directorio = r'C:\Users\usuario\OneDrive\Escritorio\VS files\spoty'

    # Obtener la lista de archivos en la ruta especificada
    archivos = [os.path.join(directorio, f'StreamingHistory{i}.json') for i in range(3)]

    # Calcular el tiempo total de reproducción y el número de reproducciones por canción y artista mensual
    tiempo_por_cancion, tiempo_por_artista_mensual = calcular_tiempo_reproduccion(archivos)

    # Mostrar los resultados y guardar en CSV
    mostrar_resultados(tiempo_por_cancion, tiempo_por_artista_mensual)
