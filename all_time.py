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
import re


user = "alex" #alex/mireia
tipo_data = "songs" #artists/albums/songs
number_of_items = 10
speed = 2  #del 1 al 10
option = "minutes"    #minutes/total_reproductions
taylor_only = False
mix_tv = False



def create_dataframe(user):
    directory_path = os.path.dirname(__file__) + f"\{user}"
    dfs = []
    all_files = os.listdir(directory_path)
    relevant_files = [file for file in all_files if file.startswith('Streaming_History_Audio')]
    for file_name in relevant_files:
        file_path = os.path.join(directory_path, file_name)
        df = pd.read_json(file_path)
        if mix_tv:
            df['master_metadata_track_name'] = df['master_metadata_track_name'].apply(lambda x: re.sub(r'\([^)]*\)', '', x).rstrip() if x and 'Version' in x else x)
        
        df['master_metadata_track_name'] = df['master_metadata_track_name'].str.replace("Taylor's Version", 'TV')
        df['master_metadata_track_name'] = df['master_metadata_track_name'].str.replace("From The Vault", 'FTV')
        df['ts'] = pd.to_datetime(df['ts'])
        dfs.append(df)
    df = pd.concat(dfs)
    return df


def get_top_data(df, user, tipo, number, artist=None, album=None):
    start_date = pd.to_datetime("2024-01-01").tz_localize('UTC')
    end_date = pd.to_datetime("2025-12-01").tz_localize('UTC')

    df = df[(df['ts'] >= start_date) & (df['ts'] <= end_date)]


    artist = artist_var.get() if artist_var.get() else None
    album = album_var.get() if album_var.get() else None
    if taylor_only.get():
        pass
        # df = df[df['master_metadata_album_artist_name'] == 'Taylor Swift']
        # df = df[df['master_metadata_album_artist_name'] == 'Myke Towers']
        # df = df[df['master_metadata_album_artist_name'] == 'Bad Bunny']
        # df = df[df['master_metadata_album_album_name'] == "1989 (Taylor's Version)"]


    if artist:
        df = df[df['master_metadata_album_artist_name'] == artist]
    if album:
        df = df[df['master_metadata_album_album_name'] == album]

    grouped_data_artist = df.groupby([df['ts'].dt.date, 'master_metadata_album_artist_name', 'spotify_track_uri']).sum(numeric_only=True)['ms_played'].reset_index()
    grouped_data_album = df.groupby([df['ts'].dt.date, 'master_metadata_album_album_name', 'spotify_track_uri']).sum(numeric_only=True)['ms_played'].reset_index()
    grouped_data_song = df.groupby([df['ts'].dt.date, 'master_metadata_track_name', 'spotify_track_uri']).sum(numeric_only=True)['ms_played'].reset_index()

    grouped_data_artist['minutes'] = grouped_data_artist['ms_played'] / 60000
    grouped_data_album['minutes'] = grouped_data_album['ms_played'] / 60000
    grouped_data_song['minutes'] = grouped_data_song['ms_played'] / 60000

    top_artists_by_day = grouped_data_artist.groupby('ts').apply(lambda x: x.nlargest(number, 'minutes')).reset_index(drop=True)
    top_albums_by_day = grouped_data_album.groupby('ts').apply(lambda x: x.nlargest(number, 'minutes')).reset_index(drop=True)
    top_songs_by_day = grouped_data_song.groupby('ts').apply(lambda x: x.nlargest(number, 'minutes')).reset_index(drop=True)

    top_artists_by_day = top_artists_by_day[top_artists_by_day['minutes'] > 0.5]
    top_albums_by_day = top_albums_by_day[top_albums_by_day['minutes'] > 0.5]
    top_songs_by_day = top_songs_by_day[top_songs_by_day['minutes'] > 0.5]

    top_artists_by_day['cumulative_minutes'] = top_artists_by_day.groupby('master_metadata_album_artist_name')['minutes'].cumsum()
    top_albums_by_day['cumulative_minutes'] = top_albums_by_day.groupby('master_metadata_album_album_name')['minutes'].cumsum()
    top_songs_by_day['cumulative_minutes'] = top_songs_by_day.groupby('master_metadata_track_name')['minutes'].cumsum()

    top_artists_by_day['total_reproductions'] = top_artists_by_day.groupby('master_metadata_album_artist_name').transform('size')
    top_albums_by_day['total_reproductions'] = top_albums_by_day.groupby('master_metadata_album_album_name').transform('size')
    top_songs_by_day['total_reproductions'] = top_songs_by_day.groupby('master_metadata_track_name').transform('size')

    return top_artists_by_day, top_albums_by_day, top_songs_by_day

