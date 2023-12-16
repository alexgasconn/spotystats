import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import time

# Ruta del directorio que contiene los archivos JSON
directory_path = r'C:\Users\usuario\OneDrive\Escritorio\VS files\spoty\mireia'

# Lista de nombres de archivos
# file_names = [
#     'Streaming_History_Audio_2018-2021_0',
#     'Streaming_History_Audio_2021-2022_1',
#     'Streaming_History_Audio_2022-2023_3',
#     'Streaming_History_Audio_2023_4',
#     'Streaming_History_Audio_2023_5'
# ]

file_names = [
    'Streaming_History_Audio_2011-2014_0',
    'Streaming_History_Audio_2014-2015_1',
    'Streaming_History_Audio_2015-2018_2',
    'Streaming_History_Audio_2018-2019_3',
    'Streaming_History_Audio_2019-2020_4',
    'Streaming_History_Audio_2020-2021_5',
    'Streaming_History_Audio_2021-2022_6',
    'Streaming_History_Audio_2022-2023_7',
    'Streaming_History_Audio_2023_8',
]

# Leer y procesar cada archivo
dfs = []
for file_name in file_names:
    file_path = os.path.join(directory_path, f'{file_name}.json')
    df = pd.read_json(file_path)
    df['ts'] = pd.to_datetime(df['ts'])
    dfs.append(df)

# Concatenar los DataFrames
df = pd.concat(dfs)

# Agrupa los datos por día y artista y calcula la cantidad total de tiempo escuchado
grouped_data = df.groupby([df['ts'].dt.date, 'master_metadata_album_artist_name']).sum(numeric_only=True)['ms_played'].reset_index()

# Convertir milisegundos a minutos
grouped_data['ms_played'] = grouped_data['ms_played'] / 60000

# Obtiene el top 10 acumulado de artistas por día
top_artists_by_day = grouped_data.groupby('ts').apply(lambda x: x.nlargest(10, 'ms_played')).reset_index(drop=True)

# Acumular los milisegundos por día y artista
top_artists_by_day['cumulative_ms'] = top_artists_by_day.groupby('master_metadata_album_artist_name')['ms_played'].cumsum()

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Top 10 Artists - Accumulated Minutes per Day")

# Crear figura de Matplotlib
fig, ax = plt.subplots(figsize=(8, 6))

# Función para actualizar el gráfico
def update_plot(selected_date):
    # Filtra los datos hasta la fecha seleccionada
    data_until_date = top_artists_by_day[top_artists_by_day['ts'] <= selected_date]

    # Agrupa por artista y calcula la suma acumulada de milisegundos
    cumulative_data = data_until_date.groupby('master_metadata_album_artist_name')['ms_played'].sum().reset_index()

    # Obtiene el Top 10 de artistas con más milisegundos acumulados
    top_artists = cumulative_data.nlargest(10, 'ms_played')

    # Configura el gráfico con colores diferentes para cada artista
    ax.clear()
    colors = plt.cm.tab10
    top_artists = top_artists.sort_values(by='ms_played', ascending=True)
    bars = ax.barh(top_artists['master_metadata_album_artist_name'], top_artists['ms_played'], color=colors(range(len(top_artists))))

    # Etiqueta con el valor en cada barra
    for bar in bars:
        xval = bar.get_width()
        ax.text(xval + 10, bar.get_y() + bar.get_height()/2, f'{xval:.2f}', va='center')

    ax.set_title(f'Top 10 Artists - Accumulated Minutes until {selected_date}')
    ax.set_xlabel('Accumulated Minutes')
    ax.set_ylabel('Artist')
    fig.tight_layout()
    canvas.draw()

# Lista de fechas únicas
unique_dates = top_artists_by_day['ts'].unique()

# Barra de desplazamiento para seleccionar la fecha
date_var = tk.StringVar(value=str(unique_dates[0]))
date_dropdown = tk.OptionMenu(root, date_var, *unique_dates)
date_dropdown.pack()

# Lienzo para la figura de Matplotlib
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Botón de reproducción
play_button = ttk.Button(root, text="Play", command=lambda: play_animation())
play_button.pack()

# Variable para controlar el estado de reproducción
play_state = tk.BooleanVar(value=False)

# Función para manejar el cambio de fecha
def date_changed(*args):
    selected_date = pd.to_datetime(date_var.get()).date()
    update_plot(selected_date)

date_var.trace_add("write", date_changed)

# Función para la animación de reproducción
def play_animation():
    global play_state
    play_state = not play_state  # Invertir el estado de reproducción
    if play_state:
        play_button.configure(text="Pause")
        for date in unique_dates:
            if play_state:
                date_var.set(str(date))
                root.update()
                time.sleep(0.05)  # Pausa de 0.05 segundos entre fechas (5 veces más rápido)
            else:
                play_button.configure(text="Play")
                break

# Ejecutar la interfaz gráfica
tk.mainloop()
