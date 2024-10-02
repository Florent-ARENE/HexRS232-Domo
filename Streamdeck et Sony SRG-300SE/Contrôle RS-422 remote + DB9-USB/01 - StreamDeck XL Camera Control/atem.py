# atem.py
import PyATEMMax

# Connexion à l'ATEM
switcher = PyATEMMax.ATEMMax()
switcher.connect('172.18.29.12')
switcher.waitForConnection()

# Vérification de connexion
if not switcher.connected:
    print("Erreur de connexion à l'ATEM")
    exit()
else:
    print("Connecté à l'ATEM")
