import os
import re
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt

PATH = r'C:\Users\usuario\OneDrive\Escritorio\VS files\spoty'
MIN_MS = 20000
SEPARA_TV = False
TODAY = datetime.now().strftime("%d%m%Y")

def leer_archivo(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {archivo}")
        return []

def get_time_per_song(archivos):
    tiempo_por_cancion = {}

    for archivo in archivos:
        data = leer_archivo(archivo)

        streamings_list = []
        list_total_hours = []
        list_total_days = []


        for registro in data:
            artist_name = registro['artistName']
            track_name = registro['trackName'].replace(",", ";")
            # track_name = track_name.replace(",", ";")
            ms_played = registro['msPlayed']
            end_time = datetime.strptime(registro['endTime'], "%Y-%m-%d %H:%M")
            day, hour = registro['endTime'].split(" ")
            list_total_hours.append(hour)
            list_total_days.append(day)


            key = f"{artist_name} - {track_name}"
            
            if SEPARA_TV == False:
                if "Version" in key:
                    key = re.sub(r'\([^)]*\)', '', key).rstrip()
                    track_name = re.sub(r'\([^)]*\)', '', track_name).rstrip()

            if key in tiempo_por_cancion:
                tiempo_por_cancion[key]['ms_played'] += ms_played
                tiempo_por_cancion[key]['reproducciones'] += 1
                tiempo_por_cancion[key]['last_played'] = end_time
                if ms_played < MIN_MS:
                    tiempo_por_cancion[key]['skips'] += 1
            else:
                tiempo_por_cancion[key] = {
                    'artist': artist_name,
                    'title': track_name,
                    'ms_played': ms_played,
                    'reproducciones': 1,
                    'first_played': end_time,
                    'last_played': end_time,
                    'skips': 0 if ms_played >= MIN_MS else 1
    }

    return tiempo_por_cancion, list_total_days, list_total_hours

def mostrar_resultados(tiempo_por_cancion):
    # Ordenar los resultados por la duración total de reproducción de mayor a menor
    resultados_ordenados = sorted(tiempo_por_cancion.items(), key=lambda x: x[1]['ms_played'], reverse=True)

    # Crear un DataFrame con los resultados
    df = pd.DataFrame(resultados_ordenados, columns=['Cancion', 'Datos'])
    df_artist_title = pd.DataFrame(df['Datos'].tolist(), index=df.index)
    df = pd.concat([df, df_artist_title], axis=1)


    df['Minutos'] = df['Datos'].apply(lambda x: x['ms_played'] / (1000 * 60))
    df['Duracion'] = df['Datos'].apply(lambda x: str(timedelta(milliseconds=x['ms_played'])).split(".")[0])
    df['Milisegundos'] = df['Datos'].apply(lambda x: x['ms_played'])
    df['Reproducciones'] = df['Datos'].apply(lambda x: x['reproducciones'])
    df['First stream'] = df['Datos'].apply(lambda x: x['first_played'].strftime("%Y-%m-%d %H:%M"))
    df['Last stream'] = df['Datos'].apply(lambda x: x['last_played'].strftime("%Y-%m-%d %H:%M"))
    df['Skips'] = df['Datos'].apply(lambda x: x['skips'])
    df['Skip %'] = (df['Datos'].apply(lambda x: x['skips']) / df['Datos'].apply(lambda x: x['reproducciones']))


    df = df[['artist', 'title', 'Duracion', 'Milisegundos', 'Reproducciones', 'First stream', 'Last stream', 'Skips', 'Skip %']]

    df.to_csv(os.path.join(PATH, f'stats_songs_{TODAY}.csv'), index=False, sep=';', encoding='utf-8')


def get_days_count(days_list):
    days_count = Counter(days_list)
    return days_count

def plot_hour(hour_list):
    datetime_list = [datetime.strptime(hour, "%H:%M") for hour in hour_list]
    hours = [dt.hour for dt in datetime_list]
    plt.hist(hours, bins=24, edgecolor='black', alpha=0.7)
    plt.xlabel('Hora del día')
    plt.ylabel('Frecuencia')
    plt.title('Histograma de Horas')
    plt.xticks(range(24))
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    files = [os.path.join(PATH, f'StreamingHistory{i}.json') for i in range(3)]

    tiempo_por_cancion, dias, horas = get_time_per_song(files)

    mostrar_resultados(tiempo_por_cancion)
