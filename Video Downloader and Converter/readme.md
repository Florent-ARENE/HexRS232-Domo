# Video Downloader and Converter

## Description

Ce projet permet de télécharger des vidéos à partir de plusieurs plateformes comme YouTube et Vimeo, en utilisant `yt-dlp`. Il convertit également les fichiers téléchargés en MP4 à partir des formats d'origine, tels que MKV ou WebM.

### Fonctionnalités principales :
- **Téléchargement de vidéos** : Télécharge des vidéos depuis des plateformes comme YouTube et Vimeo.
- **Conversion en MP4** : Conversion automatique des vidéos téléchargées en format MP4 tout en conservant la piste audio principale.
- **Support de différents formats** : Supporte les formats MKV, WebM, etc.

## Prérequis

Assurez-vous d'avoir installé les outils suivants :

- [Python](https://www.python.org/) (Version 3.7 ou supérieure)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/) (Version 7.1 ou plus récente)

### Installation de `yt-dlp`
```bash
pip install yt-dlp
```

### Installation de `ffmpeg`

1. Téléchargez la version complète de `ffmpeg` depuis [FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/).
2. Décompressez-le dans un dossier, par exemple : `C:\Program_CG33\ffmpeg-7.1-full_build`.
3. Ajoutez le chemin vers le dossier `bin` de `ffmpeg` à votre variable d'environnement `PATH`.

### Vérifiez l'installation de `ffmpeg`
```bash
ffmpeg -version
```

## Utilisation

### 1. Téléchargement des vidéos

Le script `dl.py` permet de télécharger des vidéos à partir d'une liste d'URLs définie dans le fichier `list.txt`.

#### Lancer le script de téléchargement :
```bash
python dl.py
```

Ce script :
- Télécharge les vidéos à partir des URLs.
- Affiche un retour d'information pour chaque vidéo téléchargée ou échec.
- Conserve les titres des vidéos comme nom de fichier lors du téléchargement.

### 2. Conversion des vidéos en MP4

Le script `convert_to_mp4.py` convertit les fichiers téléchargés (par exemple, en `.mkv`) au format `.mp4` tout en conservant la piste audio principale.

#### Lancer le script de conversion :
```bash
python convert_to_mp4.py
```

## Structure du projet

```
video_dl/
│
├── dl.py                 # Script principal pour télécharger les vidéos
├── convert_to_mp4.py      # Script pour convertir les vidéos en MP4
├── list.txt               # Liste des URLs des vidéos à télécharger
└── README.md              # Documentation du projet
```

## Notes

- **yt-dlp** permet d'extraire les vidéos à partir de nombreuses plateformes. Les paramètres du téléchargement peuvent être ajustés dans le script si nécessaire.
- En cas d'erreurs liées à certaines URLs (ex : vidéo introuvable sur Vimeo), le script continuera avec les autres vidéos et affichera un message d'erreur clair.

## Auteurs

Ce projet a été développé pour simplifier le téléchargement et la gestion des vidéos dans différents formats, avec un support complet pour la conversion en MP4.