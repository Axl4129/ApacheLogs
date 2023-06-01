import urllib.request
import re
import json
from datetime import datetime


# Fonction pour récupérer le contenu du fichier de log depuis l'URL
def get_log_file(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8') 
    return text

# Fonction pour analyser les logs
def analyze_log(log_text):
    connections = {}
    browsers = {}
    first_request = {}
    last_request = {}

    lines = log_text.split('\n')
    for line in lines:
        # Utiliser une expression régulière pour extraire l'adresse IP, le code de retour et le navigateur
        match = re.search(r'(\d+\.\d+\.\d+\.\d+).*\[(.*)\] "([A-Z]+) .*" (\d+) .* "(.*)"', line)
        if match:
            ip = match.group(1)
            timestamp = datetime.strptime(match.group(2), "%d/%b/%Y:%H:%M:%S %z")
            method = match.group(3)
            status_code = match.group(4)
            browser = match.group(5)

            # Compter le code de retour pour chaque adresse IP
            if ip in connections:
                connections[ip].append(status_code)
            else:
                connections[ip] = [status_code]

            # Enregistrer le navigateur pour chaque adresse IP
            if ip in browsers:
                browsers[ip].add(browser)
            else:
                browsers[ip] = {browser}

            # Mettre à jour la date de la première requête pour chaque adresse IP
            if ip not in first_request:
                first_request[ip] = timestamp
            else:
                if timestamp < first_request[ip]:
                    first_request[ip] = timestamp

            # Mettre à jour la date de la dernière requête pour chaque adresse IP
            if ip not in last_request:
                last_request[ip] = timestamp
            else:
                if timestamp > last_request[ip]:
                    last_request[ip] = timestamp

    return connections, browsers, first_request, last_request

# URL du fichier de log
log_url = 'https://cdn.antho.cefim.o2switch.site/access.log'

# Récupérer le contenu du fichier de log depuis l'URL
log_text = get_log_file(log_url)


# Analyser les logs
connections, browsers, first_request, last_request = analyze_log(log_text)

# Construire le dictionnaire final avec les résultats
results = {}
for ip, codes in connections.items():
    # Compter les codes de retour pour chaque adresse IP
    counts = {}
    for code in codes:
        if code in counts:
            counts[code] += 1
        else:
            counts[code] = 1

    # Obtenir le nombre total de requêtes pour chaque adresse IP
    total_requests = sum(counts.values())

    # Obtenir la liste des navigateurs utilisés pour chaque adresse IP
    browser_list = list(browsers[ip])

    # Obtenir les dates de la première et de la dernière requête pour chaque adresse IP
    first_request_date = first_request[ip].strftime("%Y-%m-%d %H:%M:%S")
    last_request_date = last_request[ip].strftime("%Y-%m-%d %H:%M:%S")

    # Construire l'objet final pour chaque adresse IP
    results[ip] = {
        'total_requests': total_requests,
        'status_codes': counts,
        'first_request': first_request_date,
        'last_request': last_request_date,
        'browsers': browser_list
    }

# Enregistrer les résultats dans un fichier JSON
with open('results.json', 'w') as json_file:
    json.dump(results, json_file, indent=4)