# README : Gestion des Presets pour la Caméra Sony BRC-Z700 via Stream Deck et remote RM-IP10 en simultané

## Introduction

Ce projet permet de contrôler une caméra **Sony BRC-Z700** en enregistrant et rappelant des **presets** à l'aide d'un **Stream Deck** connecté à un ordinateur via un port série **COM8**. Chaque bouton du **Stream Deck** est mappé pour enregistrer ou rappeler un preset spécifique.

L'objectif de ce guide est de fournir des instructions détaillées pour configurer et exécuter ce projet, ainsi que pour automatiser le contrôle de la caméra.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants :

- **Caméra Sony BRC-Z700**.
- **Stream Deck 6 boutons**.
- **Adaptateur DB9/USB** pour connecter la caméra à votre PC.
- **DSD TECH SH-G01B Isolateur USB** (pour éviter les interférences entre les commandes de la télécommande RM-IP10 et de l'ordinateur).
- **Python 3.x** installé sur votre ordinateur.

## 1. Installation des Dépendances

Le projet utilise des bibliothèques spécifiques pour interagir avec le **Stream Deck** et gérer les communications série avec la caméra. Voici les étapes pour installer les dépendances nécessaires.

### 1.1 Installation de Python et des bibliothèques

Assurez-vous que **Python** est installé sur votre machine. Si ce n'est pas le cas, téléchargez-le depuis [le site officiel](https://www.python.org/downloads/).

Une fois Python installé, installez les bibliothèques requises via **pip**. Ouvrez une invite de commande et exécutez les commandes suivantes :

```bash
pip install streamdeck hidapi pyserial Pillow
```

### 1.2 Gestion des dépendances HIDAPI sur Windows

La bibliothèque **hidapi** est utilisée pour gérer les interactions avec le **Stream Deck**. Dans la plupart des cas, l'installation via `pip install hidapi` suffit. Cependant, sur **Windows**, il peut parfois être nécessaire d'ajouter manuellement les fichiers **DLL** si vous rencontrez des problèmes lors de l'exécution.

#### Étapes pour installer HIDAPI et ajouter les DLLs (si nécessaire) :

1. **Installer HIDAPI** :
   Exécutez la commande suivante pour installer **hidapi** :
   ```bash
   pip install hidapi
   ```

2. **Tester l'installation** :
   Lancez votre script Python. Si tout fonctionne correctement, il n'est pas nécessaire d'aller plus loin.

3. **Si vous rencontrez une erreur liée à HIDAPI (backend HID non trouvé)** :
   - **Téléchargez le fichier `hidapi.dll`** depuis [hidapi releases](https://github.com/libusb/hidapi/releases).
   - **Placez le fichier `hidapi.dll`** dans l'un des emplacements suivants :
     - **C:\Windows\System32** (pour les systèmes 64-bit).
     - **C:\Windows\SysWOW64** (pour les systèmes 32-bit).
   - Vous pouvez également placer le fichier **`hidapi.dll`** dans le même répertoire que votre script Python.

4. **Ajouter le chemin à la variable d'environnement PATH** (optionnel) :
   Si vous préférez ne pas déplacer les fichiers, vous pouvez ajouter le chemin du répertoire contenant **`hidapi.dll`** à la variable **PATH** de votre système.

### 1.3 Outils Utilisés

- **Stream Deck** : Permet d'associer des actions spécifiques aux boutons physiques du périphérique.
- **PySerial** : Utilisé pour la communication série avec la caméra.
- **HIDAPI** : Utilisé pour gérer les interactions HID avec le **Stream Deck**.

## 2. Commandes VISCA pour la Caméra BRC-Z700

Les **commandes VISCA** permettent de contrôler la caméra via une connexion série. Ce projet utilise des commandes VISCA pour enregistrer et rappeler des **presets**.

### 2.1 Commandes d'enregistrement de preset

Chaque preset est enregistré en envoyant une commande spécifique à la caméra via le port série **COM8**.

- **Enregistrer preset 1** : `81 01 04 3F 01 00 FF`
- **Enregistrer preset 2** : `81 01 04 3F 01 01 FF`
- **Enregistrer preset 3** : `81 01 04 3F 01 02 FF`

### 2.2 Commandes de rappel de preset

Les boutons du **Stream Deck** sont également configurés pour rappeler les presets enregistrés.

- **Rappeler preset 1** : `81 01 04 3F 02 00 FF`
- **Rappeler preset 2** : `81 01 04 3F 02 01 FF`
- **Rappeler preset 3** : `81 01 04 3F 02 02 FF`

## 3. Structure du Script

Le script Python **streamdeck_setup.py** gère la détection des boutons du **Stream Deck** et envoie les commandes série correspondantes à la caméra.

### 3.1 Fonctionnalités

- **Boutons 0 à 2** : Enregistrer les presets 1, 2, et 3.
- **Boutons 3 à 5** : Rappeler les presets 1, 2, et 3.
- **Envoi des commandes série** : Utilisation de **PySerial** pour envoyer les commandes VISCA via le port **COM8** avec un baudrate de **38400**.

### 3.2 Exemple de code

Voici un extrait du script utilisé pour gérer les actions :

```python
import time
import serial
from StreamDeck.DeviceManager import DeviceManager

def send_command(command, port='COM8', baudrate=38400):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            print(f"Envoi de la commande : {command.hex()}")
            ser.write(command)
            time.sleep(0.1)
            response = ser.read(64)
            if response:
                print(f"Réponse reçue: {response.hex()}")
            else:
                print("Aucune réponse reçue")
    except serial.SerialException as e:
        print(f"Erreur de communication série : {e}")

def enregistrer_preset(preset_number):
    command = bytes([0x81, 0x01, 0x04, 0x3F, 0x01, preset_number, 0xFF])
    send_command(command)

def rappeler_preset(preset_number):
    command = bytes([0x81, 0x01, 0x04, 0x3F, 0x02, preset_number, 0xFF])
    send_command(command)
```

### 3.3 Gestion des événements du Stream Deck

Le script utilise une fonction de rappel pour détecter les boutons pressés et envoyer les commandes appropriées à la caméra.

```python
def handle_streamdeck_event(deck, key, state):
    if state:  # Si le bouton est pressé
        if key == 0:
            enregistrer_preset(0)  # Preset 1
        elif key == 1:
            enregistrer_preset(1)  # Preset 2
        elif key == 2:
            enregistrer_preset(2)  # Preset 3
        elif key == 3:
            rappeler_preset(0)  # Rappel Preset 1
        elif key == 4:
            rappeler_preset(1)  # Rappel Preset 2
        elif key == 5:
            rappeler_preset(2)  # Rappel Preset 3
```

### 3.4 Lancement du Script

Le script peut être lancé directement depuis une invite de commande, ou configuré pour être lancé via un bouton du **Stream Deck**.

Exemple de lancement via fichier `.bat` :

```batch
@echo off
python "streamdeck_setup.py"
pause
```

Script `streamdeck_setup.py` complet [ici](./streamdeck_setup.py).

## 4. Utilisation

### 4.1 Enregistrer un Preset

1. Positionnez la caméra avec la télécommande ou manuellement.
2. Appuyez sur l'un des boutons 0, 1, ou 2 du **Stream Deck** pour enregistrer le preset correspondant.

### 4.2 Rappeler un Preset

1. Appuyez sur l'un des boutons 3, 4, ou 5 du **Stream Deck** pour rappeler le preset enregistré.

## 5. Conclusion

Ce projet permet de piloter une caméra **Sony BRC-Z700** de manière fluide en utilisant un **Stream Deck**. Le système est extensible pour ajouter plus de presets ou gérer plusieurs caméras en parallèle. Grâce à l'automatisation via Python et les commandes VISCA, vous pouvez facilement configurer et contrôler votre caméra à distance avec précision.
