import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random


user = "alex" #alex/mireia/carol
tipo_data = "songs" #artists/albums/songs
number_of_items = 10
speed = 5  #del 1 al 10
option = "total_reproductions"    #ms_played/total_reproductions



def create_dataframe():
    directory_path = os.path.dirname(__file__) + f"\{user}"
    dfs = []
    all_files = os.listdir(directory_path)
    relevant_files = [file for file in all_files if file.startswith('Streaming_History_Audio')]
    for file_name in relevant_files:
        file_path = os.path.join(directory_path, file_name)
        df = pd.read_json(file_path)
        df['ts'] = pd.to_datetime(df['ts'])
        dfs.append(df)
    df = pd.concat(dfs)
    return df


def get_top_data(user, tipo, number, artist=None, album=None):
    grouped_data_artist = df.groupby([df['ts'].dt.date, 'master_metadata_album_artist_name', 'spotify_track_uri']).sum(numeric_only=True)['ms_played'].reset_index()
    grouped_data_album = df.groupby([df['ts'].dt.date, 'master_metadata_album_album_name', 'spotify_track_uri']).sum(numeric_only=True)['ms_played'].reset_index()
    grouped_data_song = df.groupby([df['ts'].dt.date, 'master_metadata_track_name', 'spotify_track_uri']).sum(numeric_only=True)['ms_played'].reset_index()

    grouped_data_artist['ms_played'] = grouped_data_artist['ms_played'] / 60000
    grouped_data_album['ms_played'] = grouped_data_album['ms_played'] / 60000
    grouped_data_song['ms_played'] = grouped_data_song['ms_played'] / 60000

    top_artists_by_day = grouped_data_artist.groupby('ts').apply(lambda x: x.nlargest(number, 'ms_played')).reset_index(drop=True)
    top_albums_by_day = grouped_data_album.groupby('ts').apply(lambda x: x.nlargest(number, 'ms_played')).reset_index(drop=True)
    top_songs_by_day = grouped_data_song.groupby('ts').apply(lambda x: x.nlargest(number, 'ms_played')).reset_index(drop=True)

    top_artists_by_day = top_artists_by_day[top_artists_by_day['ms_played'] > 10]  # Filtrar reproducciones mayores a 20 segundos
    top_albums_by_day = top_albums_by_day[top_albums_by_day['ms_played'] > 10]
    top_songs_by_day = top_songs_by_day[top_songs_by_day['ms_played'] > 10]

    top_artists_by_day['cumulative_ms'] = top_artists_by_day.groupby('master_metadata_album_artist_name')['ms_played'].cumsum()
    top_albums_by_day['cumulative_ms'] = top_albums_by_day.groupby('master_metadata_album_album_name')['ms_played'].cumsum()
    top_songs_by_day['cumulative_ms'] = top_songs_by_day.groupby('master_metadata_track_name')['ms_played'].cumsum()

    top_artists_by_day['total_reproductions'] = top_artists_by_day.groupby('master_metadata_album_artist_name').transform('size')
    top_albums_by_day['total_reproductions'] = top_albums_by_day.groupby('master_metadata_album_album_name').transform('size')
    top_songs_by_day['total_reproductions'] = top_songs_by_day.groupby('master_metadata_track_name').transform('size')

    if tipo == "artists":
        return top_artists_by_day
    elif tipo == "albums":
        return top_albums_by_day
    elif tipo == "songs":
        return top_songs_by_day

def get_unique_items():
    unique_artists = df['master_metadata_album_artist_name'].unique()
    unique_albums = df['master_metadata_album_album_name'].unique()
    unique_songs = df['master_metadata_track_name'].unique()
    unique_items = {
        'artists': unique_artists,
        'albums': unique_albums,
        'songs': unique_songs}
    return unique_items


def set_delay(speed):
    if speed == 10:
        sleep_time = 0
    else:
        sleep_time = 10 ** (-speed / 2)
    time.sleep(sleep_time)

def suppress_qt_warnings():
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"
suppress_qt_warnings()

current_date_index = 0
update_interval = 50
pause_index = 0
def animate():
    global current_date_index, play_state, colors_dict, pause_index
    if play_state and current_date_index < len(unique_dates):
        selected_date = pd.to_datetime(unique_dates[current_date_index]).date()
        date_var.set(str(selected_date))
        update_plot(selected_date, colors_dict)
        current_date_index += 1
        root.after(update_interval, animate)
    else:
        play_button.configure(text="Start")
        current_date_index = pause_index

def toggle_animation():
    global play_state, pause_index
    play_state = not play_state
    if play_state:
        play_button.configure(text="Pause")
        animate()
    else:
        play_button.configure(text="Start")
        pause_index = current_date_index


def date_changed(*args):
    global colors_dict, current_date_index
    selected_date = pd.to_datetime(date_var.get()).date()
    try:
        current_date_index = list(unique_dates).index(selected_date)
    except ValueError:
        print(f"Warning: Selected date {selected_date} is not in the data.")
    update_plot(selected_date, colors_dict)


