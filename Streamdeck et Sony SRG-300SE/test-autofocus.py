import socket

def send_command(ip, send_port, recv_port, command):
    udpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpClient.settimeout(5)
    
    # Associer le socket au port de réception
    udpClient.bind(('', recv_port))
    
    udpClient.sendto(command, (ip, send_port))
    try:
        data, _ = udpClient.recvfrom(1024)
        return data
    except socket.timeout:
        return None
    finally:
        udpClient.close()

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string.replace(" ", ""))

# Adresse IP et port de la caméra
ip = "172.18.29.1"
send_port = 52381
recv_port = 52381

# Commande pour interroger l'état de l'autofocus
command = "81 09 04 38 FF"

# Initialisation du compteur avec la séquence de forçage
count = "FF FF FF FF"

def update_counter(current_count):
    if current_count == "FF FF FF FF":
        return "00 00 00 00"
    else:
        return f"{int(current_count.replace(' ', ''), 16) + 1:08X}".rjust(8, '0')

# Envoi initial avec la séquence de forçage
prefix = f"01 00 00 05 {count}"
full_command = prefix.replace(" ", "") + command.replace(" ", "")
full_command_bytes = hex_to_bytes(full_command)

print(f"Envoi de la commande : {full_command}")
response = send_command(ip, send_port, recv_port, full_command_bytes)

if response:
    print(f"Réponse reçue : {response.hex()}")
    # Vérifier si la réponse commence par 02 (indiquant une commande acceptée)
    if response.hex().startswith("02"):
        # Incrémenter le compteur
        count = update_counter(count)
        # Envoi de la commande avec le compteur mis à jour
        prefix = f"01 00 00 05 {count}"
        full_command = prefix.replace(" ", "") + command.replace(" ", "")
        full_command_bytes = hex_to_bytes(full_command)

        print(f"Envoi de la commande avec compteur incrémenté : {full_command}")
        response = send_command(ip, send_port, recv_port, full_command_bytes)

        if response:
            print(f"Réponse reçue après incrémentation : {response.hex()}")
        else:
            print("Aucune réponse après l'incrémentation")
    elif response.hex().startswith("01"):
        print("La commande a été acceptée sans nécessité d'incrémentation.")
    else:
        print("La commande n'a pas été acceptée ou autre problème.")
else:
    print("Aucune réponse de la caméra")