def get_unique_items():
    df1 = df.dropna(subset=['master_metadata_album_artist_name'])
    df1 = df.dropna(subset=['master_metadata_album_album_name'])
    df1 = df.dropna(subset=['master_metadata_track_name'])
    unique_artists = sorted(df1['master_metadata_album_artist_name'].unique())
    unique_albums = sorted(df1['master_metadata_album_album_name'].unique())
    unique_songs = sorted(df1['master_metadata_track_name'].unique())
    unique_items = {
        'artists': unique_artists,
        'albums': unique_albums,
        'songs': unique_songs}
    return unique_items

def total_minutes(df):
    # Agrupar por canción y sumar los minutos reproducidos
    total_minutes_per_artist = df.groupby('master_metadata_album_artist_name')['ms_played'].sum() / 60000
    total_minutes_per_album = df.groupby('master_metadata_album_album_name')['ms_played'].sum() / 60000
    total_minutes_per_song = df.groupby('master_metadata_track_name')['ms_played'].sum() / 60000

    # Resetear el índice para obtener una nueva columna 'master_metadata_track_name'
    total_minutes_per_artist = total_minutes_per_artist.reset_index()
    total_minutes_per_album = total_minutes_per_album.reset_index()
    total_minutes_per_song = total_minutes_per_song.reset_index()

    return total_minutes_per_artist, total_minutes_per_album, total_minutes_per_song



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
        update_plot(selected_date, colors_dict, user, tipo_data, option, previous_days_var.get())
        current_date_index += 1
        app.after(update_interval, animate)
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
    update_plot(selected_date, colors_dict, user, tipo_data, option, previous_days_var.get())


