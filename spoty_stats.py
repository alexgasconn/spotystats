import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


user = "alex" #alex/mireia
tipo_data = "songs" #artists/albums/songs
number_of_items = 10
speed = 5  #del 1 al 10
option = "minutes"    #minutes/total_reproductions


def create_dataframe(user):
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
    # df = df[df['ms_played' > 20000]]

    return df

def rename_columns(df):
    df.rename(columns={'master_metadata_album_artist_name': 'artist',
                    'master_metadata_album_album_name': 'album',
                    'master_metadata_track_name': 'song'}, inplace=True)
    
    df.drop(['ip_addr', 'spotify_track_uri', 'episode_name', 
            'episode_show_name', 'spotify_episode_uri', 
            'offline_timestamp', 'incognito_mode'], axis=1, inplace=True, errors='ignore')
    return df

def get_unique_items(df):
    data = df.dropna(subset=['artist'])
    data = df.dropna(subset=['album'])
    data = df.dropna(subset=['song'])
    unique_artists = sorted(data['artist'].unique())
    unique_albums = sorted(data['album'].unique())
    unique_songs = sorted(data['song'].unique())
    unique_items = {
        'artists': unique_artists,
        'albums': unique_albums,
        'songs': unique_songs}
    return unique_items


def filter_artist(df, artist):
    data = df[df['artist'] == artist]
    return data

def filter_album(df, album):
    data = df[df['album'] == album]
    return data

def filter_song(df, song):
    data = df[df['song'] == song]
    return data

def delete_artist(df, artist):
    data = df[df['artist'] != artist]
    return data

def total_minutes(df):
    total_minutes_per_artist = df.groupby('artist')['ms_played'].sum() / 60000
    total_minutes_per_album = df.groupby('album')['ms_played'].sum() / 60000
    total_minutes_per_song = df.groupby('master_metadata_trsongack_name')['ms_played'].sum() / 60000

    total_minutes_per_artist = total_minutes_per_artist.reset_index()
    total_minutes_per_album = total_minutes_per_album.reset_index()
    total_minutes_per_song = total_minutes_per_song.reset_index()

    return total_minutes_per_artist, total_minutes_per_album, total_minutes_per_song

def get_top_streamed_data(df, top_n):
    # Group by date and category, summing playback time
    grouped_by_artist = df.groupby([df['ts'].dt.date, 'artist'])['ms_played'].sum().reset_index()
    grouped_by_album = df.groupby([df['ts'].dt.date, 'album'])['ms_played'].sum().reset_index()
    grouped_by_song = df.groupby([df['ts'].dt.date, 'song'])['ms_played'].sum().reset_index()

    # Convert playback time from milliseconds to minutes
    grouped_by_artist['minutes'] = grouped_by_artist['ms_played'] / 60000
    grouped_by_album['minutes'] = grouped_by_album['ms_played'] / 60000
    grouped_by_song['minutes'] = grouped_by_song['ms_played'] / 60000

    # Retrieve the top N entities by minutes played for each day
    top_artists_daily = grouped_by_artist.groupby('ts').apply(lambda x: x.nlargest(top_n, 'minutes')).reset_index(drop=True)
    top_albums_daily = grouped_by_album.groupby('ts').apply(lambda x: x.nlargest(top_n, 'minutes')).reset_index(drop=True)
    top_songs_daily = grouped_by_song.groupby('ts').apply(lambda x: x.nlargest(top_n, 'minutes')).reset_index(drop=True)

    # Calculate cumulative minutes for each entity
    top_artists_daily['cumulative_minutes'] = top_artists_daily.groupby('artist')['minutes'].cumsum()
    top_albums_daily['cumulative_minutes'] = top_albums_daily.groupby('album')['minutes'].cumsum()
    top_songs_daily['cumulative_minutes'] = top_songs_daily.groupby('song')['minutes'].cumsum()

    # Calculate total reproductions for each entity
    top_artists_daily['total_reproductions'] = top_artists_daily.groupby('artist')['minutes'].transform('size')
    top_albums_daily['total_reproductions'] = top_albums_daily.groupby('album')['minutes'].transform('size')
    top_songs_daily['total_reproductions'] = top_songs_daily.groupby('song')['minutes'].transform('size')

    return top_artists_daily, top_albums_daily, top_songs_daily


