# Contrôle d'Écran Samsung à Distance

Ce projet permet de contrôler un écran Samsung à distance via une connexion WebSocket en utilisant l'API Samsung Smart TV. Le projet inclut deux scripts Python principaux : un pour le contrôle de l'écran et un autre pour récupérer des informations détaillées sur l'écran.

## Fonctionnalités

- **Connexion à l'écran Samsung via WebSocket**
- **Obtention et stockage d'un token d'authentification pour les connexions futures**
- **Envoi de commandes de contrôle à l'écran (ex. : allumer/éteindre l'écran, régler le volume)**
- **Récupération des informations détaillées de l'écran via l'API**
- **Affichage de l'état d'alimentation de l'écran**

## Prérequis

- Python 3.x
- Les bibliothèques Python suivantes :
  - `requests`
  - `websocket-client`
  - `ssl`
  - `json`
  - `os`

Vous pouvez installer les dépendances en utilisant `pip` :

```bash
pip install requests websocket-client
```

## Structure du Projet

Le dossier `Samsung Remote Control` contient les deux scripts principaux :

- **`samsung_remote_control.py`** : 
  - Ce script permet de se connecter à un téléviseur Samsung via WebSocket. Lors de la première connexion, il obtient un token d'authentification, qui est ensuite utilisé pour les connexions futures. Une fois connecté, il permet d'envoyer des commandes à l'écran, comme allumer ou éteindre l'écran, augmenter ou diminuer le volume, etc.

- **`samsung_tv_info.py`** : 
  - Ce script récupère des informations détaillées sur le téléviseur à partir de l'API Samsung, disponible à l'adresse `http://192.168.100.10:8001/api/v2/`. Il affiche d'abord toutes les informations sous forme de JSON, puis extrait et montre l'état d'alimentation (`PowerState`) de l'écran.

## Utilisation

### 1. Exécution du Script de Contrôle à Distance (`samsung_remote_control.py`)

1. Assurez-vous que l'écran Samsung est connecté au même réseau que votre ordinateur.
2. Lancez le script en utilisant Python :

   ```bash
   python samsung_remote_control.py
   ```

3. Lors de la première exécution, vous devrez autoriser la connexion sur l'écran pour récupérer un token d'authentification.
4. Ensuite, entrez la commande que vous souhaitez envoyer à l'écran (ex. : `KEY_POWER` pour allumer ou éteindre l'écran).

### Exemple de commandes

Voici quelques commandes que vous pouvez envoyer :

- **`KEY_POWER`** : Allume/éteint l'écran.
- **`KEY_VOLUMEUP`** : Augmente le volume.
- **`KEY_VOLUMEDOWN`** : Diminue le volume.
- **`KEY_MUTE`** : Coupe/restaure le son.

### 2. Exécution du Script de Récupération des Informations (`samsung_tv_info.py`)

1. Assurez-vous que l'écran Samsung est connecté au même réseau que votre ordinateur.
2. Lancez le script en utilisant Python :

   ```bash
   python samsung_tv_info.py
   ```

3. Le script affichera toutes les informations récupérées sous forme de JSON, suivies de l'état d'alimentation de l'écran.

## Explication des Scripts

### `samsung_remote_control.py`

- **Connexion à l'écran :**
  - Le script tente de se connecter à l'écran via WebSocket, d'abord en utilisant le port 8002 (connexion sécurisée `wss`), puis en essayant le port 8001 si la première tentative échoue.
  
- **Obtention et stockage du token :**
  - Lors de la première connexion, un token d'authentification est généré et doit être validé sur l'écran. Ce token est ensuite sauvegardé dans un fichier `token.txt` pour les connexions futures.
  
- **Envoi de commandes :**
  - Une fois connecté, le script permet d'envoyer des commandes (telles que `KEY_POWER`, `KEY_VOLUP`, etc.) à l'écran.

### `samsung_tv_info.py`

- **Récupération des informations de l'API :**
  - La fonction `get_tv_info(api_url)` envoie une requête GET à l'API Samsung pour récupérer les informations du téléviseur.
  - Si la requête est réussie, elle retourne les données JSON obtenues. En cas d'échec, elle renvoie `None` et affiche un message d'erreur.

- **Affichage des informations JSON :**
  - La fonction `display_tv_info(tv_info)` affiche toutes les informations récupérées en format JSON, avec une indentation pour faciliter la lecture.

- **Affichage de l'état d'alimentation :**
  - La fonction `display_power_state(tv_info)` vérifie si les informations du téléviseur contiennent une clé `PowerState`. Si c'est le cas, elle affiche l'état d'alimentation. Sinon, elle affiche un message indiquant que l'état d'alimentation n'a pas pu être récupéré.

- **Main Function :**
  - Le script définit l'URL de l'API, récupère les informations du téléviseur en appelant `get_tv_info`, puis affiche l'état d'alimentation en appelant `display_power_state`.

## Suggestions d'Amélioration

- **Gestion améliorée des erreurs** : Ajouter plus de robustesse dans la gestion des erreurs et des exceptions.
- **Automatisation des commandes courantes** : Créer des fonctions spécifiques pour envoyer des commandes fréquemment utilisées.
- **Interface utilisateur** : Intégrer une interface utilisateur graphique (GUI) pour un contrôle plus intuitif.
- **Chiffrement du token** : Sécuriser le token en le chiffrant avant de le sauvegarder.
- **Logs et suivi** : Implémenter un système de logs pour suivre l'activité du script.