def update_plot(selected_date, colors):
    data_until_date = top_data_by_day[top_data_by_day['ts'] <= selected_date]

    if tipo_data == "artists":
        cumulative_data_artists = data_until_date.groupby('master_metadata_album_artist_name')[option].sum().reset_index()
    elif tipo_data == "albums":
        cumulative_data_albums = data_until_date.groupby('master_metadata_album_album_name')[option].sum().reset_index()
    elif tipo_data == "songs":
        cumulative_data_songs = data_until_date.groupby('master_metadata_track_name')[option].sum().reset_index()

    if tipo_data == "artists":
        top_data_artists = cumulative_data_artists.nlargest(number_of_items, option).sort_values(by=option, ascending=True)
    elif tipo_data == "albums":
        top_data_albums = cumulative_data_albums.nlargest(number_of_items, option).sort_values(by=option, ascending=True)
    elif tipo_data == "songs":
        top_data_songs = cumulative_data_songs.nlargest(number_of_items, option).sort_values(by=option, ascending=True)

    ax.clear()

    if tipo_data == "artists":
        bars = ax.barh(top_data_artists['master_metadata_album_artist_name'], top_data_artists[option], color=[colors[artist] for artist in top_data_artists['master_metadata_album_artist_name']])
    elif tipo_data == "albums":
        bars = ax.barh(top_data_albums['master_metadata_album_album_name'], top_data_albums[option], color=[colors[album] for album in top_data_albums['master_metadata_album_album_name']])
    elif tipo_data == "songs":
        bars = ax.barh(top_data_songs['master_metadata_track_name'], top_data_songs[option], color=[colors[song] for song in top_data_songs['master_metadata_track_name']])

    for bar in bars:
        xval = bar.get_width()
        pos = bar.get_y() + bar.get_height() / 2
        if xval > 150:
            if xval > 1500:
                ax.text(xval + 10, pos, f'{int(xval)} ({xval/60:.1f}h) [{xval/1440:.1f}days]', va='center')
            else:
                ax.text(xval + 10, pos, f'{int(xval)} ({xval/60:.1f}h)', va='center')
        else:
            ax.text(xval + 10, pos, f'{int(xval)}', va='center')

    ax.set_title(f'{user.capitalize()} - Top {number_of_items} {tipo_data} - {selected_date}')
    ax.set_xlabel('Accumulated Minutes' if option == 'ms_played' else 'Total Reproductions')
    ax.set_ylabel(f'{tipo_data}')
    canvas.draw()
    set_delay(speed)

def assign_colors(top_data):
    if tipo_data == "artists":
        unique_entities = top_data['master_metadata_album_artist_name'].unique()
    elif tipo_data == "albums":
        unique_entities = top_data['master_metadata_album_album_name'].unique()
    elif tipo_data == "songs":
        unique_entities = top_data['master_metadata_track_name'].unique()
    colors = {entity: f'#{random.randint(0, 0xFFFFFF):06x}' for entity in unique_entities}
    return colors


def stream_song(spotify_uri):
    sp_oauth = SpotifyOAuth(client_id='772f387bafac4393a8cafbf09ee5aa86',
                            client_secret='07d0d3b97c68425a832b6dcc6d5838ec',
                            redirect_uri='http://localhost:PORT',
                            scope='user-modify-playback-state')
    auth_url = sp_oauth.get_authorize_url()
    print(f'Por favor, visita este enlace para autorizar la aplicación: {auth_url}')
    auth_code = input('Introduce el código de autorización: ')
    token_info = sp_oauth.get_access_token(auth_code)

    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.start_playback(uris=[spotify_uri])
    else:
        print('Error al obtener el token de acceso')


def update_speed(value):
    global speed
    speed = int(value)

def update_options(*args):
    global user, tipo_data, option
    user = user_var.get()
    tipo_data = tipo_data_var.get()
    option = option_var.get()
    update_plot(pd.to_datetime(unique_dates[current_date_index]).date(), colors_dict)

def update_number_of_items(value):
    global number_of_items
    number_of_items = int(value)




df = create_dataframe()
top_data_by_day = get_top_data(user, tipo_data, number_of_items)
print(top_data_by_day)

colors_dict = assign_colors(top_data_by_day)

root = tk.Tk()
root.title(f"{user.capitalize()} - Top {number_of_items} {tipo_data} - Accumulated Minutes per Day")

fig, ax = plt.subplots(figsize=(18, 8))

unique_dates = top_data_by_day['ts'].unique()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

play_state = tk.BooleanVar(value=False)

date_var = tk.StringVar(value=str(unique_dates[0]))
date_dropdown = tk.OptionMenu(root, date_var, *unique_dates)
date_dropdown.pack(side="left", padx=10)

date_var.trace_add("write", date_changed)


# Dropdown para la variable "user"
user_var = tk.StringVar(value=user)
user_options = ["alex", "mireia", "carol"]
user_dropdown = tk.OptionMenu(root, user_var, *user_options, command=update_options)
user_dropdown.pack(side="left", padx=10)

# Dropdown para la variable "tipo_data"
tipo_data_var = tk.StringVar(value=tipo_data)
tipo_data_options = ["artists", "albums", "songs"]
tipo_data_dropdown = tk.OptionMenu(root, tipo_data_var, *tipo_data_options, command=update_options)
tipo_data_dropdown.pack(side="left", padx=10)

# Dropdown para la variable "option"
option_var = tk.StringVar(value=option)
option_options = ["ms_played", "total_reproductions"]
option_dropdown = tk.OptionMenu(root, option_var, *option_options, command=update_options)
option_dropdown.pack(side="left", padx=10)

# Barra desplazable para la variable "number_of_items"
number_of_items_var = tk.StringVar(value=str(number_of_items))
number_of_items_scale = tk.Scale(root, from_=1, to=50, orient="horizontal", variable=number_of_items_var, command=update_number_of_items, label="Number of Songs")
number_of_items_scale.pack(side="left", padx=10)

speed_var = tk.StringVar(value=str(speed))
speed_scale = tk.Scale(root, from_=1, to=10, orient="horizontal", variable=speed_var, command=update_speed, label="Speed")
speed_scale.pack(side="left", padx=10)

play_button = ttk.Button(root, text="Start", command=toggle_animation)
play_button.pack(side="left", padx=10)



update_plot(pd.to_datetime(unique_dates[0]).date(), colors_dict)

# Ejecutar la interfaz gráfica
tk.mainloop()