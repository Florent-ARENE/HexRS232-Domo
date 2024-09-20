import socket

def send_command(ip, send_port, recv_port, command):
    udpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpClient.settimeout(5)
    
    # Associer le socket au port de réception
    udpClient.bind(('', recv_port))
    
    udpClient.sendto(command, (ip, send_port))
    
    responses = []
    
    try:
        while True:
            data, _ = udpClient.recvfrom(1024)
            responses.append(data)
    except socket.timeout:
        # Fin de l'écoute après expiration du délai
        pass
    finally:
        udpClient.close()
    
    return responses

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string.replace(" ", ""))

# Adresse IP et port de la caméra
ip = "172.18.29.1"
send_port = 52381
recv_port = 52381

# Commande à envoyer pour écouter les réponses multiples
command = "02 00 00 01 00 00 00 00 01"

# Convertir la commande en bytes
command_bytes = hex_to_bytes(command)

# Envoyer la commande et capturer les réponses multiples
print(f"Envoi de la commande : {command}")
responses = send_command(ip, send_port, recv_port, command_bytes)

if responses:
    print("Réponses reçues :")
    for i, response in enumerate(responses):
        print(f"Réponse {i+1} : {response.hex()}")
else:
    print("Aucune réponse de la caméra")
