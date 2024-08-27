import requests
import json

def get_tv_info(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Vérifie si la requête a échoué
        tv_info = response.json()
        return tv_info
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des informations de l'API : {e}")
        return None

def display_tv_info(tv_info):
    if tv_info:
        print("Informations récupérées depuis l'API :")
        print(json.dumps(tv_info, indent=4))  # Affiche le JSON formaté pour une lecture facile
    else:
        print("Impossible de récupérer les informations du téléviseur.")

def display_power_state(tv_info):
    if tv_info and 'device' in tv_info and 'PowerState' in tv_info['device']:
        power_state = tv_info['device']['PowerState']
        print(f"\nL'état d'alimentation de l'écran est : {power_state}")
    else:
        print("Impossible de récupérer l'état d'alimentation.")

def main():
    api_url = 'http://192.168.100.10:8001/api/v2/'
    tv_info = get_tv_info(api_url)
    display_tv_info(tv_info)
    display_power_state(tv_info)

if __name__ == "__main__":
    main()
