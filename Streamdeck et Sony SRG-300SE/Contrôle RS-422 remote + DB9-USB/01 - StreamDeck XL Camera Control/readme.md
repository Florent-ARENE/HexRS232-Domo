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
3. **Intégration Tally avec ATEM** : Les boutons 7, 15, 23, 31 affichent l'état **Program** (rouge) et **Preview** (vert) pour les caméras connectées à l'ATEM.
4. **Sauvegarde rapide des presets** : Enregistrez les presets dans un fichier `save.conf` via le bouton 16, qui est chargé automatiquement au démarrage du script.
5. **Verbose détaillé** : Le script affiche des messages dans la console pour chaque action (enregistrement/rappel de preset, changement de mode, etc.).

## Utilisation

### Pré-requis

Installez les dépendances suivantes :

```bash
pip install StreamDeck pyserial Pillow PyATEMMax
```

### Étapes pour utiliser le script :

1. **Connectez le Stream Deck XL** et les caméras à votre ordinateur.
2. **Connectez l'ATEM** pour gérer le Tally (adresse IP à configurer dans le script).
3. **Lancez le script** `streamdeck_XL.py`.
4. **Utilisez les boutons pour interagir** :
   - **Bouton 8** : Basculer entre le mode **STORE** et **RECALL**.
   - **Boutons 1 à 6, 9 à 14, 17 à 22, 25 à 30** : Enregistrer ou rappeler des presets selon le mode sélectionné.
   - **Boutons 7, 15, 23, 31** : Sélectionner la caméra en mode **STORE** et afficher l'état **Tally** en mode **RECALL**.
   - **Bouton 16** : Sauvegarder la configuration actuelle dans `save.conf`.

## Fonctionnement

1. **Mode STORE** : Enregistrer des presets pour la caméra active. Si un preset existe déjà pour un bouton, il est écrasé.
2. **Mode RECALL** : Rappeler les presets enregistrés pour la caméra active.
3. **Sauvegarde et chargement** : Le fichier `save.conf` enregistre les presets pour chaque caméra. Il est chargé au démarrage du script pour restaurer les états précédents.

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

---

## Remerciements

Merci à tous ceux qui ont contribué à ce projet pour en faire une solution complète et fiable pour le contrôle de caméras avec un **Stream Deck XL**.
