## atem.py
import PyATEMMax

switcher = PyATEMMax.ATEMMax()

def connect_to_atem():
    switcher.connect('172.18.29.12')
    switcher.waitForConnection()

    if not switcher.connected:
        print("Erreur de connexion à l'ATEM")
        exit()
    else:
        print("Connecté à l'ATEM... OK")