def update_plot(selected_date, colors, user, tipo_data, option, show_previous_days):
    if tipo_data == "artists":
        artists_until_date = top_artists_by_day[top_artists_by_day['ts'] <= selected_date]
        if show_previous_days:
            start_date = selected_date - pd.DateOffset(days=30)
            artists_until_date = artists_until_date[artists_until_date['ts'] >= start_date]
        cumulative_data_artists = artists_until_date.groupby('master_metadata_album_artist_name')[option].sum().reset_index()
        top_data_artists = cumulative_data_artists.nlargest(number_of_items, option).sort_values(by=option, ascending=True)

    elif tipo_data == "albums":
        album_until_date = top_albums_by_day[top_albums_by_day['ts'] <= selected_date]
        if show_previous_days:
            start_date = selected_date - pd.DateOffset(days=30)
            album_until_date = album_until_date[album_until_date['ts'] >= start_date]
        cumulative_data_albums = album_until_date.groupby('master_metadata_album_album_name')[option].sum().reset_index()
        top_data_albums = cumulative_data_albums.nlargest(number_of_items, option).sort_values(by=option, ascending=True)

    elif tipo_data == "songs":
        songs_until_date = top_songs_by_day[top_songs_by_day['ts'] <= selected_date]
        if show_previous_days:
            start_date = selected_date - pd.DateOffset(days=30)
            songs_until_date = songs_until_date[songs_until_date['ts'] >= start_date]
        cumulative_data_songs = songs_until_date.groupby('master_metadata_track_name')[option].sum().reset_index()
        top_data_songs = cumulative_data_songs.nlargest(number_of_items, option).sort_values(by=option, ascending=True)

    ax.clear()
        

    if tipo_data == "artists":
        bars = ax.barh(top_data_artists['master_metadata_album_artist_name'][-number_of_items:], top_data_artists[option][-number_of_items:], color=[colors[artist] for artist in top_data_artists['master_metadata_album_artist_name'][-number_of_items:]])

    elif tipo_data == "albums":
        bars = ax.barh(top_data_albums['master_metadata_album_album_name'], top_data_albums[option], color=[colors[album] for album in top_data_albums['master_metadata_album_album_name']])

    elif tipo_data == "songs":
        top_data_songs['master_metadata_track_name'] = top_data_songs['master_metadata_track_name'].str.replace("Taylor's Version", 'TV')
        bars = ax.barh(top_data_songs['master_metadata_track_name'], top_data_songs[option], color=[colors[song] for song in top_data_songs['master_metadata_track_name']])
        plt.yticks(rotation=45)

    for bar in bars:
        minutes = bar.get_width()
        pos = bar.get_y() + bar.get_height() / 2
        hours = f"{minutes/60:.1f}"
        days = f"{minutes/1440:.1f}"

        if option == "minutes": 
            if minutes > 120:
                if minutes > 1500:
                    info = f'{int(minutes)} ({hours}h) [{days}d]'
                else:
                    info = f'{int(minutes)} ({hours}h)'
            else:
                info = f'{int(minutes)}'
        else:
            info = minutes
        ax.text(minutes + 10, pos, info, va='center')

    ax.set_title(f'{user.capitalize()} - Top {number_of_items} {tipo_data} - {selected_date}')
    ax.set_xlabel('Accumulated Minutes' if option == 'minutes' else 'Total Reproductions')
    ax.set_ylabel(f'{tipo_data}')
    canvas.draw()
    set_delay(speed)


def assign_colors(top_artists_by_day, top_albums_by_day, top_songs_by_day):
    unique_artists = top_artists_by_day['master_metadata_album_artist_name'].unique()
    unique_albums = top_albums_by_day['master_metadata_album_album_name'].unique()
    unique_songs = top_songs_by_day['master_metadata_track_name'].unique()
    colors_artists = {entity: f'#{random.randint(0, 0xFFFFFF):06x}' for entity in unique_artists}
    colors_albums = {entity: f'#{random.randint(0, 0xFFFFFF):06x}' for entity in unique_albums}
    colors_songs = {entity: f'#{random.randint(0, 0xFFFFFF):06x}' for entity in unique_songs}
    colors_dict = colors_artists | colors_albums | colors_songs
    return colors_dict


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
    update_plot(pd.to_datetime(unique_dates[current_date_index]).date(), colors_dict, user, tipo_data, option, previous_days_var.get())

def update_number_of_items(value):
    global number_of_items
    number_of_items = int(value)

def update_taylor_only():
    global taylor_only
    taylor_only = taylor_only




############### START ###############


#Creates the App
app = tk.Tk()
app.title(f"{user.capitalize()} - Top {number_of_items} {tipo_data} - Accumulated Minutes per Day")

fig, ax = plt.subplots(figsize=(17, 7))

canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

play_state = tk.BooleanVar(value=False)



#Dropdown para la variable "user"
user_var = tk.StringVar(value=user)
user_options = ["alex", "mireia", "carol"]
user_dropdown = tk.OptionMenu(app, user_var, *user_options, command=update_options)
user_dropdown.pack(side="left", padx=10)

#Dropdown para la variable "tipo_data"
tipo_data_var = tk.StringVar(value=tipo_data)
tipo_data_options = ["artists", "albums", "songs"]
tipo_data_dropdown = tk.OptionMenu(app, tipo_data_var, *tipo_data_options, command=update_options)
tipo_data_dropdown.pack(side="left", padx=10)

