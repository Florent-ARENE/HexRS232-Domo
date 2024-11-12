# StreamDeck XL Camera Control avec gestion avancée des presets et Tally

## Introduction

Ce projet permet de contrôler jusqu'à **4 caméras Sony BRC-Z700** via un **Stream Deck XL**, en utilisant des commandes **VISCA** pour gérer et rappeler des presets pour chaque caméra. Il inclut également l'intégration d'un système **Tally** via un **ATEM**, permettant d'afficher sur le **Stream Deck** quelles caméras sont en **Program** (rouge) et en **Preview** (vert).

Le projet prend en charge les modes **STORE** (enregistrement) et **RECALL** (rappel) des presets, avec un basculement simple entre ces deux modes via un bouton **toggle**.

## Fonctionnalités

1. **Contrôle multi-caméras avec presets** : Contrôlez jusqu'à 4 caméras et gérez les presets pour chacune d’elles.
2. **Modes STORE/RECALL** :
   - **STORE** : Enregistrement de presets via les boutons 1 à 6, 9 à 14, 17 à 22, 25 à 30.
   - **RECALL** : Rappel des presets via les mêmes boutons.
   - **Toggle** via le bouton 8 pour basculer entre les modes.
3. **Intégration Tally avec ATEM** : Les boutons 7, 15, 23, 31 affichent l'état **Program** (rouge) et **Preview** (vert) pour les caméras connectées à l'ATEM. Le Tally est mis à jour automatiquement en mode RECALL.
4. **Sauvegarde rapide des presets** : Enregistrez les presets dans un fichier `save.conf` via le bouton 16, qui est chargé automatiquement au démarrage du script.
5. **Verbose détaillé** : Le script affiche des messages dans la console pour chaque action (enregistrement/rappel de preset, changement de mode, etc.). Les logs incluent aussi la gestion des erreurs (commandes série, configuration).

## Aperçu des Modes

### Mode RECALL
En mode **RECALL**, le bouton **SAVE** est vert si toutes les configurations sont sauvegardées. Les boutons Caméras (7, 15, 23, 31) indiquent l'état **Program** (rouge) ou **Preview** (vert) pour les caméras connectées.

![Mode RECALL](imgs/recall.png)

### Mode STORE
En mode **STORE**, le bouton **SAVE** devient orange dès qu'un changement non sauvegardé est détecté. Les caméras sont sélectionnables avec des boutons en bleu pour l'affichage actif.

![Mode STORE](imgs/store.png)

## Prérequis

### Matériel requis :

