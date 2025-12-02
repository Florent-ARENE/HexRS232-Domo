# Documentation Technique - Protocole ATEM UDP

Ce document détaille le protocole de communication UDP utilisé par les switchers Blackmagic ATEM, ainsi que l'implémentation du client Python `atem_client.py`.

> 📖 Pour l'utilisation générale du projet, consultez le [README principal](readme.md).

---

## Table des matières

1. [Vue d'ensemble du protocole](#vue-densemble-du-protocole)
2. [Format des paquets](#format-des-paquets)
3. [Handshake de connexion](#handshake-de-connexion)
4. [Commandes ATEM](#commandes-atem)
5. [atem_client.py - Implémentation](#atem_clientpy---implémentation)
6. [atem.py - Wrapper PyATEMMax](#atempy---wrapper-pyatemmax)
7. [Configuration des caméras](#configuration-des-caméras)
8. [Système de feedback visuel](#système-de-feedback-visuel-sequencespy)
9. [Historique des découvertes](#historique-des-découvertes)
10. [Référence des commandes](#référence-des-commandes)

---

## Vue d'ensemble du protocole

Le switcher ATEM communique via **UDP sur le port 9910**. Le protocole est propriétaire mais a été reverse-engineered par la communauté.

### Caractéristiques principales

- **Transport** : UDP port 9910
- **Fiabilité** : Système d'ACK/retransmission au niveau applicatif
- **Session** : Identifiant de session 16-bit
- **Séquencement** : Numéros de séquence pour ordonner les paquets

---

## Format des paquets

### Structure générale

```
┌─────────────────────────────────────┐
│         Header UDP (12 bytes)       │
├─────────────────────────────────────┤
│      Command Block 1 (variable)     │
├─────────────────────────────────────┤
│      Command Block 2 (variable)     │
├─────────────────────────────────────┤
│              ...                    │
└─────────────────────────────────────┘
```

### Header UDP (12 bytes)

```
Offset  Taille  Nom             Description
------  ------  --------------  ------------------------------------------
0       1       flags_len_hi    Flags (5 bits MSB) + Length high (3 bits LSB)
1       1       len_lo          Length low (8 bits)
2-3     2       session_id      Identifiant de session (big-endian)
4-5     2       ack_num         Numéro de séquence à acquitter (big-endian)
6-7     2       reserved        Réservé (0x0000)
8-9     2       remote_seq      Séquence distante (big-endian)
10-11   2       local_seq       Séquence locale (big-endian)
```

### Flags du Header

| Bit | Masque | Nom      | Description |
|-----|--------|----------|-------------|
| 7   | 0x80   | ACK      | Paquet d'acquittement |
| 6   | 0x40   | -        | Non utilisé |
| 5   | 0x20   | RETX     | Retransmission (paquet déjà envoyé) |
| 4   | 0x10   | SYN      | Synchronisation (handshake initial) |
| 3   | 0x08   | RELIABLE | Paquet fiable, nécessite un ACK |

### Calcul de la longueur

```python
# Encodage
flags_len_hi = (flags & 0xF8) | ((length >> 8) & 0x07)
len_lo = length & 0xFF

# Décodage
length = ((flags_len_hi & 0x07) << 8) | len_lo
flags = flags_len_hi & 0xF8
```

### Format d'un Command Block

```
Offset  Taille  Nom         Description
------  ------  ----------  ------------------------------------------
0-1     2       cmd_len     Longueur totale du bloc (big-endian)
2-3     2       padding     Padding (0x0000)
4-7     4       cmd_name    Nom de commande (4 caractères ASCII)
8+      var     payload     Données de la commande
```

**Important** : La longueur des command blocks doit être alignée sur 4 bytes.

---

## Handshake de connexion

### Diagramme de séquence

```
    Client                                    ATEM
       │                                        │
       │─────── HELLO (SYN) ──────────────────>│
       │        session_id=0x53AB               │
       │        length=20                       │
       │                                        │
       │<─────── SYN-ACK ──────────────────────│
       │         session_id=0xXXXX (peut différer)
       │                                        │
       │<─────── RELIABLE packet #1 ───────────│
       │         État initial du switcher       │
       │                                        │
       │─────── ACK #1 ───────────────────────>│
       │                                        │
       │<─────── RELIABLE packet #2 ───────────│
       │                                        │
       │─────── ACK #2 ───────────────────────>│
       │                                        │
       │              ... (~118 paquets) ...    │
       │                                        │
       │<─────── RELIABLE packet #N ───────────│
       │         (dernier paquet initial)       │
       │                                        │
       │─────── ACK #N ───────────────────────>│
       │                                        │
       │═══════ CONNEXION ÉTABLIE ═════════════│
       │                                        │
       │─────── Commande (RELIABLE) ──────────>│
       │                                        │
       │<─────── ACK ──────────────────────────│
       │                                        │
```

### Paquet HELLO (SYN)

```python
def build_hello_packet(session_id=0x53AB):
    packet = bytearray(20)
    packet[0] = 0x10           # Flag SYN
    packet[1] = 0x14           # Length = 20
    packet[2] = (session_id >> 8) & 0xFF
    packet[3] = session_id & 0xFF
    packet[12] = 0x01          # Version protocole
    return bytes(packet)
```

### Paquet ACK

```python
def build_ack_packet(session_id, ack_num):
    packet = bytearray(12)
    packet[0] = 0x80           # Flag ACK
    packet[1] = 0x0C           # Length = 12
    packet[2] = (session_id >> 8) & 0xFF
    packet[3] = session_id & 0xFF
    packet[4] = (ack_num >> 8) & 0xFF
    packet[5] = ack_num & 0xFF
    return bytes(packet)
```

### Points critiques découverts

#### 1. Capture du Session ID

L'ATEM peut accepter notre Session ID ou en proposer un autre. **Il faut capturer le Session ID dès le premier paquet reçu**, pas seulement sur les paquets SYN.

```python
# CORRECT
data, addr = sock.recvfrom(2048)
session_id = (data[2] << 8) | data[3]  # Capturer immédiatement

# INCORRECT - Ne pas attendre un paquet SYN spécifique
if data[0] & 0x10:  # Seulement si SYN
    session_id = ...  # Trop tard!
```

#### 2. ACK obligatoires

**Chaque paquet avec le flag RELIABLE (0x08) doit être acquitté**, sinon :
- L'ATEM retransmet en boucle (flag RETX = 0x20)
- L'ATEM refuse d'accepter nos commandes
- La connexion ne s'établit jamais vraiment

```python
# Pour CHAQUE paquet reçu
if flags & 0x08:  # RELIABLE
    ack = build_ack_packet(session_id, remote_seq)
    sock.sendto(ack, (ip, port))
```

#### 3. Stabilisation avant commandes

L'ATEM envoie environ **118 paquets** contenant l'état complet du switcher. Il faut attendre que ce flux se stabilise avant d'envoyer des commandes.

```python
# Attendre 500ms sans nouveau paquet
last_packet_time = time.time()
while time.time() - last_packet_time < 0.5:
    try:
        data = sock.recv(2048)
        last_packet_time = time.time()
        # Traiter et ACK...
    except socket.timeout:
        pass
```

---

## Commandes ATEM

### CPvI - Change Preview Input

**Fonction** : Changer la source Preview d'un M/E

**Format du payload** (4 bytes) :
```
Offset  Taille  Description
------  ------  ------------------------------------------
0       1       ME index (0 = ME1, 1 = ME2, ...)
1       1       Réservé (0x00)
2-3     2       Source (big-endian)
```

**⚠️ IMPORTANT** : Pas de mask byte ! Contrairement à ce que suggèrent certaines documentations, le format avec un mask byte (0x01 en premier) **ne fonctionne pas**.

**Exemple - Preview vers input 2 sur ME1** :
```
Command: "CPvI"
Payload: 00 00 00 02
         │  │  └──┴── Source = 2 (big-endian)
         │  └─────── Réservé = 0x00
         └────────── ME = 0
```

**Test effectué** :
```
Format testé              Résultat
------------------------  --------
01 00 00 02 (avec mask)   ÉCHEC - ACK reçu mais Preview non changée
00 00 00 02 (sans mask)   SUCCÈS - Preview changée!
```

### CPgI - Change Program Input

**Fonction** : Changer la source Program d'un M/E

**Format identique à CPvI**

### DAut - Do Auto Transition

**Fonction** : Exécuter une transition AUTO

**Format du payload** (4 bytes) :
```
Offset  Taille  Description
------  ------  ------------------------------------------
0       1       ME index (0 = ME1)
1-3     3       Padding (0x00 0x00 0x00)
```

### DCut - Do Cut

**Fonction** : Exécuter un CUT

**Format identique à DAut**

### PrgI - Program Input (réception seulement)

**Fonction** : L'ATEM notifie la source Program actuelle

**Format du payload observé** :
```
Offset  Taille  Description
------  ------  ------------------------------------------
0       1       ME index
1       1       Byte inconnu (ignoré, souvent 0x76)
2-3     2       Source actuelle (big-endian)
```

### PrvI - Preview Input (réception seulement)

**Fonction** : L'ATEM notifie la source Preview actuelle

**Format similaire à PrgI**, parfois 8 bytes avec des données additionnelles.

---

## atem_client.py - Implémentation

### Vue d'ensemble

`atem_client.py` est un client Python pur qui communique directement avec l'ATEM via UDP. Il ne dépend d'aucune bibliothèque externe pour le protocole ATEM.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     ATEMClient                          │
├─────────────────────────────────────────────────────────┤
│  Attributs:                                             │
│    - ip, port                                           │
│    - session_id, local_seq, highest_remote              │
│    - program: {ME: source}                              │
│    - preview: {ME: source}                              │
│    - connected: bool                                    │
├─────────────────────────────────────────────────────────┤
│  Méthodes publiques:                                    │
│    - connect(timeout) -> bool                           │
│    - disconnect()                                       │
│    - get_program(me) -> int                             │
│    - get_preview(me) -> int                             │
│    - set_preview_input(me, source)                      │
│    - set_program_input(me, source)                      │
│    - do_auto(me)                                        │
│    - do_cut(me)                                         │
├─────────────────────────────────────────────────────────┤
│  Méthodes internes:                                     │
│    - _process_packet(data)                              │
│    - _parse_commands(data)                              │
│    - _send_ack(remote_seq)                              │
│    - _send_command(cmd_name, payload)                   │
│    - _recv_loop()  [thread]                             │
└─────────────────────────────────────────────────────────┘
```

### Cycle de vie

```python
# 1. Création
client = ATEMClient("172.18.29.12")

# 2. Connexion (bloquant, avec timeout)
if client.connect(timeout=10):
    # 3. Utilisation
    print(f"Program: {client.get_program(0)}")
    client.set_preview_input(0, 2)
    client.do_auto(0)
    
# 4. Déconnexion
client.disconnect()
```

### Thread de réception

Un thread daemon tourne en arrière-plan pour :
- Recevoir les paquets de l'ATEM
- Envoyer les ACK automatiquement
- Mettre à jour l'état (program, preview)

```python
def _recv_loop(self):
    while self._running:
        try:
            data, addr = self.sock.recvfrom(2048)
            self._process_packet(data)
        except socket.timeout:
            pass
```

### Construction d'une commande

```python
def _send_command(self, cmd_name, payload):
    # Incrémenter la séquence locale
    self.local_seq += 1
    
    # Command block (aligné sur 4 bytes)
    cmd_len = 8 + len(payload)
    while cmd_len % 4 != 0:
        cmd_len += 1
    
    cmd = bytearray(cmd_len)
    cmd[0:2] = cmd_len.to_bytes(2, 'big')
    cmd[4:8] = cmd_name.encode('ascii')
    cmd[8:8+len(payload)] = payload
    
    # Header
    total = 12 + cmd_len
    header = bytearray(12)
    header[0] = 0x08 | ((total >> 8) & 0x07)  # RELIABLE + length
    header[1] = total & 0xFF
    header[2:4] = self.session_id.to_bytes(2, 'big')
    header[4:6] = self.highest_remote.to_bytes(2, 'big')  # ACK
    header[10:12] = self.local_seq.to_bytes(2, 'big')
    
    self.sock.sendto(header + cmd, (self.ip, self.port))
```

---

## atem.py - Wrapper PyATEMMax

### Objectif

`atem.py` expose **exactement la même interface** que PyATEMMax, permettant aux fichiers existants (`tally.py`, `sequences.py`) de fonctionner sans modification.

### Interface émulée

```python
# Utilisation identique à PyATEMMax
from atem import switcher, connect_to_atem

connect_to_atem()

# Lecture (comme PyATEMMax)
program = switcher.programInput[0].videoSource  # "input5"
preview = switcher.previewInput[0].videoSource  # "input1"

# Commandes (comme PyATEMMax)
switcher.setPreviewInputVideoSource(0, "input2")
switcher.execAutoME(0)
```

### Classes d'émulation

```python
class VideoSourceProperty:
    """Émule switcher.programInput[0].videoSource"""
    @property
    def videoSource(self):
        value = self._get_func()
        return f"input{value}" if value else None

class InputAccessor:
    """Émule switcher.programInput[0]"""
    def __getitem__(self, index):
        return VideoSourceProperty(...)

class ATEMWrapper:
    """Émule PyATEMMax.ATEMMax()"""
    def __init__(self):
        self.programInput = InputAccessor(self._get_program)
        self.previewInput = InputAccessor(self._get_preview)
    
    def setPreviewInputVideoSource(self, me, source):
        # Convertit "input2" en 2 si nécessaire
        if isinstance(source, str):
            source = int(source.replace("input", ""))
        self._client.set_preview_input(me, source)
```

### Mapping des méthodes

| PyATEMMax | atem.py (wrapper) | ATEMClient |
|-----------|-------------------|------------|
| `switcher.programInput[0].videoSource` | Émulé | `get_program(0)` |
| `switcher.previewInput[0].videoSource` | Émulé | `get_preview(0)` |
| `switcher.setPreviewInputVideoSource(me, src)` | Émulé | `set_preview_input(me, src)` |
| `switcher.execAutoME(me)` | Émulé | `do_auto(me)` |
| `switcher.execCutME(me)` | Émulé | `do_cut(me)` |

---

## Configuration des caméras

### Vue d'ensemble

Le projet est configuré par défaut pour **6 caméras**. Cette section explique comment adapter la configuration selon votre installation.

### Fichiers à modifier

| Fichier | Paramètre | Description |
|---------|-----------|-------------|
| `presets.py` | `camera_preset_count`, `camera_presets` | Nombre de caméras supportées pour les presets |
| `tally.py` | `camera_input_map` | Mapping caméras ↔ inputs ATEM |
| `sequences.py` | `camera_input_map`, numéros de caméra | Caméra utilisée pour les plans larges/flous |
| `streamdeck.py` | `range(3, 8)` | Boutons associés aux caméras |

### 1. Nombre de caméras (presets.py)

Le dictionnaire définit combien de caméras peuvent enregistrer des presets :

```python
# Pour 6 caméras (défaut)
camera_preset_count = {i: 1 for i in range(1, 7)}  # Caméras 1 à 6
camera_presets = {i: [] for i in range(1, 7)}

# Pour 4 caméras
camera_preset_count = {i: 1 for i in range(1, 5)}  # Caméras 1 à 4
camera_presets = {i: [] for i in range(1, 5)}

# Pour 8 caméras
camera_preset_count = {i: 1 for i in range(1, 9)}  # Caméras 1 à 8
camera_presets = {i: [] for i in range(1, 9)}
```

**Important** : Modifier aussi dans `load_configuration()` du même fichier.

### 2. Mapping Caméras ↔ Inputs ATEM (tally.py)

Ce dictionnaire fait le lien entre les numéros de caméras logiques et les inputs physiques de l'ATEM :

```python
camera_input_map = {
    1: 1,   # Caméra 1 → ATEM input 1
    2: 2,   # Caméra 2 → ATEM input 2
    3: 3,   # Caméra 3 → ATEM input 3
    4: 4,   # Caméra 4 → ATEM input 4
    5: 5,   # Caméra 5 → ATEM input 5
    6: 6,   # Caméra 6 → ATEM input 6
}
```

**Exemple de configuration non-linéaire** :
```python
camera_input_map = {
    1: 1,   # Caméra 1 → ATEM input 1
    2: 3,   # Caméra 2 → ATEM input 3 (input 2 utilisé pour autre chose)
    3: 5,   # Caméra 3 → ATEM input 5
    4: 8,   # Caméra 4 → ATEM input 8
}
```

### 3. Séquences automatiques (sequences.py)

Le fichier `sequences.py` utilise une caméra dédiée pour les transitions (plan large → plan serré → plan flou). Par défaut, c'est la **caméra 6**.

```python
def sequence_actions(camera_number, preset_number):
    # Caméra utilisée pour le plan large (preset 16) et plan flou (preset 15)
    TRANSITION_CAMERA = 6
    
    # Étape 1: Plan large
    recall_preset(TRANSITION_CAMERA, 16)
    # ...
    
    # Étape 9: Plan flou
    recall_preset(TRANSITION_CAMERA, 15)
```

**Pour changer la caméra de transition**, modifier les appels `recall_preset(6, ...)` et `set_camera_preview(6)`.

### 4. Boutons du Stream Deck (streamdeck.py)

Les boutons 3 à 7 sont associés aux caméras 1 à 5 pour la sélection :

```python
# Mise à jour des boutons caméras (boutons 3-7 = CAM 1-5)
for button, camera in zip(range(3, 8), range(1, 6)):
    color = "blue" if camera == camera_number else "black"
    deck.set_key_image(button, create_button_image(deck, f"CAM {camera}", color))
```

**Pour plus de caméras** sur le Stream Deck, il faudrait :
- Utiliser des pages supplémentaires, ou
- Réorganiser le layout des boutons

### Exemple : Passer de 6 à 4 caméras

1. **presets.py** :
```python
camera_preset_count = {i: 1 for i in range(1, 5)}
camera_presets = {i: [] for i in range(1, 5)}
# Et dans load_configuration() :
camera_preset_count = config_data.get('camera_preset_count', {i: 1 for i in range(1, 5)})
camera_presets = {i: [] for i in range(1, 5)}
```

2. **tally.py** :
```python
camera_input_map = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
}
```

3. **sequences.py** : Changer la caméra de transition (ex: caméra 4 au lieu de 6)

4. **streamdeck.py** :
```python
for button, camera in zip(range(3, 7), range(1, 5)):  # Boutons 3-6 = CAM 1-4
```

### Adressage VISCA multi-caméras

Les commandes VISCA utilisent le premier octet pour identifier la caméra :

| Caméra | Premier octet | Exemple preset 1 |
|--------|---------------|------------------|
| 1 | `0x81` | `81 01 04 3F 02 00 FF` |
| 2 | `0x82` | `82 01 04 3F 02 00 FF` |
| 3 | `0x83` | `83 01 04 3F 02 00 FF` |
| 4 | `0x84` | `84 01 04 3F 02 00 FF` |
| 5 | `0x85` | `85 01 04 3F 02 00 FF` |
| 6 | `0x86` | `86 01 04 3F 02 00 FF` |
| 7 | `0x87` | `87 01 04 3F 02 00 FF` |

Le calcul dans le code :
```python
command_prefix = 0x80 + camera_number  # 0x81 pour caméra 1, 0x86 pour caméra 6
```

---

## Système de feedback visuel (sequences.py)

### Vue d'ensemble

Pendant l'exécution d'une séquence de rappel de preset, le système fournit un feedback visuel et bloque les interactions utilisateur pour éviter les actions accidentelles.

### Flag `sequence_running`

Variable globale exportée par `sequences.py` :

```python
# Dans sequences.py
sequence_running = False  # True pendant l'exécution d'une séquence

def start_blink(deck):
    global sequence_running
    sequence_running = True
    # ...

def stop_blink(deck):
    global sequence_running
    sequence_running = False
    # ...
```

### Utilisation dans streamdeck_XL.py

```python
import sequences  # Import du module entier pour accès dynamique

def update_display(deck):
    # Ne pas mettre à jour pendant une séquence
    if sequences.sequence_running:
        return
    # ...

def streamdeck_callback(deck, key, state):
    # Ignorer les événements pendant une séquence
    if sequences.sequence_running:
        return
    # ...
```

**Important** : Il faut importer le module (`import sequences`) et non la variable (`from sequences import sequence_running`), sinon la valeur ne sera pas mise à jour dynamiquement.

### Effet de pulsation (breathing)

Le bouton RECALL pulse en rouge pendant la séquence :

```python
def _blink_recall_button(deck):
    min_intensity = 30       # Rouge sombre
    max_intensity = 255      # Rouge vif
    steps = 20               # Étapes par cycle
    delay = 0.04             # 40ms entre chaque étape
    
    intensity = min_intensity
    direction = 1  # 1 = montée, -1 = descente
    step_size = (max_intensity - min_intensity) // (steps // 2)
    
    while _blink_active:
        deck.set_key_image(0, create_button_image(
            deck, "RECALL", (intensity, 0, 0), text_color="white", bold=True
        ))
        
        intensity += direction * step_size
        
        if intensity >= max_intensity:
            direction = -1
        elif intensity <= min_intensity:
            direction = 1
        
        time.sleep(delay)
```

**Paramètres de l'animation** :
- Cycle complet : ~1.6 secondes (montée + descente)
- Intensité : varie de 30 (sombre) à 255 (vif)
- Thread daemon : s'arrête automatiquement si le programme principal se termine

---

## Historique des découvertes

### Problème initial

PyATEMMax parvenait à :
- ✅ Se connecter à l'ATEM
- ✅ Lire l'état (Program, Preview)
- ❌ Envoyer des commandes (CPvI, DAut ignorées)

### Méthodologie de debug

1. **Création d'un sniffer** (`atem_sniffer.py`) pour capturer les paquets
2. **Analyse des flags** et des séquences
3. **Comparaison** avec le comportement attendu
4. **Tests itératifs** de différents formats

### Découverte #1 : ACK manquants

```
Observation:
- L'ATEM envoyait des milliers de paquets avec flag RETX (0x20)
- Les séquences revenaient en arrière (1, 2, 3, ... 1, 2, 3, ...)

Cause:
- Aucun ACK n'était envoyé pendant la phase initiale
- L'ATEM retransmettait indéfiniment

Solution:
- Envoyer un ACK pour CHAQUE paquet RELIABLE
```

### Découverte #2 : Session ID

```
Observation:
- Notre Session ID: 0x53AB
- Session ID dans les paquets ATEM: 0xDC77 (différent!)

Cause:
- L'ATEM peut proposer son propre Session ID
- Nous continuions à utiliser le nôtre

Solution:
- Capturer le Session ID dès le premier paquet reçu
- L'utiliser pour tous les paquets suivants
```

### Découverte #3 : Format CPvI

```
Observation:
- Commande CPvI avec mask byte (0x01): ACK reçu, mais Preview inchangée
- Commande CPvI sans mask byte: SUCCÈS!

Cause:
- Le format documenté avec mask byte ne fonctionne pas
- Le format correct est [ME, 0x00, source_hi, source_lo]

Solution:
- Utiliser le format sans mask byte
```

---

## Référence des commandes

### Commandes d'envoi (Client → ATEM)

| Commande | Description | Payload |
|----------|-------------|---------|
| `CPvI` | Change Preview Input | `[ME, 0x00, src_hi, src_lo]` |
| `CPgI` | Change Program Input | `[ME, 0x00, src_hi, src_lo]` |
| `DAut` | Do Auto Transition | `[ME, 0x00, 0x00, 0x00]` |
| `DCut` | Do Cut | `[ME, 0x00, 0x00, 0x00]` |

### Commandes de réception (ATEM → Client)

| Commande | Description | Payload |
|----------|-------------|---------|
| `PrgI` | Program Input | `[ME, ??, src_hi, src_lo]` |
| `PrvI` | Preview Input | `[ME, ??, src_hi, src_lo, ...]` |
| `InCm` | Init Complete | Marqueur de fin d'initialisation |
| `TlIn` | Tally Input | État tally des sources |

### Sources courantes

| Valeur | Source |
|--------|--------|
| 1-8 | Inputs 1-8 |
| 1000 | Color Bars |
| 2001 | Color 1 |
| 2002 | Color 2 |
| 3010 | Media Player 1 |
| 3020 | Media Player 2 |
| 6000 | Super Source |
| 10010 | ME 1 Program |
| 10011 | ME 1 Preview |

---

## Ressources

- [SKAARHOJ ATEM Protocol](https://www.skaarhoj.com/discover/blackmagic-atem-switcher-protocol) - Documentation communautaire
- [PyATEMMax](https://github.com/clvLabs/PyATEMMax) - Implémentation Python de référence
- [Wireshark](https://www.wireshark.org/) - Capture de paquets réseau
