import yt_dlp
import os

# Listes pour garder trace des téléchargements réussis et des erreurs
success_downloads = []
failed_downloads = []

# Fonction de téléchargement avec gestion des erreurs
def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mkv',
        'outtmpl': '%(title)s.%(ext)s',  # Utilisation du titre pour le nom de fichier
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mkv',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            print(f"[INFO] Téléchargement réussi : {video_title}")
            success_downloads.append(video_title)
        except yt_dlp.utils.DownloadError as e:
            print(f"[ERREUR] Erreur lors du téléchargement de '{url}' : {str(e)}")
            failed_downloads.append(url)

# Lire les URL depuis le fichier list.txt
with open("list.txt", "r") as f:
    urls = f.readlines()

# Traiter chaque URL
for url in urls:
    url = url.strip()  # Nettoyer les espaces ou les sauts de ligne
    print(f"[INFO] Téléchargement de l'URL : {url}")
    download_video(url)

# Résumé final
print("\n### Résumé des téléchargements ###")
print(f"Nombre total de vidéos dans list.txt : {len(urls)}")
print(f"Vidéos téléchargées avec succès : {len(success_downloads)}")
print(f"Vidéos ayant échoué : {len(failed_downloads)}")

if success_downloads:
    print("\nVidéos téléchargées avec succès :")
    for title in success_downloads:
        print(f"- {title}")

if failed_downloads:
    print("\nVidéos ayant échoué :")
    for url in failed_downloads:
        print(f"- {url}")
