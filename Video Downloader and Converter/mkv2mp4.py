import os
import subprocess

# Dossier contenant les fichiers téléchargés
download_folder = "C:/Program_CG33/Nmap/video_dl"

# Fonction pour convertir un fichier MKV en MP4
def convert_to_mp4(mkv_file):
    mp4_file = mkv_file.replace(".mkv", ".mp4")
    
    # Commande FFmpeg pour convertir le fichier MKV en MP4
    ffmpeg_command = ["ffmpeg", "-i", mkv_file, "-codec", "copy", mp4_file]
    
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"[INFO] Conversion réussie : {mkv_file} -> {mp4_file}")
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Erreur lors de la conversion de {mkv_file} : {str(e)}")

# Parcourir les fichiers dans le dossier
for filename in os.listdir(download_folder):
    if filename.endswith(".mkv"):
        mkv_file = os.path.join(download_folder, filename)
        print(f"[INFO] Conversion du fichier : {mkv_file}")
        convert_to_mp4(mkv_file)

print("\nConversion terminée.")
