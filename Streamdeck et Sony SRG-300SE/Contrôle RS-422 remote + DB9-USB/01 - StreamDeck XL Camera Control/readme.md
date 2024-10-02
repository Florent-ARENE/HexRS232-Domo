# StreamDeck XL Camera Control avec gestion avancée des presets et Tally

## Introduction

Ce projet permet de contrôler jusqu'à **4 caméras** via un **Stream Deck XL**, en utilisant des commandes **VISCA** pour gérer et rappeler des presets pour chaque caméra. Il inclut également l'intégration d'un système **Tally** via un ATEM, permettant d'afficher sur le Stream Deck quelles caméras sont en **Program** (rouge) et en **Preview** (vert).

Le script prend en charge les modes **STORE** (enregistrement) et **RECALL** (rappel) des presets, avec un basculement simple entre les deux modes via un bouton **toggle**.

## Fonctionnalités

1. **Contrôle multi-caméras avec presets** : Contrôlez jusqu'à 4 caméras et gérez les presets pour chacune d’elles.
2. **Modes STORE/RECALL** :
   - **STORE** : Enregistrement de presets via les boutons 1 à 6, 9 à 14, 17 à 22, 25 à 30.
   - **RECALL** : Rappel des presets via les mêmes boutons.
   - **Toggle** via le bouton 8 pour basculer entre les modes.
3. **Intégration Tally avec ATEM** : Les boutons 7, 15, 23, 31 affichent l'état **Program** (rouge) et **Preview** (vert) pour les caméras connectées à l'ATEM. Le Tally est mis à jour automatiquement en mode RECALL.
4. **Sauvegarde rapide des presets** : Enregistrez les presets dans un fichier `save.conf` via le bouton 16, qui est chargé automatiquement au démarrage du script.
5. **Verbose détaillé** : Le script affiche des messages dans la console pour chaque action (enregistrement/rappel de preset, changement de mode, etc.). Les logs incluent aussi la gestion des erreurs (commandes série, configuration).

## Utilisation

### Pré-requis

Installez les dépendances suivantes :

```bash
pip install StreamDeck pyserial Pillow PyATEMMax
```

### Étapes pour utiliser le script :

1. **Connectez le Stream Deck XL** et les caméras à votre ordinateur.
2. **Connectez l'ATEM** pour gérer le Tally (adresse IP à configurer dans le script).
3. **Lancez le script** `streamdeck_XL.py` complet [ici](./streamdeck_XL.py).
4. **Utilisez les boutons pour interagir** :
   - **Bouton 8** : Basculer entre le mode **STORE** et **RECALL**.
   - **Boutons 1 à 6, 9 à 14, 17 à 22, 25 à 30** : Enregistrer ou rappeler des presets selon le mode sélectionné.
   - **Boutons 7, 15, 23, 31** : Sélectionner la caméra en mode **STORE** et afficher l'état **Tally** en mode **RECALL**.
   - **Bouton 16** : Sauvegarder la configuration actuelle dans `save.conf`.

### Mode RECALL
![Mode RECALL](./imgs/recall.png)

### Mode STORE
![Mode STORE](./imgs/store.png)

## Fonctionnement

1. **Mode STORE** : Enregistrer des presets pour la caméra active. Si un preset existe déjà pour un bouton, il est écrasé. Avant suppression, une vérification est effectuée pour s'assurer que le preset existe bien.
2. **Mode RECALL** : Rappeler les presets enregistrés pour la caméra active. Si un preset n'existe pas pour une caméra donnée, une erreur est loggée dans le verbose.
3. **Sauvegarde et chargement** : Le fichier `save.conf` enregistre les presets pour chaque caméra. Il est chargé au démarrage du script pour restaurer les états précédents.
4. **Gestion du Tally** : En mode RECALL, le Tally est mis à jour pour afficher les caméras actuellement en **Program** et **Preview** sur l'ATEM.

## Fichier de configuration `save.conf`

Exemple de configuration :

```json
{
    "preset_camera_map": [
        [1, [1, 1]],
        [2, [2, 1]],
        [3, [3, 1]],
        [4, [4, 1]]
    ],
    "camera_preset_count": {
        "1": 2,
        "2": 2,
        "3": 1,
        "4": 1
    }
}
```

## Explications techniques

- **Gestion des trous dans les presets** : Le script ajuste automatiquement les numéros de preset en comblant les trous laissés par les presets supprimés.
- **Intégration Tally** : Utilisation de l'API **PyATEMMax** pour afficher l'état des caméras (rouge pour **Program**, vert pour **Preview**).
- **Verbose détaillé** : Le script affiche chaque action (changement de mode, enregistrement/rappel de preset, sélection de caméra) dans la console pour un suivi en temps réel.

## Arborescence des fichiers

Le projet est structuré comme suit :

```
📂 **StreamDeck XL Camera Control**
│
│
├── 📜 **streamdeck_XL.py**         # Fichier principal (main) du script, gère l'initialisation
│                                    des modules et le fonctionnement global
│
├── 📜 **streamdeck.py**            # Gestion spécifique du Stream Deck : affichage, boutons,
│                                    événements et basculement entre les modes STORE/RECALL
│
├── 📜 **presets.py**               # Gestion des presets pour chaque caméra (enregistrement,
│                                    rappel, sauvegarde, chargement)
│
├── 📜 **camera.py**                # Gestion des commandes série VISCA pour contrôler les caméras
│
├── 📜 **tally.py**                 # Gestion de l'intégration Tally via l'ATEM (Program/Preview)
│
├── 📜 **atem.py**                  # Connexion et gestion de la communication avec l'ATEM
│
└── 📜 **display.py**               # Création des images pour les boutons du Stream Deck
```

Cette arborescence décrit la structure du projet et les responsabilités de chaque fichier. Les images dans le dossier **imgs** illustrent les différents modes du Stream Deck (STORE/RECALL) pour la documentation.


## Remerciements

Merci à tous ceux qui ont contribué à ce projet pour en faire une solution complète et fiable pour le contrôle de caméras avec un **Stream Deck XL**.