import matplotlib.pyplot as plt

def plot_top(df, num, category):
    # Group by the specified category and calculate total minutes played
    grouped_data = df.groupby(category)['ms_played'].sum().reset_index()
    grouped_data['minutes_played'] = grouped_data['ms_played'] / 60000

    # Get the top 20 entities by total minutes played
    top = grouped_data.nlargest(num, 'minutes_played')

    # Plot the data
    plt.figure(figsize=(12, 8))
    plt.barh(top[category], top['minutes_played'], color='skyblue')
    plt.title(f"Top 20 {category.capitalize()}s of All Time by Total Minutes Played")
    plt.xlabel("Total Minutes Played")
    plt.ylabel(category.capitalize())
    plt.gca().invert_yaxis()  # Invert y-axis for descending order
    plt.tight_layout()
    plt.show()


def filter_by_date_range(df, start_date, end_date):
    df['ts'] = pd.to_datetime(df['ts'])

    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')

    filtered_df = df[(df['ts'] >= start_date) & (df['ts'] <= end_date)]
    return filtered_df



def monthly_visualizations(df):
    monthly_data = df.groupby(df['ts'].dt.to_period('M'))['ms_played'].sum()
    monthly_data_minutes = monthly_data / (1000 * 60)

    x_labels = [period.start_time.strftime('%Y-%m-%d') for period in monthly_data.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_data_minutes.plot(kind='bar',edgecolor='black', ax=ax)
    ax.set_title('Monthly Time', fontsize=16)
    ax.set_xlabel('Month', fontsize=14)
    ax.set_ylabel('Minutes Played', fontsize=14)
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    
    plt.tight_layout()
    plt.show()


def weekly_visualizations(df):
    weekly_data = df.groupby(df['ts'].dt.to_period('W'))['ms_played'].sum()
    weekly_data_minutes = weekly_data / (1000 * 60)

    x_labels = [period.start_time.strftime('%Y-%m-%d') for period in weekly_data.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    weekly_data_minutes.plot(kind='bar',edgecolor='black', ax=ax)
    ax.set_title('Weekly Time', fontsize=16)
    ax.set_xlabel('Week', fontsize=14)
    ax.set_ylabel('Minutes Played', fontsize=14)
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    
    plt.tight_layout()
    plt.show()


def daily_visualizations(df):
    daily_data = df.groupby(df['ts'].dt.to_period('D'))['ms_played'].sum()
    daily_data_minutes = daily_data / (1000 * 60)

    x_labels = [period.start_time.strftime('%Y-%m-%d') for period in daily_data.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    daily_data_minutes.plot(kind='bar',edgecolor='black', ax=ax)
    ax.set_title('Daily Time', fontsize=16)
    ax.set_xlabel('Day', fontsize=14)
    ax.set_ylabel('Minutes Played', fontsize=14)
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    
    plt.tight_layout()
    plt.show()




########################## START ##############################
df = create_dataframe(user)
spotify_df = rename_columns(df)
unique_data = get_unique_items(spotify_df)

taylor_df = filter_artist(spotify_df, "Taylor Swift")
olivia_df = filter_artist(spotify_df, "Olivia Rodrigo")
myke_df = filter_artist(spotify_df, "Myke Towers")
coldplay_df = filter_artist(spotify_df, "Coldplay")
oasis_df = filter_artist(spotify_df, "Oasis")
bizarrap_df = filter_artist(spotify_df, "Bizarrap")
londra_df = filter_artist(spotify_df, "Paulo Londra")
badbunny_df = filter_artist(spotify_df, "Bad Bunny")
queen_df = filter_artist(spotify_df, "Queen")

folklore_df = filter_album(spotify_df, "folklore")
evermore_df = filter_album(spotify_df, "evermore")

df = filter_song(spotify_df, "Sister of Pearl")

top_artists, top_albums, top_songs = get_top_streamed_data(spotify_df, 10)

df_2025 = filter_by_date_range(spotify_df, "2025-01-01", "2025-12-01")


no_taylor = delete_artist(spotify_df, "Taylor Swift") 

# plot_top(no_taylor, 20, "song")
# plot_top(no_taylor, 20, "album")
plot_top(df_2025, 50, "album")

monthly_visualizations(df_2025)
# weekly_visualizations(no_taylor)
# daily_visualizations(no_taylor)
