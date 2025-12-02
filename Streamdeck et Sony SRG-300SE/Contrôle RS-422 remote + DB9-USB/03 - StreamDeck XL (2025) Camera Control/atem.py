## atem.py
"""
Interface ATEM - Wrapper compatible PyATEMMax
Utilise ATEMClient en interne mais expose la même interface que PyATEMMax
pour que les autres fichiers (tally.py, sequences.py) fonctionnent sans modification.
"""
from atem_client import ATEMClient


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


# Instance globale (comme avec PyATEMMax)
switcher = ATEMWrapper()

# Callbacks pour le tally
_tally_callbacks = []
_monitor_thread = None
_running = False


def connect_to_atem():
    """Fonction de connexion (identique à l'original)"""
    global _running, _monitor_thread
    
    switcher.connect('172.18.29.12')
    switcher.waitForConnection()

    if not switcher.connected:
        print("Erreur de connexion à l'ATEM")
        exit()
    else:
        print("Connecté à l'ATEM... OK")
        
        # Démarrer le monitoring des changements de tally
        import threading
        _running = True
        _monitor_thread = threading.Thread(target=_monitor_tally, daemon=True)
        _monitor_thread.start()


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
