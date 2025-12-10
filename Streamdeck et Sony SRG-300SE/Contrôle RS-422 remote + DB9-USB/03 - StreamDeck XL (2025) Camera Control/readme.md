# StreamDeck XL Camera Control avec gestion avancée des presets et Tally

## Introduction

Ce projet permet de contrôler jusqu'à **6 caméras Sony BRC-Z700** via un **Stream Deck XL**, en utilisant des commandes **VISCA** pour gérer et rappeler des presets pour chaque caméra. Il inclut également l'intégration d'un système **Tally** via un **ATEM**, permettant d'afficher sur le **Stream Deck** quelles caméras sont en **Program** (rouge) et en **Preview** (vert).

Le projet prend en charge les modes **STORE** (enregistrement) et **RECALL** (rappel) des presets, avec un basculement simple entre ces deux modes via un bouton **toggle**.

> 📘 **Documentation technique** : Pour les détails du protocole ATEM UDP et l'implémentation de `atem_client.py`, consultez le [README Technique](readme_technique.md).

## Fonctionnalités

1. **Contrôle multi-caméras avec presets** : Contrôlez jusqu'à 6 caméras et gérez les presets pour chacune d'elles. Chaque caméra peut avoir ses propres presets enregistrés et rappelés indépendamment.
2. **Modes STORE/RECALL** :
   - **STORE** : Enregistrement de presets via les boutons 8 à 31.
   - **RECALL** : Rappel des presets via les mêmes boutons.
   - **Toggle** via le bouton 0 pour basculer entre les modes.
3. **Intégration Tally avec ATEM** : Les boutons 3 à 7 affichent l'état **Program** (rouge) et **Preview** (vert) pour les caméras connectées à l'ATEM. Le Tally est mis à jour automatiquement en mode RECALL.
4. **Contrôle ATEM natif** : Changement de Preview et transitions AUTO via protocole UDP natif (sans dépendance PyATEMMax).
5. **Sauvegarde rapide des presets** : Enregistrez les presets dans un fichier `save.conf` via le bouton 1 (SAVE), qui est chargé automatiquement au démarrage du script.
6. **Interruption des séquences** : Possibilité d'arrêter une séquence de rappel en cours en appuyant sur le bouton RECALL clignotant.
7. **Séquence intelligente** : La séquence de rappel s'adapte automatiquement selon que la caméra cible est la même ou différente de celle en Program.
8. **Initialisation automatique** : Au démarrage, le système force automatiquement le style de transition MIX sur l'ATEM pour garantir des transitions fluides.
9. **Verbose détaillé** : Le script affiche des messages dans la console pour chaque action (enregistrement/rappel de preset, changement de mode, etc.). Les logs incluent aussi la gestion des erreurs (commandes série, configuration).

## Aperçu des Modes

### Mode RECALL
En mode **RECALL**, le bouton **SAVE** est vert clair si toutes les configurations sont sauvegardées. Les boutons Caméras (3 à 7) indiquent l'état **Program** (rouge) ou **Preview** (vert) pour les caméras connectées.

![Mode RECALL](imgs/recall.png)

### Mode STORE
En mode **STORE**, le bouton **SAVE** devient jaune dès qu'un changement non sauvegardé est détecté. Les caméras sont sélectionnables avec des boutons en bleu pour l'affichage actif.

![Mode STORE](imgs/store.png)

## Prérequis

### Matériel requis :

