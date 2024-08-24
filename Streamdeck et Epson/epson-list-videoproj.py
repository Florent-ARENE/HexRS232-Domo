import socket
import re
import time
import netifaces
from concurrent.futures import ThreadPoolExecutor

# Fonction pour lister les interfaces réseau avec leurs adresses IP
def list_network_interfaces():
    interfaces = netifaces.interfaces()
    ip_addresses = {}

    for iface in interfaces:
        addresses = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addresses:
            ipv4_info = addresses[netifaces.AF_INET][0]
            ip_addresses[iface] = ipv4_info['addr']

    return ip_addresses

# Fonction pour récupérer l'état du projecteur et son nom (si possible)
def get_projector_info(projector_ip):
    try:
        port = 4352
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)  # Réduction du timeout pour accélérer les tests
        sock.connect((projector_ip, port))

        # Lire la première réponse PJLink 0
        initial_response = sock.recv(1024).decode('ascii')
        print(f"Réponse initiale du projecteur {projector_ip} :", initial_response)

        # Envoyer la commande PJLink pour obtenir l'état du projecteur
        command = "%1POWR ?\r"
        sock.send(command.encode('ascii'))

        # Lire la réponse du projecteur
        status_response = sock.recv(1024).decode('ascii')

        # Envoyer la commande PJLink pour obtenir le nom du projecteur
        command_name = "%1NAME ?\r"
        sock.send(command_name.encode('ascii'))
        name_response = sock.recv(1024).decode('ascii')

        # Fermer la connexion
        sock.close()

        return status_response, name_response
    except Exception as e:
        print(f"Erreur lors de la connexion à {projector_ip}: {e}")
        return None, None

# Fonction pour envoyer la commande de mise sous tension ou hors tension
def send_power_command(projector_ip, state):
    try:
        time.sleep(1)  # Attendre 1 seconde
        port = 4352
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((projector_ip, port))

        if state == "on":
            command = "%1POWR 1\r"
        elif state == "off":
            command = "%1POWR 0\r"
        sock.send(command.encode('ascii'))

        response = sock.recv(1024).decode('ascii')
        print(f"Réponse du projecteur {projector_ip} :", response)

        sock.close()
    except Exception as e:
        print(f"Erreur lors de l'envoi de la commande à {projector_ip}: {e}")

# Fonction pour scanner une adresse IP
def scan_ip(ip, projectors):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)  # Timeout plus court pour accélérer le scan
        sock.connect((ip, 4352))
        response = sock.recv(1024).decode('ascii')
        if "PJLINK" in response:
            print(f"Dispositif PJLink trouvé à {ip}. Tentative de récupération d'information...")
            status_response, name_response = get_projector_info(ip)
            if status_response:
                state = "allumé" if "POWR=1" in status_response else "éteint"
                # Extraction du nom du projecteur
                projector_name = re.search(r"NAME=(.*)\r", name_response)
                projector_name = projector_name.group(1) if projector_name else "Inconnu"
                projectors.append((ip, projector_name, state))
            else:
                print(f"Connexion PJLink échouée pour {ip}.")
        sock.close()
    except Exception as e:
        print(f"Impossible de se connecter à {ip}: {e}")

# Fonction principale
def main():
    # Lister les interfaces réseau et leurs adresses IP
    ip_addresses = list_network_interfaces()

    if not ip_addresses:
        print("Aucune interface réseau détectée.")
        return

    print("Interfaces réseau détectées :")
    for idx, (iface, ip) in enumerate(ip_addresses.items(), start=1):
        print(f"{idx}. {iface} - {ip}")

    # Demander à l'utilisateur de choisir une interface
    choice = int(input("\nChoisissez une interface réseau à utiliser : ")) - 1
    selected_iface = list(ip_addresses.keys())[choice]
    local_ip = ip_addresses[selected_iface]

    # Déterminer le sous-réseau
    subnet = '.'.join(local_ip.split('.')[:-1]) + '.'

    projectors = []
    
    print(f"Scan du sous-réseau {subnet}0/24 en cours...")

    # Utilisation de ThreadPoolExecutor pour le scan en parallèle
    with ThreadPoolExecutor(max_workers=50) as executor:
        for i in range(0, 255):
            ip = subnet + str(i)
            executor.submit(scan_ip, ip, projectors)

    # Afficher les projecteurs détectés
    if projectors:
        print("\nProjecteurs détectés :")
        for idx, (ip, name, state) in enumerate(projectors):
            print(f"{idx + 1}. {name} ({ip}) - État: {state}")

        # Demander à l'utilisateur de choisir un projecteur
        choice = int(input("\nChoisissez un numéro de projecteur pour changer son état : ")) - 1
        if 0 <= choice < len(projectors):
            selected_projector = projectors[choice]
            new_state = "off" if selected_projector[2] == "allumé" else "on"
            send_power_command(selected_projector[0], new_state)
        else:
            print("Numéro de projecteur invalide.")
    else:
        print("Aucun projecteur détecté.")

if __name__ == "__main__":
    main()
