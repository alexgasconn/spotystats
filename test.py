import os
import pandas as pd
import matplotlib.pyplot as plt

def create_dataframe(user):
    directory_path = os.path.join(os.path.dirname(__file__), user)
    dfs = []
    all_files = os.listdir(directory_path)
    relevant_files = [file for file in all_files if file.startswith('Streaming_History_Audio')]
    for file_name in relevant_files:
        file_path = os.path.join(directory_path, file_name)
        df = pd.read_json(file_path)
        # Aplicar transformaciones si es necesario
        df['master_metadata_track_name'] = df['master_metadata_track_name'].str.replace("Taylor's Version", 'TV')
        df['master_metadata_track_name'] = df['master_metadata_track_name'].str.replace("From The Vault", 'FTV')
        df['ts'] = pd.to_datetime(df['ts'])
        dfs.append(df)
    df = pd.concat(dfs)
    return df

# Crear DataFrame a partir del archivo CSV
user = "alex"
df = create_dataframe(user)

# Verificar si se ha creado el DataFrame correctamente
if df is not None:
    print("DataFrame creado exitosamente.")
else:
    print("No se pudo crear el DataFrame. Por favor, verifica la ruta del archivo CSV.")

# Filtrar las reproducciones del álbum "1989" y "1989 (Taylor's Version)"
album_1989 = df[((df['master_metadata_album_album_name'] == '1989') | 
                (df['master_metadata_album_album_name'] == "1989 (Taylor's Version)") |
                (df['master_metadata_album_album_name'] == "1989 (TV)")) & 
                (df['master_metadata_album_artist_name'] == "Taylor Swift")]

# Obtener el número de reproducciones de cada canción en el álbum "1989"
reproducciones_1989 = album_1989['master_metadata_track_name'].value_counts()

# Crear un gráfico de barras para mostrar el número de reproducciones de cada canción
plt.figure(figsize=(10, 6))
reproducciones_1989.plot(kind='bar', color='skyblue')
plt.title('Reproducciones por Canción - Álbum "1989"')
plt.xlabel('Canción')
plt.ylabel('Número de Reproducciones')
plt.xticks(rotation=45, ha='right', fontsize=8)  # Rotar las etiquetas del eje x y ajustar el tamaño de fuente
plt.tight_layout()
plt.show()