- **Caméras Sony BRC-Z700** (jusqu'à 6)
- **Stream Deck XL** avec **32 boutons**
- **Adaptateur DB9/USB** pour connecter la caméra à votre PC
- **DSD TECH SH-G01B Isolateur USB** (pour éviter les interférences entre la télécommande RM-IP10 et l'ordinateur)
- **Blackmagic ATEM** (testé avec ATEM Mini, compatible autres modèles)
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

Si Python n'est pas trouvé dans votre PATH après l'installation :

1. **Ouvrez les Paramètres Système Avancés** sur Windows.
2. **Cliquez sur Variables d'environnement**.
3. **Ajoutez un nouveau chemin** vers le dossier d'installation de Python (exemple : `C:\Python39`) dans la variable PATH.

#### Installation des dépendances Python

Installez les bibliothèques nécessaires via **pip** :

```bash
pip install StreamDeck hidapi pyserial Pillow
```

> **Note** : PyATEMMax n'est plus nécessaire. Le projet utilise maintenant `atem_client.py`, un client ATEM UDP natif développé spécifiquement pour ce projet.

### Gestion des dépendances HIDAPI sur Windows

Si vous rencontrez des erreurs avec **hidapi**, suivez les étapes ci-dessous pour ajouter manuellement les fichiers **DLL** :

1. Téléchargez le fichier `hidapi.dll` depuis [hidapi releases](https://github.com/libusb/hidapi/releases).
2. Placez le fichier dans **C:\Windows\System32** (pour les systèmes 64-bit) ou **C:\Windows\SysWOW64** (pour les systèmes 32-bit).

## Configuration

### Adresse IP ATEM

Modifier dans `atem.py` (fonction `connect_to_atem()`) :
```python
switcher.connect('172.18.29.12')  # Remplacer par l'IP de votre ATEM
```

### Port série VISCA

Modifier dans `camera.py` :
```python
def send_command(command, port='COM8', baudrate=38400):
```

### Mapping Caméras ↔ Inputs ATEM

Modifier dans `tally.py` :
```python
camera_input_map = {
    1: 1,   # Caméra 1 → ATEM input 1
    2: 2,   # Caméra 2 → ATEM input 2
    3: 3,   # Caméra 3 → ATEM input 3
    4: 4,   # Caméra 4 → ATEM input 4
    5: 5,   # Caméra 5 → ATEM input 5
    6: 6    # Caméra 6 → ATEM input 6
}
```

## Utilisation

### Étapes pour utiliser le script :

1. **Connectez le Stream Deck XL** et les caméras à votre ordinateur.
2. **Connectez l'ATEM** au même réseau (adresse IP à configurer dans `atem.py`).
3. **Lancez le script** :
   ```bash
   python streamdeck_XL.py
   ```
4. **Utilisez les boutons pour interagir** :
   - **Bouton 0** : Basculer entre le mode **STORE** et **RECALL**.
   - **Bouton 1** : Sauvegarder la configuration actuelle dans `save.conf`.
   - **Bouton 2** : Changer de page sur le Stream Deck.
   - **Boutons 3 à 7** : Sélectionner une caméra active (STORE) / Afficher Tally (RECALL).
   - **Boutons 8 à 31** : Enregistrer ou rappeler des presets selon le mode sélectionné.

## Fonctionnement

1. **Mode STORE** : Enregistrer des presets pour la caméra active. Si un preset existe déjà pour un bouton, il est écrasé.
2. **Mode RECALL** : Rappeler les presets enregistrés. Si un preset n'existe pas, une erreur est loggée.
3. **Gestion du Tally** : En mode RECALL, le Tally affiche les caméras en **Program** et **Preview** via l'ATEM.

### Support des 6 caméras

Le système prend en charge **6 caméras** pour l'enregistrement et le rappel des presets :

| Caméra | Adresse VISCA | Input ATEM (défaut) | Rôle |
|--------|---------------|---------------------|------|
| CAM 1 | `0x81` | Input 1 | Caméra standard |
| CAM 2 | `0x82` | Input 2 | Caméra standard |
| CAM 3 | `0x83` | Input 3 | Caméra standard |
| CAM 4 | `0x84` | Input 4 | Caméra standard |
| CAM 5 | `0x85` | Input 5 | Caméra standard |
| CAM 6 | `0x86` | Input 6 | Caméra de transition (plan large/flou) |

**Note** : La caméra 6 est utilisée par défaut comme caméra de transition avec :
- **Preset 16** : Plan large (utilisé pour masquer les mouvements)
- **Preset 15** : Plan flou (position de repos)

Cette configuration peut être modifiée dans `sequences.py` si vous souhaitez utiliser une autre caméra pour les transitions.

## Phase d'initialisation ATEM

Au démarrage, le système exécute une **phase d'initialisation** qui configure automatiquement l'ATEM :

1. **Style de transition** : Force le mode **MIX** sur ME0 (évite les surprises si l'ATEM était en WIPE ou DVE)

Cette phase est extensible pour ajouter d'autres configurations automatiques à l'avenir.

### Messages console à l'initialisation

```
Connecté à l'ATEM... OK

==================================================
📋 Phase d'initialisation ATEM
==================================================
  Style de transition ME0: WIPE
  → Passage de WIPE à MIX
  ✓ Style maintenant: MIX
==================================================
✅ Initialisation terminée
==================================================
```

## Séquence de Rappel de Preset (Intelligente)

Le système utilise une **séquence intelligente** qui s'adapte automatiquement selon le contexte :

### Cas 1 : Caméra différente de celle en Program (~3 secondes)

Si vous rappelez un preset sur une caméra **différente** de celle actuellement en Program, la transition masque naturellement le mouvement de la caméra. La séquence est donc raccourcie :

```
1. Rappel du preset sur la caméra cible
2. Temporisation 1.5s (la caméra se cale)
3. Passage de la caméra cible en Preview
4. Transition AUTO (MIX)
```

**Message console** : `📷 Caméra différente (2 → 4) - Transition directe`

### Cas 2 : Même caméra que celle en Program (~9 secondes)

Si vous rappelez un preset sur la **même caméra** que celle en Program, il faut masquer le mouvement avec un plan de coupe. La séquence complète est utilisée :

```
1. Rappel preset 16 sur caméra 6 (plan large)
2. Temporisation 2s
3. Passage caméra 6 en Preview
4. Transition AUTO (vers plan large)
5. Rappel preset de la caméra cible
6. Temporisation 2s (la caméra se cale)
7. Passage caméra cible en Preview
8. Transition AUTO (vers caméra cible)
9. Rappel preset 15 sur caméra 6 (plan flou)
```

**Message console** : `📷 Même caméra (3) - Passage par plan large`

### Feedback visuel pendant la séquence

Pendant l'exécution de la séquence :

- **Bouton RECALL (0)** : Effet de pulsation rouge (breathing) indiquant que la séquence est en cours
- **Interactions bloquées** : Tous les boutons sont désactivés jusqu'à la fin de la séquence
- **Affichage figé** : Le Tally et les autres boutons ne sont pas mis à jour

### Interruption d'une séquence

En cas d'erreur d'appui ou pour annuler une séquence en cours :

1. **Appuyez sur le bouton RECALL** (bouton 0) pendant qu'il clignote
2. La séquence s'arrête immédiatement (délai max ~100ms)
3. Un message `🛑 Séquence interrompue...` s'affiche dans la console
4. Le bouton RECALL revient à son état normal (rouge foncé)
5. Le système est prêt pour une nouvelle action

> **Note** : L'interruption arrête la séquence à l'étape en cours. Les actions déjà exécutées (transitions, presets rappelés) ne sont pas annulées.

## Commandes VISCA pour la Caméra BRC-Z700

Les **commandes VISCA** permettent de contrôler la caméra via une connexion série.

### Enregistrement de preset

- **Enregistrer preset 1** : `81 01 04 3F 01 00 FF`
- **Enregistrer preset 2** : `81 01 04 3F 01 01 FF`

### Rappel de preset

- **Rappeler preset 1** : `81 01 04 3F 02 00 FF`
- **Rappeler preset 2** : `81 01 04 3F 02 01 FF`

### Adressage multi-caméras

Le premier byte indique la caméra cible :
- `0x81` = Caméra 1
- `0x82` = Caméra 2
- `0x86` = Caméra 6

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

| Fichier | Rôle |
|---------|------|
| `streamdeck_XL.py` | Fichier principal, orchestration générale |
| `streamdeck.py` | Initialisation et gestion des événements Stream Deck |
| `presets.py` | Gestion des presets (enregistrement, rappel, sauvegarde) |
| `sequences.py` | Séquences de rappel intelligentes avec logique conditionnelle |
| `camera.py` | Commandes série VISCA |
| `tally.py` | Affichage Tally (Program/Preview) |
| `atem.py` | Interface ATEM (wrapper compatible PyATEMMax) + initialisation |
| `atem_client.py` | Client ATEM UDP natif |
| `display.py` | Création des images pour les boutons |

> 📘 Pour les détails techniques de `atem_client.py` et du protocole ATEM, voir [readme_technique.md](readme_technique.md).

### Versions alternatives

| Fichier | Description |
|---------|-------------|
| `sequences.py` | **Version principale** - Séquence intelligente (courte ou complète selon le contexte) |
| `sequences_legacy.py` | Version legacy - Toujours la séquence complète de 9 étapes |

### Relations entre les fichiers

```
streamdeck_XL.py (main)
    ├── streamdeck.py      → Initialisation et événements Stream Deck
    ├── presets.py         → Logique des presets (lance séquences en thread)
    │   ├── sequences.py   → Séquences intelligentes + interruption
    │   │   └── atem.py    → Interface ATEM + initialisation
    │   │       └── atem_client.py  → Client UDP natif
    │   └── camera.py      → Commandes VISCA série
    ├── tally.py           → Affichage Program/Preview
    │   └── atem.py        → Lecture état ATEM
    └── display.py         → Rendu des boutons
```

### Arborescence des fichiers

```
📂 StreamDeck XL Camera Control
│
├── 📜 streamdeck_XL.py         # Fichier principal du script
├── 📜 streamdeck.py            # Gestion du Stream Deck
├── 📜 presets.py               # Gestion des presets (enregistrement, rappel, sauvegarde)
├── 📜 sequences.py             # Séquences intelligentes (version principale)
├── 📜 sequences_legacy.py      # Séquences complètes (version legacy)
├── 📜 camera.py                # Commandes série VISCA
├── 📜 tally.py                 # Intégration Tally via ATEM
├── 📜 atem.py                  # Interface ATEM (wrapper) + initialisation
├── 📜 atem_client.py           # Client ATEM UDP natif
├── 📜 display.py               # Création des images pour les boutons
├── 📜 readme.md                # Ce fichier
├── 📜 readme_technique.md      # Documentation technique ATEM
└── 📂 imgs/
    ├── 🖼️ recall.png
    └── 🖼️ store.png
```

## Dépannage

### L'ATEM ne répond pas aux commandes

1. Vérifier l'adresse IP dans `atem.py`
2. Vérifier que le port 9910/UDP est accessible
3. Vérifier les logs de connexion (doit afficher "Connecté à l'ATEM... OK")

### Le Tally ne se met pas à jour

1. Vérifier le mapping `camera_input_map` dans `tally.py`
2. Vérifier que les sources sont bien connectées sur l'ATEM

### Les commandes VISCA ne fonctionnent pas

1. Vérifier le port COM dans `camera.py`
2. Vérifier le câblage DB9/USB
3. Vérifier le baudrate (38400)

### La séquence ne s'interrompt pas

1. Vérifier que vous appuyez bien sur le bouton 0 (RECALL) pendant le clignotement
2. L'arrêt peut prendre jusqu'à 100ms pour être effectif
3. Vérifier les messages dans la console (`🛑 Séquence interrompue...`)

### La transition n'est pas en MIX

1. Vérifier les logs d'initialisation (doit afficher "Style maintenant: MIX")
2. Si le problème persiste, activer `ENSURE_MIX_TRANSITION = True` dans `sequences.py`

### Erreur "No module named PIL"

```bash
pip install Pillow
```

### Erreur "No module named StreamDeck"

```bash
pip install StreamDeck hidapi
```
