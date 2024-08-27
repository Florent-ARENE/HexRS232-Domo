import websocket
import ssl
import json
import os

def create_connection(host, port, token=None, secure=False):
    protocol = "wss" if secure else "ws"
    if token:
        url = f"{protocol}://{host}:{port}/api/v2/channels/samsung.remote.control?name=RmxvUmVtb3RlU2Ftc3VuZw==&token={token}"
    else:
        url = f"{protocol}://{host}:{port}/api/v2/channels/samsung.remote.control?name=RmxvUmVtb3RlU2Ftc3VuZw=="
    
    print(f"Tentative de connexion à {url}...")

    try:
        if secure:
            ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            ws = websocket.create_connection(url)
        
        print(f"Connexion réussie avec {protocol} sur le port {port}")
        return ws
    except Exception as e:
        print(f"Échec de la connexion à {protocol} sur le port {port} : {e}")
        return None

def get_token(ws):
    try:
        response = ws.recv()
        response_data = json.loads(response)
        if "token" in response_data.get("data", {}):
            token = response_data["data"]["token"]
            print(f"Token reçu : {token}")
            return token
        else:
            print("Aucun token trouvé dans la réponse.")
            return None
    except Exception as e:
        print(f"Erreur lors de la réception du token : {e}")
        return None

def send_command(ws, command):
    payload = {
        "method": "ms.remote.control",
        "params": {
            "Cmd": "Click",
            "DataOfCmd": command,
            "Option": "false",
            "TypeOfRemote": "SendRemoteKey"
        }
    }

    ws.send(json.dumps(payload))
    try:
        result = ws.recv()
        print(f"Réponse reçue pour {command} : {result}")
    except Exception as e:
        print(f"Erreur lors de la réception de la réponse pour {command} : {e}")

def main():
    host = '192.168.100.10'
    token_file = 'token.txt'
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as file:
            token = file.read().strip()
        print(f"Token chargé depuis le fichier : {token}")
    else:
        token = None

    # Étape 1 : Si aucun token n'est trouvé, obtenez-le
    if not token:
        ws = create_connection(host, 8002, secure=True)
        if not ws:
            ws = create_connection(host, 8001, secure=False)
        
        if ws:
            token = get_token(ws)
            if token:
                with open(token_file, 'w') as file:
                    file.write(token)
                print(f"Token sauvegardé dans {token_file}.")
            ws.close()
        else:
            print("Impossible de se connecter au téléviseur pour obtenir le token.")
            return

    # Étape 2 : Utilisation du token pour envoyer des commandes
    if token:
        ws = create_connection(host, 8002, token, secure=True)
        if not ws:
            ws = create_connection(host, 8001, token, secure=False)
        
        if ws:
            try:
                command = input("Entrez la commande KEY_ à envoyer (par exemple, KEY_POWER) : ").strip()
                send_command(ws, command)
            finally:
                ws.close()
                print("Connexion fermée.")
        else:
            print("Impossible de se reconnecter au téléviseur avec le token.")
    else:
        print("Token non reçu, impossible de continuer.")

if __name__ == "__main__":
    main()