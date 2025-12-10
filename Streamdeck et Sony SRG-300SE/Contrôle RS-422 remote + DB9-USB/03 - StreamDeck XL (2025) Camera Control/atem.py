## atem.py
"""
Interface ATEM - Wrapper compatible PyATEMMax
Utilise ATEMClient en interne mais expose la même interface que PyATEMMax
pour que les autres fichiers (tally.py, sequences.py) fonctionnent sans modification.

Ajout : Gestion du style de transition (MIX/WIPE/DIP/DVE/STING)
"""
from atem_client import ATEMClient, TRANSITION_MIX, TRANSITION_DIP, TRANSITION_WIPE, TRANSITION_DVE, TRANSITION_STING, TRANSITION_NAMES


class VideoSourceProperty:
    """Émule l'accès à videoSource comme PyATEMMax"""
    def __init__(self, get_func):
        self._get_func = get_func
    
    @property
    def videoSource(self):
        value = self._get_func()
        # Retourner au format "inputX" comme PyATEMMax
        if value is not None:
            return f"input{value}"
        return None


class InputAccessor:
    """Émule l'accès par index [0] comme PyATEMMax"""
    def __init__(self, get_func):
        self._get_func = get_func
        self._cache = {}
    
    def __getitem__(self, index):
        if index not in self._cache:
            self._cache[index] = VideoSourceProperty(lambda i=index: self._get_func(i))
        return self._cache[index]


class ATEMWrapper:
    """
    Wrapper qui émule l'interface PyATEMMax.ATEMMax()
    
    Propriétés émulées:
        - switcher.connected
        - switcher.programInput[me].videoSource
        - switcher.previewInput[me].videoSource
    
    Méthodes émulées:
        - switcher.connect(ip)
        - switcher.waitForConnection()
        - switcher.setPreviewInputVideoSource(me, source)
        - switcher.setProgramInputVideoSource(me, source)
        - switcher.execAutoME(me)
        - switcher.execCutME(me)
    
    Méthodes ajoutées pour le style de transition:
        - switcher.setTransitionStyle(me, style)
        - switcher.getTransitionStyle(me)
        - switcher.ensureMixTransition(me)
    """
    
    def __init__(self):
        self._client = None
        self._ip = None
        self.connected = False
        
        # Créer les accessors pour programInput et previewInput
        self.programInput = InputAccessor(self._get_program)
        self.previewInput = InputAccessor(self._get_preview)
    
    def _get_program(self, me=0):
        if self._client:
            return self._client.get_program(me)
        return None
    
    def _get_preview(self, me=0):
        if self._client:
            return self._client.get_preview(me)
        return None
    
    def connect(self, ip):
        """Connecter à l'ATEM (comme PyATEMMax)"""
        self._ip = ip
        self._client = ATEMClient(ip)
    
    def waitForConnection(self, timeout=10):
        """Attendre la connexion (comme PyATEMMax)"""
        if self._client:
            self.connected = self._client.connect(timeout=timeout)
        return self.connected
    
    def setPreviewInputVideoSource(self, me, source):
        """Changer la source Preview (comme PyATEMMax)
        
        Args:
            me: Index du M/E (0 = ME1)
            source: Peut être un int ou une string "inputX"
        """
        if self._client:
            # Convertir "inputX" en int si nécessaire
            if isinstance(source, str) and source.startswith("input"):
                source = int(source.replace("input", ""))
            self._client.set_preview_input(me, source)
    
    def setProgramInputVideoSource(self, me, source):
        """Changer la source Program (comme PyATEMMax)"""
        if self._client:
            if isinstance(source, str) and source.startswith("input"):
                source = int(source.replace("input", ""))
            self._client.set_program_input(me, source)
    
    def execAutoME(self, me=0):
        """Exécuter une transition AUTO (comme PyATEMMax)"""
        if self._client:
            self._client.do_auto(me)
    
    def execCutME(self, me=0):
        """Exécuter un CUT (comme PyATEMMax)"""
        if self._client:
            self._client.do_cut(me)
    
    # === Nouvelles méthodes pour le style de transition ===
    
    def setTransitionStyle(self, me, style):
        """Définir le style de transition
        
        Args:
            me: Index du M/E (0 = ME1)
            style: 0=MIX, 1=DIP, 2=WIPE, 3=DVE, 4=STING
                   ou string: "mix", "dip", "wipe", "dve", "sting"
        
        Returns:
            True si la commande a été envoyée
        """
        if self._client:
            # Convertir string en int si nécessaire
            if isinstance(style, str):
                style_map = {
                    "mix": TRANSITION_MIX,
                    "dip": TRANSITION_DIP,
                    "wipe": TRANSITION_WIPE,
                    "dve": TRANSITION_DVE,
                    "sting": TRANSITION_STING
                }
                style = style_map.get(style.lower(), TRANSITION_MIX)
            
            return self._client.set_transition_style(me, style)
        return False
    
    def getTransitionStyle(self, me=0):
        """Obtenir le style de transition actuel
        
        Args:
            me: Index du M/E (0 = ME1)
        
        Returns:
            Style (0=MIX, 1=DIP, 2=WIPE, 3=DVE, 4=STING) ou None
        """
        if self._client:
            return self._client.get_transition_style(me)
        return None
    
    def getTransitionStyleName(self, me=0):
        """Obtenir le nom du style de transition actuel
        
        Args:
            me: Index du M/E (0 = ME1)
        
        Returns:
            Nom du style ("MIX", "WIPE", etc.) ou "Unknown"
        """
        style = self.getTransitionStyle(me)
        if style is not None:
            return TRANSITION_NAMES.get(style, f"Unknown({style})")
        return "Unknown"
    
    def ensureMixTransition(self, me=0):
        """S'assurer que le style de transition est MIX
        
        Vérifie le style actuel et le change en MIX si nécessaire.
        
        Args:
            me: Index du M/E (0 = ME1)
        
        Returns:
            True si déjà en MIX ou si la commande a été envoyée
        """
        if self._client:
            return self._client.ensure_mix_transition(me)
        return False