- **Caméra Sony BRC-Z700**
- **Stream Deck XL** avec **32 boutons**
- **Adaptateur DB9/USB** pour connecter la caméra à votre PC
- **DSD TECH SH-G01B Isolateur USB** (pour éviter les interférences entre la télécommande RM-IP10 et l'ordinateur)
- **Python 3.x** installé sur votre ordinateur

### Installation de Python et des Dépendances

#### Étapes d'installation de Python :

1. **Téléchargez Python** depuis [python.org](https://www.python.org/downloads/) ou depuis le Microsoft Store.
2. **Installez Python** en cochant la case "Add Python to PATH" (Ajouter Python au PATH).
3. **Vérifiez l'installation** en ouvrant un terminal (ou PowerShell sur Windows) et en exécutant :
   ```bash
   python --version
   ```
   Vous devriez voir la version de Python installée.

#### Ajout de Python aux variables d'environnement

Si Python n’est pas trouvé dans votre PATH après l’installation :

1. **Ouvrez les Paramètres Système Avancés** sur Windows.
2. **Cliquez sur Variables d’environnement**.
3. **Ajoutez un nouveau chemin** vers le dossier d’installation de Python (exemple : `C:\Python39`) dans la variable PATH.

#### Installation des dépendances Python

Installez les bibliothèques nécessaires via **pip** :

```bash
pip install StreamDeck hidapi pyserial Pillow PyATEMMax
```

### Gestion des dépendances HIDAPI sur Windows

Si vous rencontrez des erreurs avec **hidapi**, suivez les étapes ci-dessous pour ajouter manuellement les fichiers **DLL** :

1. Téléchargez le fichier `hidapi.dll` depuis [hidapi releases](https://github.com/libusb/hidapi/releases).
2. Placez le fichier dans **C:\Windows\System32** (pour les systèmes 64-bit) ou **C:\Windows\SysWOW64** (pour les systèmes 32-bit).

## Utilisation

### Étapes pour utiliser le script :

1. **Connectez le Stream Deck XL** et les caméras à votre ordinateur.
2. **Connectez l'ATEM** pour gérer le Tally (adresse IP à configurer dans le script).
3. **Lancez le script** `streamdeck_XL.py`.
4. **Utilisez les boutons pour interagir** :
   - **Bouton 8** : Basculer entre le mode **STORE** et **RECALL**.
   - **Boutons 1 à 6, 9 à 14, 17 à 22, 25 à 30** : Enregistrer ou rappeler des presets selon le mode sélectionné.
   - **Boutons 7, 15, 23, 31** : Sélectionner la caméra en mode **STORE** et afficher l'état **Tally** en mode **RECALL**.
   - **Bouton 16** : Sauvegarder la configuration actuelle dans `save.conf`.

## Commandes VISCA pour la Caméra BRC-Z700

Les **commandes VISCA** permettent de contrôler la caméra via une connexion série.

### Enregistrement de preset

- **Enregistrer preset 1** : `81 01 04 3F 01 00 FF`
- **Enregistrer preset 2** : `81 01 04 3F 01 01 FF`

### Rappel de preset

- **Rappeler preset 1** : `81 01 04 3F 02 00 FF`
- **Rappeler preset 2** : `81 01 04 3F 02 01 FF`

## Fonctionnement

1. **Mode STORE** : Enregistrer des presets pour la caméra active. Si un preset existe déjà pour un bouton, il est écrasé.
2. **Mode RECALL** : Rappeler les presets enregistrés. Si un preset n'existe pas, une erreur est loggée.
3. **Gestion du Tally** : En mode RECALL, le Tally affiche les caméras en **Program** et **Preview** via l'ATEM.

## Sauvegarde et Chargement de la Configuration

Le fichier `save.conf` enregistre les presets pour chaque caméra et est chargé automatiquement au démarrage du script.

Exemple de fichier `save.conf` :

```json
{
    "preset_camera_map": [
        [1, 1],
        [2, 2],
        [3, 1],
        [4, 1]
    ],
    "camera_preset_count": {
        "1": 2,
        "2": 2,
        "3": 1,
        "4": 1
    }
}
```

## Description détaillée des fichiers

#### 1. **streamdeck_XL.py** (fichier principal)
   - **Rôle** : Initialise l'interface avec le Stream Deck et définit la logique de basculement entre les modes "STORE" et "RECALL". Gère les boutons et le rappel/sauvegarde des presets.
   - **Fonctions clés** :
     - `update_display(deck)`: Gère l'interface en fonction du mode sélectionné (STORE ou RECALL).
     - `change_page()`: Permet de naviguer entre les pages du Stream Deck.
     - `streamdeck_callback(deck, key, state)`: Callback principal pour la gestion des actions sur les boutons. Oriente les actions vers `handle_streamdeck_event` selon le bouton pressé.

#### 2. **presets.py**
   - **Rôle** : Gère la création, le rappel, l’enregistrement et le chargement des presets pour chaque caméra.
   - **Fonctions clés** :
     - `get_real_button_number(button_number)`: Calcule l'identifiant global d’un bouton selon la page.
     - `enregistrer_preset(deck, key, camera_number, recording_enabled, page)`: Enregistre les presets avec gestion d'incrémentation et d’écrasement.
     - `rappeler_preset(deck, key, page)`: Rappelle le preset assigné à un bouton spécifique.
     - `save_configuration(deck)`, `load_configuration(deck)`: Sauvegarde et charge les presets depuis `save.conf`.
     - `adjust_camera_preset_count()`: Assure la cohérence du comptage des presets par caméra.
     - `set_current_page(page)`: Synchronise la page actuelle avec `streamdeck_XL.py`.

#### 3. **streamdeck.py**
   - **Rôle** : Initialise et gère les interactions basiques avec le Stream Deck (affichage de boutons et événements).
   - **Fonctions clés** :
     - `initialize_streamdeck()`: Initialise le Stream Deck.
     - `update_camera_buttons(deck, camera_number, recording_enabled)`: Mets à jour l'affichage des caméras en mode STORE.
     - `set_toggle_button(deck, mode)`: Gère le bouton de bascule entre les modes.
     - `handle_streamdeck_event(deck, key, state, camera_number, recording_enabled, save_configuration, enregistrer_preset, rappeler_preset)`: Délègue les actions de bouton selon le contexte.

#### 4. **display.py**
   - **Rôle** : Crée les images pour les boutons en fonction de l’état (couleur, texte).
   - **Fonctions clés** :
     - `create_button_image(deck, text, color)`: Génère une image de bouton.
     - `update_save_button(deck, config_changed)`: Change l'affichage du bouton SAVE selon les changements non sauvegardés.

#### 5. **tally.py**
   - **Rôle** : Affiche l’état du Tally sur le Stream Deck pour les caméras en Program et Preview.
   - **Fonctions clés** :
     - `update_tally(deck)`: Assure la mise à jour de l’état Program et Preview sur le Stream Deck【470†source】.

#### 6. **camera.py**
   - **Rôle** : Gère l'envoi des commandes VISCA pour contrôler les caméras.
   - **Fonctions clés** :
     - `send_command(command)`: Envoie une commande série pour contrôler les caméras.

#### 7. **sequences.py**
   - **Rôle** : Exécute les séquences de rappel de presets.
   - **Fonctions clés** :
     - `sequence_actions(camera, preset)`: Envoie les commandes pour rappeler un preset pour une caméra spécifique.

#### 8. **atem.py**
   - **Rôle** : Interface avec l’ATEM pour récupérer et modifier les sources en Program et Preview.
   - **Fonctions clés** :
     - `connect_to_atem()`: Établit la connexion avec le switcher ATEM.


### Relations entre les fichiers

- **streamdeck_XL.py** est le fichier principal orchestrant l’ensemble des actions du Stream Deck. La fonction `streamdeck_callback` assure la logique de contrôle principal, tandis que `handle_streamdeck_event` dans **streamdeck.py** délègue les tâches aux fonctions de gestion du mode et de configuration.
  
- **presets.py** gère la logique des presets en enregistrement et en rappel, coordonnant avec **display.py** pour les changements de couleur des boutons, et **camera.py** pour envoyer les commandes VISCA.

- **tally.py** met à jour les boutons du Stream Deck en fonction des états Program et Preview des caméras via l’ATEM.

- **display.py** crée les images des boutons et fournit un retour visuel sur les actions du Stream Deck.

- **atem.py** établit la connexion avec l’ATEM pour le contrôle du Tally.

- **streamdeck.py** fournit les fonctions `initialize_streamdeck`, `set_toggle_button`, `update_camera_buttons`, et `handle_streamdeck_event`, délégant les actions spécifiques de chaque bouton aux fonctions des autres modules en fonction du mode et des configurations.

- **sequences.py** gère les séquences d'actions complexes pour chaque caméra, appelées depuis **presets.py** lors de rappels de presets.

### Arborescence des fichiers

Le projet est structuré comme suit :

```
📂 StreamDeck XL Camera Control
│
├── 📜 streamdeck_XL.py         # Fichier principal du script
├── 📜 streamdeck.py            # Gestion du Stream Deck
├── 📜 presets.py               # Gestion des presets (enregistrement, rappel, sauvegarde)
├── 📜 sequences.py             # Gestion des séquences (enregistrement, rappel, sauvegarde)
├── 📜 camera.py                # Commandes série VISCA
├── 📜 tally.py                 # Intégration Tally via ATEM
├── 📜 atem.py                  # Connexion à l'ATEM
└── 📜 display.py               # Création des images pour les boutons
```