#Dropdown para la variable "option"
option_var = tk.StringVar(value=option)
option_options = ["minutes", "total_reproductions"]
option_dropdown = tk.OptionMenu(app, option_var, *option_options, command=update_options)
option_dropdown.pack(side="left", padx=10)

#Barra desplazable para la variable "number_of_items"
number_of_items_var = tk.StringVar(value=str(10))
number_of_items_scale = tk.Scale(app, from_=1, to=50, orient="horizontal", variable=number_of_items_var, command=update_number_of_items, label=f"Number of {tipo_data}")
number_of_items_scale.pack(side="left", padx=10)

#Barra desplazable para la variable "speed"
speed_var = tk.StringVar(value=str(5))
speed_scale = tk.Scale(app, from_=1, to=10, orient="horizontal", variable=speed_var, command=update_speed, label="Speed")
speed_scale.pack(side="left", padx=10)

play_button = ttk.Button(app, text="Start", command=toggle_animation)
play_button.pack(side="left", padx=10)

#Add a Checkbutton for the Taylor Only option
taylor_only = tk.BooleanVar(value=True)
taylor_only_checkbox = ttk.Checkbutton(app, text="Only Taylor", variable=taylor_only, command=update_taylor_only)
taylor_only_checkbox.pack(side="left", padx=10)

# Después de la creación de taylor_only_checkbox, puedes agregar lo siguiente:
previous_days_var = tk.BooleanVar(value=True)
previous_days_checkbox = ttk.Checkbutton(app, text="Show Previous 30 Days", variable=previous_days_var)
previous_days_checkbox.pack(side="left", padx=10)







#Gets dataframe data
df = create_dataframe(user)
all_data = get_unique_items()
all_artists = all_data["artists"]
all_albums = all_data["albums"]
total = total_minutes(df)

artist_var = tk.StringVar(value=None)
artist_dropdown = tk.OptionMenu(app, artist_var, *all_artists)
artist_dropdown.pack(side="right", padx=10)

album_var = tk.StringVar(value=None)
album_dropdown = tk.OptionMenu(app, album_var, *all_albums)
album_dropdown.pack(side="right", padx=10)

top_artists_by_day, top_albums_by_day, top_songs_by_day = get_top_data(df, user, tipo_data, number_of_items, artist_var, album_var)

colors_dict = assign_colors(top_artists_by_day, top_albums_by_day, top_songs_by_day)

unique_dates = top_songs_by_day['ts'].unique()

#Gets dates from the resulted dataframes
date_var = tk.StringVar(value=str(unique_dates[0]))
date_dropdown = tk.OptionMenu(app, date_var, *unique_dates)
date_dropdown.pack(side="right", padx=10)
date_var.trace_add("write", date_changed)


def monthly_visualizations(df):
    # Filtrar las reproducciones de Taylor Swift
    taylor_df = df[df['master_metadata_album_artist_name'] == 'Taylor Swift']
    
    # Agrupar por mes y sumar los minutos reproducidos
    monthly_data = taylor_df.groupby(taylor_df['ts'].dt.to_period('M'))['ms_played'].sum() # Convertir a minutos
    
    # Imprimir las visualizaciones mensuales
    for month, minutes in monthly_data.items():
        print(f"{month.to_timestamp().strftime('%B %Y')}: {minutes}")

# Llamar a la función con el dataframe
monthly_visualizations(df)

#Ejecutar la interfaz gráfica
tk.mainloop()



#WARNING DE ERROR AL COMPARAR TIME STAMPS
#SELECCIONAR QUIN ARTIRSTA CONCRET VOLS BUSCAR
#SAME AMB ALBUM
#MOURE INDICADOR PER NAVEGAR EN DATES COM A INDRA
#TOTS ELS DATOS MENYS UN ARTISTA
#GIRAR NOMS DE CANCÇONS ALBUMS I ARTISTES (ARA NOMES HI HA 1)