# Instance globale (comme avec PyATEMMax)
switcher = ATEMWrapper()

# Constantes exportées pour le style de transition
STYLE_MIX = TRANSITION_MIX
STYLE_DIP = TRANSITION_DIP
STYLE_WIPE = TRANSITION_WIPE
STYLE_DVE = TRANSITION_DVE
STYLE_STING = TRANSITION_STING

# Callbacks pour le tally
_tally_callbacks = []
_monitor_thread = None
_running = False


def connect_to_atem():
    """Fonction de connexion avec phase d'initialisation"""
    global _running, _monitor_thread
    
    switcher.connect('172.18.29.12')
    switcher.waitForConnection()

    if not switcher.connected:
        print("Erreur de connexion à l'ATEM")
        exit()
    else:
        print("Connecté à l'ATEM... OK")
        
        # ============================================
        # PHASE D'INITIALISATION
        # ============================================
        print("\n" + "=" * 50)
        print("📋 Phase d'initialisation ATEM")
        print("=" * 50)
        
        _init_transition_style()
        # Ajouter ici d'autres initialisations futures :
        # _init_xxx()
        # _init_yyy()
        
        print("=" * 50)
        print("✅ Initialisation terminée")
        print("=" * 50 + "\n")
        
        # Démarrer le monitoring des changements de tally
        import threading
        _running = True
        _monitor_thread = threading.Thread(target=_monitor_tally, daemon=True)
        _monitor_thread.start()


def _init_transition_style():
    """
    Initialisation du style de transition.
    Force le mode MIX sur ME0 si nécessaire.
    """
    import time
    
    # Petite pause pour s'assurer que tous les états ont été reçus
    time.sleep(0.3)
    
    style = switcher.getTransitionStyle(0)
    style_name = switcher.getTransitionStyleName(0)
    
    print(f"  Style de transition ME0: {style_name}")
    
    if style is None:
        print("  ⚠️ Style non reçu, forçage MIX par précaution")
        switcher.setTransitionStyle(0, STYLE_MIX)
        time.sleep(0.2)
    elif style != STYLE_MIX:
        print(f"  → Passage de {style_name} à MIX")
        switcher.setTransitionStyle(0, STYLE_MIX)
        time.sleep(0.2)
        # Vérifier que le changement a été pris en compte
        new_style_name = switcher.getTransitionStyleName(0)
        print(f"  ✓ Style maintenant: {new_style_name}")
    else:
        print("  ✓ Déjà en MIX, aucun changement nécessaire")


def register_tally_callback(callback):
    """Enregistrer un callback appelé lors des changements Program/Preview"""
    if callback not in _tally_callbacks:
        _tally_callbacks.append(callback)


def _monitor_tally():
    """Thread qui surveille les changements de Program/Preview"""
    import time
    last_program = None
    last_preview = None
    
    while _running:
        if switcher.connected:
            program = switcher._get_program(0)
            preview = switcher._get_preview(0)
            
            if program != last_program or preview != last_preview:
                last_program = program
                last_preview = preview
                
                # Appeler tous les callbacks
                for callback in _tally_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Erreur callback tally: {e}")
        
        time.sleep(0.1)
